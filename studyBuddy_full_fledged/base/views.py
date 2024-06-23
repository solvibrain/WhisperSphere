from django.shortcuts import render,redirect
from .models import Room,Topic,Message
from django.http import HttpResponse
from .forms import RoomForm
from .forms import userForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q # this import is for using andd or in the searching mehtod

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
                                        Q(room__name__icontains = q))
   context={'rooms':rooms,'topics':topics,'room_count': room_count,'room_messages':room_messages}
   
   return render(request,'base/index.html',context)


def room(request,pk):
   room=None
   room= Room.objects.get(id=pk)
   room_messages=room.message_set.all()  # type: ignore #this code is used for the sepecificity of theindividuality
   participants=room.participants.all()
   if request.method =='POST':
      message=Message.objects.create(
         user=request.user,
         room=room,
         body=request.POST.get('message_body')
      )
      room.participants.add(request.user)
      return redirect('room',pk=room.id) # type: ignore

   
   context={'rooms':room,'room_messages':room_messages,'participants':participants}
   return render(request,'base/room.html', context)



#Here Decorator is used for restriction of loging in and if not then allowing them to login
@login_required(login_url='login')
def createRoom(request):
   page='create'
   form=RoomForm()
   topics=Topic.objects.all()
   if request.method =="POST":
      topic_name=request.POST.get('topic')
      topic,created =Topic.objects.get_or_create(name=topic_name)
      Room.objects.create(
         host=request.user,
         topic=topic,
         name=request.POST.get('name'),
         description=request.POST.get('description')
      )
      return redirect('index')
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
def updateRoom(request,pk):
   room=Room.objects.get(id=pk)
   form=RoomForm(instance=room)
   topics=Topic.objects.all()
   context={'form':form, 'topics':topics, 'room':room}
   # restriction code
   if request.user != room.host:# This code is for restricting other user to update another room and this code can be used somewhere else
      return HttpResponse("You are not allowed to do this because you are not the host of this room")
   
   if request.method =="POST":
      topic_name=request.POST.get('topic')
      topic,created =Topic.objects.get_or_create(name=topic_name)
      room.name=request.POST.get('name')
      room.description=request.POST.get('description')
      room.topic = topic_name
      room.save()

      # form= RoomForm(request.POST,instance=room)
      # if form.is_valid():
      #    form.save()
      return redirect('index')
   return render(request,'base/create_room.html',context)



#Here Decorator is used for restriction of loging in and if not then allowing them to login
@login_required(login_url='login')
def deleteRoom(request,pk):
   room=Room.objects.get(id=pk)

   if request.user != room.host:# This code is for restricting other user to update another room and this code can be used somewhere else
      return HttpResponse("You are not allowed to do this because you are not the host of this room")
   
   if request.method == "POST":
      room.delete()
      return redirect('index')
   return render(request,'base/deleteRoom.html',{'obj':room})



# This view is for the user giving him a permission to user to delete his own message
@login_required(login_url='login')
def deleteMessage(request,pk):
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
def loginPage(request):
   page='login'
   if request.user.is_authenticated:
      return redirect('index')

   if request.method ==  'POST':
      username=request.POST.get('username').lower()
      password=request.POST.get('password')

      try:
         user=User.objects.get(username=username)
      except:
         messages.error(request,'User does not exitst')   
      user=authenticate(request,username=username,password=password)   

      if user is not None:
         login(request,user)
         return redirect('index')
      else:
         messages.error(request,"username and Password  Does not Exist")

   context={'page':page}
   return render(request,'base/login_page.html',context)

# creating the view function for the loging out the user
def logoutUser(request):
   logout(request)
   return redirect('index')




# creting the view for the registeration of the usser
def registerUser(request):
   form=UserCreationForm()
   context={'form':form}
   if request.method =="POST":
      form=UserCreationForm(request.POST)
      if form.is_valid():
         user=form.save(commit=False)
         user.username=user.username.lower()
         user.save()
         login(request,user)
         return redirect('index')
      else:
         messages.error(request,'Ther is some Error Occured while you registering the page.')
   return render(request,'base/login_page.html',context)



# creating the view for the userProfile 
def userProfile(request,pk):
   user= User.objects.get(id=pk)
   room= user.room_set.all()
   room_messages= user.message_set.all()
   topics=Topic.objects.all()
   context={'user' : user,'rooms':room,'topics':topics , 'room_messages':room_messages}
   return render(request,'base/userProfile.html',context)


@login_required(login_url='login')
def updateUser(request):
   user=request.user
   form=userForm(instance=user)
   context={'form':form}
   if request.method == 'POST':
      form=userForm(request.POST,instance=user)
      if form.is_valid():
         form.save()
         return redirect('user-profile', pk=user.id)
   return render(request,'base/update-user.html',context)



@login_required(login_url='login')
def setting(request):
   return render(request,'base/settings.html')


@login_required(login_url='login')
def activityPage(request):
   q=request.GET.get('q') if request.GET.get('q') != None else ''
   room_messages=Message.objects.filter(Q(room__topic__name__icontains = q)|
                                        Q(room__name__icontains = q))
   context={'room_messages':room_messages}
   return render(request,'base/activity_mobile.html',context)


def topicPage(request):
   q=request.GET.get('q') if request.GET.get('q') != None else ''
   topics=Topic.objects.filter(Q(name__icontains = q))
   context={'topics':topics}
   return render(request,'base/topics_mobile.html',context)