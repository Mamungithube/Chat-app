# utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

def send_global_notification(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "global_notifications",
        {
            "type": "send_notification",
            "content": {
                "message": message,
                "type": "global_notification",
                "timestamp": str(timezone.now())
            }
        }
    )