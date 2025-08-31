import json
import urllib.parse
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth.models import AnonymousUser

# Define safe characters pattern for group names
SAFE_CHARS = re.compile(r"[^a-zA-Z0-9_\-\.]")


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get raw room name from URL
        raw_room_name = self.scope['url_route']['kwargs']['room_name']
        
        # Use urllib.parse.unquote() on the raw URL room_name for display name
        self.room_display = urllib.parse.unquote(raw_room_name)
        
        # Derive a slugified version (lowercase, replace non [a-zA-Z0-9_.-] with "-")
        self.room_slug = SAFE_CHARS.sub("-", self.room_display).lower()
        
        # Use the slug in self.room_group_name
        self.room_group_name = f"chat_{self.room_slug}"
        
        print(f"WebSocket connecting to room: {self.room_display}")
        print(f"Room slug: {self.room_slug}")
        print(f"Room group name: {self.room_group_name}")
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"WebSocket connected successfully to room: {self.room_display}")
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']
        
        if isinstance(user, AnonymousUser):
            return
        
        # Save message to database
        await self.save_message(user, message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username,
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))
    
    @database_sync_to_async
    def save_message(self, user, message):
        # Keep using the display name for DB lookups
        room = ChatRoom.objects.get(name=self.room_display)
        Message.objects.create(room=room, sender=user, content=message)
