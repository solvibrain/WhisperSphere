from django.forms import ModelForm
from .models import Room,User
from django.contrib.auth.forms import UserCreationForm

class RoomForm(ModelForm):
    class Meta:
        model=Room
        fields= '__all__'
        exclude=['host','participants']



class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['avatar','first_name','last_name', 'bio', 'username','email']

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields =['first_name','last_name', "username","email","password1","password2"]
