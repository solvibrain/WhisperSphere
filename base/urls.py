from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutUser,name="logout"),
    path('register/',views.registerUser,name="register"),
   
    path('room/<str:pk>/',views.room, name="room"),
    path('userProfile/<str:pk>/', views.userProfile , name="user-profile"),
    path('update-user/',views.updateUser, name="updateUser"),
    path('setting/',views.setting, name="setting"),
   
    path('create-room/',views.createRoom,name="create-room"),
    path('update-room/<str:pk>/',views.updateRoom,name="update-room"),
    path('delete-room/<str:pk>/',views.deleteRoom,name="delete-room"),
    path('delete-message/<str:pk>/',views.deleteMessage ,name="delete-message"),

    path('activityPage/',views.activityPage,name="activity-page"),
    path('topicPage/',views.topicPage, name="topic-page"),
   
    path('back/',views.back,name='back'),
]
