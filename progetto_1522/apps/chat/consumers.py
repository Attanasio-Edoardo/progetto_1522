"""
apps/chat/consumers.py

WebSocket consumer per la chat real-time tra vittima e operatore.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Gestisce la connessione WebSocket per una chat room associata a un ticket.
    Ogni ticket ha il suo gruppo: 'chat_ticket_{ticket_id}'.
    """

    async def connect(self):
        self.ticket_id   = self.scope['url_route']['kwargs']['ticket_id']
        self.room_group  = f'chat_ticket_{self.ticket_id}'

        # Unisci al gruppo della chat
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        """Riceve un messaggio dal WebSocket e lo distribuisce al gruppo."""
        data = json.loads(text_data)
        testo         = data.get('message', '').strip()
        tipo_mittente = data.get('tipo_mittente', 'VITTIMA')

        if not testo:
            return

        # Salva il messaggio nel DB
        await self.salva_messaggio(testo, tipo_mittente)

        # Distribuisci a tutti nel gruppo
        await self.channel_layer.group_send(
            self.room_group,
            {
                'type': 'chat_message',
                'message': testo,
                'tipo_mittente': tipo_mittente,
                'timestamp': timezone.now().strftime('%H:%M'),
            }
        )

    async def chat_message(self, event):
        """Invia il messaggio al WebSocket del client."""
        await self.send(text_data=json.dumps({
            'message':       event['message'],
            'tipo_mittente': event['tipo_mittente'],
            'timestamp':     event['timestamp'],
        }))

    @database_sync_to_async
    def salva_messaggio(self, testo, tipo_mittente):
        from apps.chat.models import Messaggio
        from apps.tickets.models import Ticket

        try:
            ticket = Ticket.objects.get(pk=self.ticket_id)
        except Ticket.DoesNotExist:
            return

        user = self.scope.get('user')
        Messaggio.objects.create(
            ticket=ticket,
            operatore=user if (user and user.is_authenticated) else None,
            tipo_mittente=tipo_mittente,
            testo=testo,
        )
