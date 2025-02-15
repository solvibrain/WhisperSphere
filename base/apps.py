from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    # This Code is to check whether the app is using adapter or not 
    def ready(self):
        """
        This is just to verify that adapter is working with attached code.
        Overrides the ready() method of AppConfig to load the adapter
    
        Since the adapter is defined in settings, we need to import settings
        here to print the name of the adapter being used
        """

        print("Loading adapter...")
        from django.conf import settings
        print(f"Current adapter: {settings.SOCIALACCOUNT_ADAPTER}")