# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'global-notifications/$', consumers.GlobalNotificationConsumer.as_asgi()),
]