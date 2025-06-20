# consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

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

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send_json(event["content"])