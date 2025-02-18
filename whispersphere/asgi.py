"""
ASGI config for whispersphere project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""


import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whispersphere.settings')
django.setup()  # Add this line before get_asgi_application()

application = get_asgi_application()