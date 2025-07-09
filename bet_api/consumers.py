import random
import asyncio
import json
import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from bet_api.models import ChatMessage,CrashGameRecord
from django.contrib.auth.models import User
from bet_api.serializers import ChatMessageSerializer
from bet_api.models.urser_model import UserProfile

User = get_user_model()





class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        db_balance = await self.get_user_balance()
        self.balance = float(db_balance) if db_balance is not None else 1000.0
        self.bet = 0.0
        self.cashed_out = False
        self.multiplier = 1.0
        self.crash_point = round(random.uniform(1.2, 5.0), 2)
        self.time_elapsed = 0
        self.max_duration = 150
        self.base_delay = 0.05
        self.max_delay = 0.3
        self.game_task = None  

        await self.accept()
        print("WebSocket connected")

        await self.send(json.dumps({
            'balance': round(self.balance, 2),
            'message': 'Please send your bet to start the game.'
        }))

    @database_sync_to_async
    def get_user_balance(self):
        if self.user and self.user.is_authenticated:
            try:
                return self.user.profile.balance
            except Exception:
                return None
        return None

    async def disconnect(self, close_code):
        print("WebSocket disconnected")
        if self.game_task:
            self.game_task.cancel()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            # Handle bet input
            if 'bet' in data and not self.game_task:
                bet_amount = float(data['bet'])
                if bet_amount > 0 and bet_amount <= self.balance:
                    self.bet = bet_amount
                    self.balance -= self.bet
                    await self.send(json.dumps({
                        'balance': round(self.balance, 2),
                        'message': f'Bet of {self.bet} accepted. Game starting...'
                    }))
                    self.game_task = asyncio.create_task(self.game_loop())
                else:
                    await self.send(json.dumps({
                        'error': 'Invalid bet amount or insufficient balance.'
                    }))

            # Handle cashout action
            elif data.get('action') == 'cashout' and self.game_task:
                self.cashed_out = True

        except (json.JSONDecodeError, ValueError):
            await self.send(json.dumps({'error': 'Invalid request.'}))

    async def game_loop(self):
        multiplier = self.multiplier
        time_elapsed = self.time_elapsed
        crash_point = self.crash_point

        while multiplier < crash_point and time_elapsed < self.max_duration and not self.cashed_out:
            # Simulate crash/increase logic
            distance_to_crash = crash_point - multiplier
            decrement_chance = max(0.05, min(0.3, distance_to_crash / 10))

            if random.random() < decrement_chance:
                # Decrease
                if multiplier < 2:
                    decrement = random.uniform(0.005, 0.01)
                elif multiplier < 3.5:
                    decrement = random.uniform(0.01, 0.02)
                else:
                    decrement = random.uniform(0.02, 0.04)
                multiplier = max(1.0, multiplier - decrement)
            else:
                # Increase
                if multiplier < 2:
                    increment = random.uniform(0.008, 0.015)
                elif multiplier < 3.5:
                    increment = random.uniform(0.02, 0.04)
                else:
                    increment = random.uniform(0.04, 0.07)
                multiplier += increment

            multiplier = round(multiplier, 2)

            await self.send(json.dumps({
                'multiplier': multiplier,
                'status': 'running',
                'balance': round(self.balance, 2)
            }))

            delay = min(self.max_delay, self.base_delay + (time_elapsed * 0.002))
            await asyncio.sleep(delay)

            time_elapsed += 1

        # Handle end of game
        if self.cashed_out:
            winnings = round(self.bet * multiplier, 2)
            self.balance += winnings
            await self.send(json.dumps({
                'multiplier': multiplier,
                'status': 'cashed_out',
                'winnings': winnings,
                'balance': round(self.balance, 2),
                'message': f'You cashed out and won {winnings}!'
            }))
        else:
            await self.send(json.dumps({
                'multiplier': multiplier,
                'status': 'crashed',
                'winnings': 0,
                'balance': round(self.balance, 2),
                'message': 'You crashed and lost your bet.'
            }))

        # Reset game state for replay
        self.game_task = None
        self.cashed_out = False
        self.multiplier = 1.0
        self.crash_point = round(random.uniform(1.2, 5.0), 2)
        self.time_elapsed = 0
        self.bet = 0.0

        await self.send(json.dumps({
            'message': 'Game over. Send a new bet to play again.'
        }))






class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        try:
            self.other_user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        except (KeyError, ValueError):
            await self.close()
            return

        if self.user.id == self.other_user_id:
            await self.close()
            return

        user_ids = sorted([self.user.id, self.other_user_id])
        self.room_group_name = f"chat_{user_ids[0]}_{user_ids[1]}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # 🔥 Send chat history after accepting connection
        messages = await self.get_chat_history(self.user.id, self.other_user_id)
        await self.send(text_data=json.dumps({
            "type": "chat_history",
            "messages": messages
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message_type = data.get("type")

        if message_type == "chat":
            await self.handle_chat(data)
        elif message_type in ["offer", "answer", "ice-candidate"]:
            await self.handle_webrtc_signaling(data)
        elif message_type == "document":
            await self.handle_document(data)

    async def handle_chat(self, data):
        message = data.get("message")
        receiver_id = data.get("receiver_id")
        if not message or not receiver_id:
            return

        receiver = await self.get_user_by_id(receiver_id)
        if not receiver:
            return

        saved_message = await self.save_message(self.user, receiver, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_id": self.user.id,
                "receiver_id": receiver.id,
                "timestamp": saved_message.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
            "sender_id": event["sender_id"],
            "receiver_id": event["receiver_id"],
            "timestamp": event["timestamp"]
        }))

    async def handle_webrtc_signaling(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "webrtc_message",
                **data,
                "sender": self.user.username
            }
        )

    async def webrtc_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def handle_document(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "document_message",
                "document_url": data.get("document_url"),
                "file_name": data.get("file_name"),
                "sender": self.user.username
            }
        )

    async def document_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "document",
            "document_url": event["document_url"],
            "file_name": event["file_name"],
            "sender": event["sender"]
        }))

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        return ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)

    @database_sync_to_async
    def get_chat_history(self, user1_id, user2_id):
        messages = ChatMessage.objects.filter(
            sender_id__in=[user1_id, user2_id],
            receiver_id__in=[user1_id, user2_id]
        ).order_by("timestamp")
        return ChatMessageSerializer(messages, many=True).data
# End of code