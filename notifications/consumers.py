# consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import Notification

class GlobalNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print("WebSocket connecting... user:", self.scope["user"])
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            print("Anonymous user, closing WebSocket")
            await self.close()
        else:
            self.group_name = "global_notifications"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        
    @database_sync_to_async
    def save_notification(self, user, message):
        """Save notification to database synchronously"""
        Notification.objects.create(
            user=user,
            message=message
        )



    async def receive(self, text_data=None, **kwargs):
        data = json.loads(text_data)
        message = data.get("message", "")
        await self.save_notification(self.user, message)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_notification",
                "content": {
                    "user": self.user.username,
                    "message": message
                }
            }
        )
        
    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        content = event.get("content", {})
        await self.send_json(content)
