"""WebSocket consumer for hearing room live chat."""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class HearingChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time hearing room chat."""

    async def connect(self):
        self.hearing_id = self.scope['url_route']['kwargs']['hearing_id']
        self.room_group_name = f'hearing_chat_{self.hearing_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

        # Notify others of join
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'username': self.user.display_name,
                'role': self.user.get_role_display(),
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()

        if not message:
            return

        # Save to database
        await self.save_message(message)

        # Broadcast
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.display_name,
                'role': self.user.get_role_display(),
                'timestamp': timezone.now().strftime('%H:%M'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'role': event['role'],
            'timestamp': event['timestamp'],
        }))

    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'join',
            'username': event['username'],
            'role': event['role'],
        }))

    @database_sync_to_async
    def save_message(self, message):
        from hearings.models import ChatMessage, Hearing
        try:
            hearing = Hearing.objects.get(pk=self.hearing_id)
            ChatMessage.objects.create(
                hearing=hearing,
                sender=self.user,
                message=message,
            )
        except Hearing.DoesNotExist:
            pass
