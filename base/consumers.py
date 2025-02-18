from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Message, Room, User
from datetime import datetime
import asyncio
from typing import Awaitable




class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope["user"]
        
        # Update user's last seen and send presence update
        await self.update_user_presence(True)


        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Update user's last seen and send presence update
        await self.update_user_presence(False)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        # Handle different message types
        if 'type' in text_data_json:
            if text_data_json['type'] == 'typing':
                await self.handle_typing(text_data_json)
                return
            elif text_data_json['type'] == 'read_receipt':
                await self.handle_read_receipt(text_data_json)
                return
                
        message = text_data_json['message']

        
        # Save the message to the database
        message_obj = await self.save_message(message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.scope["user"].username,
                'user_id': str(self.scope["user"].id),
                'avatar_url': self.scope["user"].avatar_url,
                'message_id': str(message_obj.id),
                'timestamp': message_obj.created.isoformat()
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def typing_status(self, event):
        # Send typing status to WebSocket
        await self.send(text_data=json.dumps(event))

    async def read_receipt(self, event):
        # Send read receipt to WebSocket
        await self.send(text_data=json.dumps(event))

    async def presence_update(self, event):
        # Send presence update to WebSocket
        await self.send(text_data=json.dumps(event))

    async def handle_typing(self, data):
        # Broadcast typing status to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_status',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': data['is_typing']
            }
        )

    async def handle_read_receipt(self, data):
        # Update message read status
        await self.mark_message_read(data['message_id'])
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt',
                'message_id': data['message_id'],
                'user_id': str(self.user.id),
                'username': self.user.username
            }
        )

    @database_sync_to_async
    def update_user_presence(self, is_online):
        user = User.objects.get(id=self.user.id)
        user.last_seen = datetime.now()
        user.save()
        
        # Broadcast presence update
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'presence_update',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_online': is_online,
                'last_seen': user.last_seen.isoformat()
            }
        )



    @database_sync_to_async
    def mark_message_read(self, message_id):
        message = Message.objects.get(id=message_id)
        message.read = True
        message.save()


    @database_sync_to_async
    def save_message(self, message) -> Awaitable[Message]:
        room = Room.objects.get(id=self.room_id)
        message_obj = Message.objects.create(
            user=self.scope["user"],
            room=room,
            body=message
        )
        room.participants.add(self.scope["user"])
        room.save()  # Ensure room changes are saved
        return message_obj
