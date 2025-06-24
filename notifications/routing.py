# routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/global-notifications/", consumers.GlobalNotificationConsumer.as_asgi()),
]