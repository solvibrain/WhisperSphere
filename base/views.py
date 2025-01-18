# Import necessary modules
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .models import Room, Topic, Message, UserProfile, Badge, Event, Notification
from .forms import RoomForm, UserForm
from django.utils import timezone


#Generating Custom Google URL
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.models import SocialApp
from django.urls import reverse

def custom_google_login(request):
    # Get the Google provider configuration
    google_provider = GoogleProvider(request)
    app = SocialApp.objects.get_current(provider='google')
    
    # Build the Google OAuth URL directly
    authorize_url = google_provider.get_oauth_url(request)
    
    # Redirect directly to Google's auth page
    return redirect(authorize_url)




def index(request):
    """
    View for the home page.
    Displays rooms, topics, and personalized recommendations.
    """
    # Get search query from GET parameters
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    # Filter rooms based on search query
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    # Get top 5 topics by room count
    topics = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')[:5]
    room_count = rooms.count()

    # Filter messages based on search query
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q) |
        Q(room__name__icontains=q)
    )

    # Personalized room recommendations
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
            user_profile = UserProfile.objects.create(user=request.user)
        user_interests = user_profile.interests.all()
        recommended_rooms = Room.objects.filter(topic__in=user_interests).exclude(participants=request.user)[:5]
    else:
        # For non-authenticated users, show popular rooms
        recommended_rooms = Room.objects.annotate(participant_count=Count('participants')).order_by('-participant_count')[:5]

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
        'recommended_rooms': recommended_rooms,
    }
    return render(request, 'base/index.html', context)

def back(request):
    previous_page = request.META.get('HTTP_REFERER')
    if previous_page:
        return redirect(previous_page)
    else:
        # If there is no previous page, redirect to a default URL
        return redirect('index')  

@login_required(login_url='login')
def setting(request):
   return render(request,'base/settings.html')

@login_required(login_url='login')
def room(request, pk):
    """
    View for a specific room.
    Handles message creation, user participation, and notifications.
    """
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        # Create a new message
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('message_body')
        )
        room.participants.add(request.user)

        # Award points for participation
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.points += 5
        user_profile.save()

        # Check for level up
        if user_profile.points >= user_profile.level * 100:
            user_profile.level += 1
            user_profile.save()
            messages.success(request, f"Congratulations! You've reached level {user_profile.level}!")

        # Create notifications for mentions
        mentioned_users = [user for user in User.objects.all() if user.username in message.body]
        for mentioned_user in mentioned_users:
            Notification.objects.create(
                recipient=mentioned_user,
                notification_type='mention',
                actor=request.user,
                target=message
            )

        return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants
    }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    """
    View for creating a new room.
    Handles room creation and awards points to the user.
    """
    page = 'create'
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        # Award points for creating a room
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.points += 20
        user_profile.save()

        return redirect('index')

    context = {'form': form, 'topics': topics, 'page': page}
    return render(request, 'base/create_room.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    """
    View for updating an existing room.
    Only allows the room host to make changes.
    """
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed to do this because you are not the host of this room")

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('index')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/create_room.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    """
    View for deleting a room.
    Only allows the room host to delete the room.
    """
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed to do this because you are not the host of this room")

    if request.method == "POST":
        room.delete()
        return redirect('index')
    return render(request, 'base/deleteRoom.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    """
    View for deleting a message.
    Only allows the message author to delete the message.
    """
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed to delete others' messages")

    if request.method == "POST":
        message.delete()
        return redirect('room', pk=message.room.id)
    return render(request, 'base/deleteRoom.html', {'obj': message})

@login_required(login_url='login')
def upvoteMessage(request, pk):
    """
    View for upvoting a message.
    Handles upvote toggling, point awarding, and notification creation.
    """
    message = Message.objects.get(id=pk)
    user_profile = UserProfile.objects.get(user=request.user)

    if request.user not in message.upvotes.all():
        message.upvotes.add(request.user)
        # Award points for receiving an upvote
        message_user_profile = UserProfile.objects.get(user=message.user)
        message_user_profile.points += 2
        message_user_profile.save()

        # Create notification for upvote
        Notification.objects.create(
            recipient=message.user,
            notification_type='upvote',
            actor=request.user,
            target=message
        )
    else:
        message.upvotes.remove(request.user)

    return redirect('room', pk=message.room.id)

def loginPage(request):
    """
    View for user login.
    Handles authentication and redirects.
    """
    page = 'login'
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Username and Password do not match")

    context = {'page': page}
    return render(request, 'base/login_page.html', context)

def logoutUser(request):
    """
    View for user logout.
    Logs out the user and redirects to the home page.
    """
    logout(request)
    return redirect('index')

def registerUser(request):
    """
    View for user registration.
    Creates a new user account and associated UserProfile.
    """
    form = UserCreationForm()
    context = {'form': form}

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'An error occurred during registration.')

    return render(request, 'base/login_page.html', context)

def userProfile(request, pk):
    """
    View for displaying user profile.
    Shows user's rooms, messages, topics, and badges.
    """
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    user_profile = UserProfile.objects.get(user=user)
    badges = user.badges.all()

    context = {
        'user': user,
        'rooms': rooms,
        'topics': topics,
        'room_messages': room_messages,
        'user_profile': user_profile,
        'badges': badges
    }
    return render(request, 'base/userProfile.html', context)

@login_required(login_url='login')
def updateUser(request):
    """
    View for updating user profile.
    Allows users to modify their profile information.
    """
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html', context)

@login_required(login_url='login')
def activityPage(request):
    """
    View for displaying recent activity.
    Shows recent messages filtered by search query.
    """
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q) |
        Q(room__name__icontains=q)
    )
    context = {'room_messages': room_messages}
    return render(request, 'base/activity_mobile.html', context)

def topicPage(request):
    """
    View for displaying topics.
    Shows topics filtered by search query.
    """
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics_mobile.html', context)

@login_required(login_url='login')
def notificationsPage(request):
    """
    View for displaying user notifications.
    Shows all notifications for the current user and handles marking as read.
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created')
    unread_count = notifications.filter(read=False).count()

    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = Notification.objects.get(id=notification_id)
            notification.read = True
            notification.save()

    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'base/notifications.html', context)

@login_required(login_url='login')
def createEvent(request, room_pk):
    """
    View for creating a new event in a room.
    Allows users to schedule events within a specific room.
    """
    room = Room.objects.get(id=room_pk)
    if request.method == 'POST':
        Event.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            room=room,
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time')
        )
        return redirect('room', pk=room_pk)
    return render(request, 'base/create_event.html', {'room': room})

@login_required(login_url='login')
def joinEvent(request, event_pk):
    """
    View for joining an event.
    Allows users to participate in scheduled events.
    """
    event = Event.objects.get(id=event_pk)
    event.participants.add(request.user)
    return redirect('room', pk=event.room.id)