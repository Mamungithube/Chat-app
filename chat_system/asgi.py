"""
ASGI config for chat_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns as chat_ws
from notifications.routing import websocket_urlpatterns as notif_ws
from chat.middleware import JWTAuthMiddleware  # অথবা একটি global middleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

# Combine all websocket routes
websocket_urlpatterns = chat_ws + notif_ws

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # normal Django views
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})

