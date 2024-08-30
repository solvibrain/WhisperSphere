from django.shortcuts import render,redirect
from .models import Room,Topic,Message,User
from django.db import IntegrityError
from django.http import HttpResponse
from .forms import RoomForm
from .forms import UserForm,MyUserCreationForm


from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q # this import is for using and or in the searching method
from .utils import validate_name # helpful function

# rooms=[
#         {"id":1, "name":"Pthon Web Development Course"},
#         {"id":2,"name":"Django Course"},
#         {"id":3,"name":"Developing PRoject"},
#     ]
# Create your views here.
def index(request):
#    room=[
#         {"id":1, "name":"Pthon Web Development Course"},
#         {"id":2,"name":"Django Course"},
#         {"id":3,"name":"Developing PRoject"},
#     ]
   q=request.GET.get('q') if request.GET.get('q') != None else ''
   rooms= Room.objects.filter(Q(topic__name__icontains=q)|
                              Q(name__icontains=q)|
                              Q(description__icontains=q))
   topics= Topic.objects.all()[0:5]
   room_count=rooms.count()
   room_messages=Message.objects.filter(Q(room__topic__name__icontains = q)|
                                        Q(room__name__icontains = q)| Q(body__icontains =q))
   context={'rooms':rooms,'topics':topics,'room_count': room_count,'room_messages':room_messages}
   
   return render(request,'base/index.html',context)


def login_page(request):
   page='login'
   
   if request.user.is_authenticated:
      return redirect('index')

   if request.method ==  'POST':
      
      email=request.POST.get('email').lower()
      password=request.POST.get('password')

      try:
         user=User.objects.get(email=email)
         user=authenticate(request,email=email,password=password) 
         if user is not None:
            login(request,user)
            return redirect('index')
         else:
            messages.error(request,"Email and Password  Does not Exist")
      except:
         messages.error(request,'User does not exist')   
      

      # if user is not None:
      #    login(request,user)
      #    return redirect('index')
      # else:
      #    messages.error(request,"username and Password  Does not Exist")

   context={'page':page}
   return render(request,'base/login_page.html',context)

# creating the view function for the loging out the user
def logout_user(request):
   logout(request)
   return redirect('index')




# creting the view for the registeration of the usser
def register_user(request):
   form=MyUserCreationForm()
   context={'form':form}
   if request.method =="POST":
      form=MyUserCreationForm(request.POST)
      if form.is_valid():
         user=form.save(commit=False)
         user.username=user.username.lower()
         user.save()
         print("pass1")
         user.backend = 'django.contrib.auth.backends.ModelBackend'
         print("pass2")
         login(request,user)
         print("pass3")
         return redirect('index')
      else:
         messages.error(request,'Ther is some Error Occured while you registering the page.')
   return render(request,'base/login_page.html',context)



# creating the view for the userProfile 
def user_profile(request,pk):
   user= User.objects.get(id=pk)
   room= user.rooms.all()
   room_messages= user.messages.all()
   topics=Topic.objects.all()
   context={'user' : user,'rooms':room,'topics':topics , 'room_messages':room_messages}
   return render(request,'base/userProfile.html',context)


@login_required(login_url='login')
def update_user(request):
   user=request.user
   form=UserForm(instance=user)
   context={'form':form}
   if request.method == 'POST':
      # this code is for using Form prefilled before usig it for updating
      form=UserForm(request.POST,request.FILES,instance=user)
      if form.is_valid():
         form.save()
         return redirect('user-profile', pk=user.id)
   return render(request,'base/update-user.html',context)





def room(request,pk):
   room=None
   room= Room.objects.get(id=pk)
   room_messages=room.room_messages.all() # this is for getting all the message for related room , because here we are using many to one relationship
   participants=room.participants.all()
   if request.method =='POST':
      message = Message.objects.create(
         user=request.user,
         room=room,
         body=request.POST.get('message_body')
      )
      room.participants.add(request.user)
      return redirect('room',pk=room.id) 

   
   context={'room':room,'room_messages':room_messages,'participants':participants}
   return render(request,'base/room.html', context)



