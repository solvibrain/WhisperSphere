from django.contrib import admin
from .models import Room,Message,Topic,UserProfile,Badge,Event, Notification,Tag

# Register your models here.
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Topic)
admin.site.register(UserProfile)
admin.site.register(Badge)
admin.site.register(Event)
admin.site.register(Notification)
admin.site.register(Tag)

