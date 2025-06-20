from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import uuid4
from django.utils import timezone
from conversations.models import Conversation, Message
from conversations.enums import WebhookEventType, MessageType, ConversationStatus


class WebhookTests(APITestCase):
    def setUp(self):
        self.url = reverse("webhook")
        self.conversation_id = str(uuid4())

    def test_new_conversation(self):
        payload = {
            "type": WebhookEventType.NEW_CONVERSATION.value,
            "timestamp": timezone.now().isoformat(),
            "data": {"id": self.conversation_id},
        }
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Conversation.objects.filter(id=self.conversation_id).exists())

    def test_new_message_in_open_conversation(self):
        # Primeiro cria a conversa
        Conversation.objects.create(
            id=self.conversation_id, status=ConversationStatus.OPEN.value
        )

        message_id = str(uuid4())
        payload = {
            "type": WebhookEventType.NEW_MESSAGE.value,
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": message_id,
                "conversation_id": self.conversation_id,
                "content": "Mensagem de teste",
            },
        }
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(
            Message.objects.filter(
                id=message_id, conversation_id=self.conversation_id
            ).exists()
        )

    def test_new_message_in_nonexistent_conversation(self):
        message_id = str(uuid4())
        payload = {
            "type": WebhookEventType.NEW_MESSAGE.value,
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": message_id,
                "conversation_id": self.conversation_id,
                "content": "Mensagem sem conversa",
            },
        }
        response = self.client.post(self.url, data=payload, format="json")
        # Como o Celery pode bufferizar, o status esperado é 202 se dentro do limite, ou 400 se fora
        self.assertIn(
            response.status_code,
            [status.HTTP_202_ACCEPTED, status.HTTP_400_BAD_REQUEST],
        )

    def test_close_conversation(self):
        Conversation.objects.create(
            id=self.conversation_id, status=ConversationStatus.OPEN.value
        )

        payload = {
            "type": WebhookEventType.CLOSE_CONVERSATION.value,
            "timestamp": timezone.now().isoformat(),
            "data": {"id": self.conversation_id},
        }
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        conversation = Conversation.objects.get(id=self.conversation_id)
        self.assertEqual(conversation.status, ConversationStatus.CLOSED.value)

    def test_send_message_to_closed_conversation(self):
        Conversation.objects.create(
            id=self.conversation_id, status=ConversationStatus.CLOSED.value
        )

        message_id = str(uuid4())
        payload = {
            "type": WebhookEventType.NEW_MESSAGE.value,
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": message_id,
                "conversation_id": self.conversation_id,
                "content": "Tentando enviar para conversa fechada",
            },
        }
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Message.objects.filter(id=message_id).exists())

    def test_invalid_event_type(self):
        payload = {
            "type": "INVALID_EVENT",
            "timestamp": timezone.now().isoformat(),
            "data": {},
        }
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_uuid_in_new_message(self):
        payload = {
            "type": "NEW_MESSAGE",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": "not-a-uuid",
                "conversation_id": "also-invalid",
                "content": "Testando UUID inválido",
            },
        }
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("id", response.data)
        self.assertIn("conversation_id", response.data)

    def test_new_message_with_invalid_timestamp(self):
        payload = {
            "type": "NEW_MESSAGE",
            "timestamp": "not-a-real-date",
            "data": {
                "id": str(uuid4()),
                "conversation_id": str(uuid4()),
                "content": "Mensagem com timestamp inválido",
            },
        }
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("timestamp", response.data)

    def test_close_already_closed_conversation(self):
        Conversation.objects.create(
            id=self.conversation_id, status=ConversationStatus.CLOSED.value
        )

        payload = {
            "type": "CLOSE_CONVERSATION",
            "timestamp": timezone.now().isoformat(),
            "data": {"id": self.conversation_id},
        }

        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_webhook_without_data_field(self):
        payload = {
            "type": "NEW_CONVERSATION",
            "timestamp": timezone.now().isoformat(),
            # "data" ausente
        }

        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("data", response.data)

    def test_new_message_with_invalid_conversation_uuid(self):
        payload = {
            "type": "NEW_MESSAGE",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": str(uuid4()),
                "conversation_id": "not-a-uuid",
                "content": "Teste UUID inválido",
            },
        }

        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("conversation_id", response.data)


class ConversationEndpointsTests(APITestCase):
    def test_list_conversations(self):
        Conversation.objects.create(id=uuid4(), status=ConversationStatus.OPEN.value)
        Conversation.objects.create(id=uuid4(), status=ConversationStatus.CLOSED.value)

        url = reverse("conversation_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_conversation_detail(self):
        conv = Conversation.objects.create(
            id=uuid4(), status=ConversationStatus.OPEN.value
        )

        url = reverse("conversation_detail", kwargs={"id": conv.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["id"]), str(conv.id))