#Here Decorator is used for restriction of loging in and if not then allowing them to login
@login_required(login_url='login')
def create_room(request):
   page='create'
   form=RoomForm()
   topics=Topic.objects.all()
   if request.method =="POST":
      topic_name=request.POST.get('topic')
      room_name = request.POST.get('name')
      # adding Checks for the input values
      
      # Validate topic name
      is_valid, error_message = validate_name(topic_name)
      if not is_valid:
          messages.error(request, f"Invalid topic name:{error_message}")
          return redirect('create-room')
      
      # Validate room name
      is_valid, error_message = validate_name(room_name, check_profanity=False)
      if not is_valid:
          messages.error(request, f"Invalid room name:{error_message}")
          return redirect('create-room')
      
      # Check if room name already exists
      if Room.objects.filter(name=room_name).exists():
          messages.error(request, "A room with this name already exists.")
          return redirect('create-room')
      
      # If all checks pass, create the topic and room
      topic,created = Topic.objects.get_or_create(name=topic_name)
      
      try:
          room = Room.objects.create(
              host=request.user,
              topic=topic,
              name=room_name,
              description=request.POST.get('description')
          )
          return redirect('room', pk=room.id)
      except IntegrityError:
          messages.error(request, "An error occurred while creating the room. Please try again.")
          return redirect('create-room')
      # form= RoomForm(request.POST)
      # #this code is for saving the data filled inthe form in the database.
      # if form.is_valid():
      #    room=form.save(commit=False)
      #    room.host= request.user
      #    room.save()
   context={'form':form , 'topics':topics,'page':page}
   return render(request,'base/create_room.html',context)   


#Here Decorator is used for restriction of loging in and if not then allowing them to login
@login_required(login_url='login')
def update_room(request,pk):
   room=Room.objects.get(id=pk)
   form=RoomForm(instance=room)
   topics=Topic.objects.all()
   context={'form':form, 'topics':topics, 'room':room}
   # restriction code
   if request.user != room.host:# This code is for restricting other user to update another room and this code can be used somewhere else
      return HttpResponse("You are not allowed to do this because you are not the host of this room")
   
   if request.method =="POST":
      topic_name=request.POST.get('topic')
      room_name = request.POST.get('name')
      # adding Checks for the input values
      
      # Validate topic name
      is_valid, error_message = validate_name(topic_name)
      if not is_valid:
          messages.error(request, f"Invalid topic name:{error_message}")
          return redirect('update-room',pk = pk)
      
      # Validate room name
      is_valid, error_message = validate_name(room_name, check_profanity=False)
      if not is_valid:
          messages.error(request, f"Invalid room name:{error_message}")
          return redirect('update-room',pk = pk)
      
      topic,created =Topic.objects.get_or_create(name=topic_name)
      try:
         
         room.name=room_name
         room.description=request.POST.get('description')
         room.topic = topic
         room.save()
         return redirect('room', pk=room.id)
         
      except IntegrityError:
          messages.error(request, "An error occurred while updating the room. Please try again.")
          return redirect('update-room',pk = pk)
      # form= RoomForm(request.POST,instance=room)
      # if form.is_valid():
      #    form.save()
      
   return render(request,'base/create_room.html',context)



#Here Decorator is used for restriction of loging in and if not then allowing them to login
@login_required(login_url='login')
def delete_room(request,pk):
   room=Room.objects.get(id=pk)

   if request.user != room.host:# This code is for restricting other user to update another room and this code can be used somewhere else
      return HttpResponse("You are not allowed to do this because you are not the host of this room")
   
   if request.method == "POST":
      room.delete()
      return redirect('index')
   return render(request,'base/deleteRoom.html',{'obj':room})



# This view is for the user giving him a permission to user to delete his own message
@login_required(login_url='login')
def delete_message(request,pk):
   message=Message.objects.get(id=pk)
   

   if request.user != message.user:
      return HttpResponse("you are not allowed to delete others message")

   if request.method == "POST":
      message.delete()
      return redirect('index')
   return render(request,'base/deleteRoom.html',{'obj':message})


def back(request):
    previous_page = request.META.get('HTTP_REFERER')
    if previous_page:
        return redirect(previous_page)
    else:
        # If there is no previous page, redirect to a default URL
        return redirect('index')   
    
   #  creating the view for the login page


@login_required(login_url='login')
def setting(request):
   return render(request,'base/settings.html')


@login_required(login_url='login')
def activity_page(request):
   q=request.GET.get('q') if request.GET.get('q') != None else ''
   room_messages=Message.objects.filter(Q(room__topic__name__icontains = q)|
                                        Q(room__name__icontains = q))
   context={'room_messages':room_messages}
   return render(request,'base/activity_mobile.html',context)


def topic_page(request):
   q=request.GET.get('q') if request.GET.get('q') != None else ''
   topics=Topic.objects.filter(Q(name__icontains = q))
   context={'topics':topics}
   return render(request,'base/topics_mobile.html',context)