from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_notification_api(request):
    message = request.data.get("message", "")
    user = request.user

    # Save to database
    Notification.objects.create(user=user, message=message)

    # Send to WebSocket group
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "global_notifications",
        {
            "type": "send_notification",
            "content": {
                "user": user.username,
                "message": message
            }
        }
    )

    return Response({"status": "sent"})
