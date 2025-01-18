# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import UserProfile

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        return super().pre_social_login(request, sociallogin)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Create UserProfile if it doesn't exist
        UserProfile.objects.get_or_create(user=user)
        return user