from django.urls import path
from . import views
urlpatterns = [
    path('rooms/',views.getRooms, name = "getrooms"),
    path('room/<str:pk>/',views.getSingleRoom , name ="getSingleRoom"),
]