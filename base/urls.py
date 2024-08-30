from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.login_page,name="login"),
    path('logout/',views.logout_user,name="logout"),
    path('register/',views.register_user,name="register"),
   
    path('room/<str:pk>/',views.room, name="room"),
    path('user-profile/<str:pk>/', views.user_profile , name="user-profile"),
    path('update-user/<str:pk>/',views.update_user, name="update_user"),
    path('setting/',views.setting, name="setting"),
   
    path('create-room/',views.create_room,name="create-room"),
    path('update-room/<str:pk>/',views.update_room,name="update-room"),
    path('delete-room/<str:pk>/',views.delete_room,name="delete-room"),
    path('delete-message/<str:pk>/',views.delete_message ,name="delete-message"),

    path('activityPage/',views.activity_page,name="activity-page"),
    path('topicPage/',views.topic_page, name="topic-page"),
   
    path('back/',views.back,name='back'),
]
