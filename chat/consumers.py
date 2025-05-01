# # code solved

# import json
# from channels.generic.websocket import WebsocketConsumer
# from django.contrib.auth.models import User
# from .models import Message
# from asgiref.sync import async_to_sync

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_code']
#         self.group_name = f'room_{self.room_name}'

#         self.user = self.scope.get('user')  #  missing chilo 

#         if not self.user or not self.user.is_authenticated:
#             self.close()
#             return

#         async_to_sync(self.channel_layer.group_add)(
#             self.group_name,
#             self.channel_name
#         )
#         self.accept()

#         self.send(text_data=json.dumps({
#             'type': 'connected',
#             'message': f'Welcome {self.user.username} to {self.room_name} chat room!'
#         }))

#     def disconnect(self, close_code):
#         if hasattr(self, 'group_name'):
#             async_to_sync(self.channel_layer.group_discard)(
#                 self.group_name,
#                 self.channel_name
#             )

#     def receive(self, text_data):
#         try:
#             data = json.loads(text_data)
#             message = data.get('message')
#             receiver_id = data.get('receiver')

#             if not message or not receiver_id:
#                 self.send(text_data=json.dumps({'error': 'Message and receiver are required'}))
#                 return

#             try:
#                 receiver = User.objects.get(id=receiver_id)
#             except User.DoesNotExist:
#                 self.send(text_data=json.dumps({'error': 'Receiver does not exist'}))
#                 return

#             Message.objects.create(
#                 sender=self.user,
#                 receiver=receiver,
#                 content=message
#             )

#             # Broadcast to room
#             async_to_sync(self.channel_layer.group_send)(
#                 self.group_name,
#                 {
#                     'type': 'chat_message',
#                     'message': f"{self.user.username}: {message}"
#                 }
#             )

#         except json.JSONDecodeError:
#             self.send(text_data=json.dumps({'error': 'Invalid JSON'}))

#     def chat_message(self, event):
#         message = event['message']
#         self.send(text_data=json.dumps({'message': message}))

# personal send massage 

import json
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from asgiref.sync import async_to_sync
from django.core.cache import cache

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.group_name = f'room_{self.room_name}'
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            self.close()
            return
        cache.set(f'user_{self.user.id}_channel', self.channel_name, timeout=300)  # 5 minute timeout

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

        self.send(text_data=json.dumps({
            'type': 'connected',
            'message': f'Welcome {self.user.username} to {self.room_name} chat room!'
        }))

    def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            cache.delete(f'user_{self.user.id}_channel')
        
        if hasattr(self, 'group_name'):
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name
            )

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message')
            receiver_id = data.get('receiver')

            if not message or not receiver_id:
                self.send(text_data=json.dumps({'error': 'Message and receiver are required'}))
                return

            try:
                receiver = User.objects.get(id=receiver_id)
            except User.DoesNotExist:
                self.send(text_data=json.dumps({'error': 'Receiver does not exist'}))
                return

            Message.objects.create(
                sender=self.user,
                receiver=receiver,
                content=message
            )

            receiver_channel_name = cache.get(f'user_{receiver.id}_channel')
            
            if receiver_channel_name:
                async_to_sync(self.channel_layer.send)(
                    receiver_channel_name,
                    {
                        'type': 'private.message',
                        'message': f"{self.user.username}: {message}",
                        'sender_id': self.user.id
                    }
                )
                
                self.send(text_data=json.dumps({
                    'message': f"You to {receiver.username}: {message}",
                    'receiver_id': receiver.id
                }))
            else:
                self.send(text_data=json.dumps({
                    'error': 'Recipient is not currently online'
                }))

        except json.JSONDecodeError:
            self.send(text_data=json.dumps({'error': 'Invalid JSON'}))

    def private_message(self, event):
        self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id']
        }))