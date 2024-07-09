from django.db.models.deletion import CASCADE
from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Topic(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host=models.ForeignKey(User, on_delete= models.SET_NULL,null=True)  # on_delte is for that if parent get deleted then child will remain in the database.
    topic=models.ForeignKey('Topic', on_delete= models.SET_NULL, null=True) 
    # id= models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)+
    name=models.CharField(max_length=200)
    description= models.TextField(null=True, blank=True)
    participants=models.ManyToManyField(User,related_name='participants', blank=True)
    update= models.DateTimeField(auto_now=True)
    created= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-update','-created']
    
    def __str__(self) :
        return self.name


class Message(models.Model):
    user=models.ForeignKey(User, on_delete= models.CASCADE)
    room= models.ForeignKey(Room, on_delete= models.CASCADE)        
    body= models.TextField()
    update= models.DateTimeField(auto_now=True)
    created= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-update','-created']

    def __str__(self):
        return self.body[0:50]