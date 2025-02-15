# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from .models import User

import logging
logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        print("=============== ADAPTER EXECUTING ===============")
        print("Google Data:", sociallogin.account.extra_data)
        logger.info("Adapter executing with data: %s", sociallogin.account.extra_data)

        
        # Get user if exists, or create new one
        # This block of code will attempt to match the user with an existing user
        # in the database. If the user does not exist, it will create a new
        # user. The user's email, first name, last name, and username will be
        # set based on the data provided by Google.
        user = sociallogin.user
        if user.id is None:
            user = sociallogin.user = self.new_user(request, sociallogin)
        
        # Get data from Google
        data = sociallogin.account.extra_data
        # Debuggiing Statements
        print("Processing user:", user.email)
        print("Available data:", data)
        # Parse and set user data
        user.email = data.get('email')
        user.first_name = data.get('given_name', '') # TODO - Handle empty first name
        user.last_name = data.get('family_name', '') # TODO - Handle empty last name
        
        # Set username (you might want to customize this)
        if not user.username: 
            user.username = data.get('email').split('@')[0]
        
        # Set other fields
        user.is_active = True
        logger.info("Adapter executing with data: %s", sociallogin.account.extra_data)
        user.last_login = timezone.now()
        
        # Get language from Google locale
        if 'locale' in data:
            user.language = data.get('locale', '').split('_')[0]  # Convert 'en_US' to 'en'
        
        # Handle avatar if present
        if 'picture' in data:
            # You might want to download and save the image
            # For now, we'll just store the URL
            from django.core.files import File
            from django.core.files.temp import NamedTemporaryFile
            import requests
            
            img_url = data['picture']
            print(f"Attempting to download image from: {img_url}")

            try:
                response = requests.get(img_url)
                if response.status_code == 200:
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(response.content)
                    img_temp.flush()
                    
                    # Generate a filename from the email
                    filename = f"avatar_{user.email.split('@')[0]}.jpg"
                    print(f"Saving image as: {filename}")
                    user.avatar.save(filename, File(img_temp), save=False)
                    print("Image saved successfully")
            except Exception as e:
                print(f"Error downloading avatar: {e}")
        
        user.save()
        print(f"User saved. Avatar path: {user.avatar.path if user.avatar else 'No avatar'}")
        return user

    def populate_user(self, request, sociallogin, data):
        """
        Called when creating a new user account. You can override user fields here before saving.
        """
        user = super().populate_user(request, sociallogin, data)
        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Enables auto-signup if email is verified with Google.
        """
        return True