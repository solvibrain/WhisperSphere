from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _

from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from .utils import validate_name

import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def index(request):
    q = request.GET.get('q', '')
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ).select_related('topic', 'host').prefetch_related('participants')
    
    topics = Topic.objects.all()[:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q) |
        Q(room__name__icontains=q) |
        Q(body__icontains=q)
    ).select_related('user', 'room')

    paginator = Paginator(rooms, 10)  # Show 10 rooms per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'rooms': page_obj,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages
    }
    return render(request, 'base/index.html', context)

@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        email = request.POST.get('email', '').lower()
        password = request.POST.get('password', '')

        try:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user,backend= auth_backend)
                return redirect('index')
            else:
                messages.error(request, _("Invalid email or password"))
        except User.DoesNotExist:
            messages.error(request, _("User does not exist"))
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            messages.error(request, _("An error occurred. Please try again."))

    return render(request, 'base/login_page.html', {'page': 'login'})

@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('index')

@require_http_methods(["GET", "POST"])
def register_user(request):
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.username = user.username.lower()
                    user.save()
                    auth_backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user,backend= auth_backend)
                return redirect('index')
            except Exception as e:
                logger.error(f"User registration error: {str(e)}")
                messages.error(request, _("An error occurred during registration. Please try again."))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    return render(request, 'base/login_page.html', {'form': form})

@require_http_methods(["GET"])
def user_profile(request, pk):
    user = get_object_or_404(User, id=pk)
    rooms = user.rooms.all()
    room_messages = user.messages.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'topics': topics,
        'room_messages': room_messages
    }
    return render(request, 'base/userProfile.html', context)

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def update_user(request, pk):
    # Get the user profile to be updated
    profile_user = get_object_or_404(User, pk=pk)
    
    # Check if the logged-in user is the same as the profile user
    if request.user.id != profile_user.id:
        return HttpResponseForbidden("You don't have permission to update this profile.")
    
    form = UserForm(instance=profile_user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=profile_user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=profile_user.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    
    return render(request, 'base/update-user.html', {'form': form})
@require_http_methods(["GET", "POST"])
def room(request, pk):
    room = get_object_or_404(Room, id=pk)
    room_messages = room.room_messages.all().select_related('user')
    participants = room.participants.all()

    if request.method == 'POST':
        if request.user.is_authenticated:
            Message.objects.create(
                user=request.user,
                room=room,
                body=request.POST.get('message_body')
            )
            room.participants.add(request.user)
            return redirect('room', pk=room.id)
        else:
            return redirect('login')

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants
    }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        room_name = request.POST.get('name')

        is_valid, error_message = validate_name(topic_name)
        if not is_valid:
            messages.error(request, f"Invalid topic name: {error_message}")
            return redirect('create-room')

        is_valid, error_message = validate_name(room_name, check_profanity=False)
        if not is_valid:
            messages.error(request, f"Invalid room name: {error_message}")
            return redirect('create-room')

        if Room.objects.filter(name=room_name).exists():
            messages.error(request, _("A room with this name already exists."))
            return redirect('create-room')

        try:
            with transaction.atomic():
                topic, _ = Topic.objects.get_or_create(name=topic_name)
                room = Room.objects.create(
                    host=request.user,
                    topic=topic,
                    name=room_name,
                    description=request.POST.get('description')
                )
            return redirect('room', pk=room.id)
        except IntegrityError:
            messages.error(request, _("An error occurred while creating the room. Please try again."))
            logger.error(f"Room creation error for user {request.user.id}")

    context = {'form': form, 'topics': topics, 'page': 'create'}
    return render(request, 'base/create_room.html', context)

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def update_room(request, pk):
    room = get_object_or_404(Room, id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponseForbidden(_("You are not allowed to update this room."))

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        room_name = request.POST.get('name')

        is_valid, error_message = validate_name(topic_name)
        if not is_valid:
            messages.error(request, f"Invalid topic name: {error_message}")
            return redirect('update-room', pk=pk)

        is_valid, error_message = validate_name(room_name, check_profanity=False)
        if not is_valid:
            messages.error(request, f"Invalid room name: {error_message}")
            return redirect('update-room', pk=pk)

        try:
            with transaction.atomic():
                topic, _ = Topic.objects.get_or_create(name=topic_name)
                room.name = room_name
                room.description = request.POST.get('description')
                room.topic = topic
                room.save()
            return redirect('room', pk=room.id)
        except IntegrityError:
            messages.error(request, _("An error occurred while updating the room. Please try again."))
            logger.error(f"Room update error for room {pk} by user {request.user.id}")

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/create_room.html', context)

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def delete_room(request, pk):
    room = get_object_or_404(Room, id=pk)

    if request.user != room.host:
        return HttpResponseForbidden(_("You are not allowed to delete this room."))

    if request.method == "POST":
        room.delete()
        return redirect('index')

    return render(request, 'base/deleteRoom.html', {'obj': room})

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def delete_message(request, pk):
    message = get_object_or_404(Message, id=pk)

    if request.user != message.user:
        return HttpResponseForbidden(_("You are not allowed to delete this message."))

    if request.method == "POST":
        message.delete()
        return redirect('index')

    return render(request, 'base/deleteRoom.html', {'obj': message})

@require_http_methods(["GET"])
def back(request):
    previous_page = request.META.get('HTTP_REFERER')
    return redirect(previous_page) if previous_page else redirect('index')

@login_required(login_url='login')
@require_http_methods(["GET"])
def setting(request):
    return render(request, 'base/settings.html')

@login_required(login_url='login')
@require_http_methods(["GET"])
def activity_page(request):
    q = request.GET.get('q', '')
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q) |
        Q(room__name__icontains=q)
    ).select_related('user', 'room')
    return render(request, 'base/activity_mobile.html', {'room_messages': room_messages})

@require_http_methods(["GET"])
def topic_page(request):
    q = request.GET.get('q', '')
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics_mobile.html', {'topics': topics})