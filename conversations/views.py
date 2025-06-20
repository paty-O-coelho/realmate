from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, WebhookSerializer
from .tasks import process_inbound_message, process_delayed_message
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample
from .enums import WebhookEventType, MessageType, ConversationStatus


@extend_schema(
    request=WebhookSerializer,
    responses={201: None, 202: None, 200: None, 400: None, 404: None},
    examples=[
        OpenApiExample(
            name="NEW_CONVERSATION",
            value={
                "type": "NEW_CONVERSATION",
                "timestamp": "2025-06-04T14:20:00Z",
                "data": {"id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"},
            },
            request_only=True,
        ),
        OpenApiExample(
            name="NEW_MESSAGE",
            value={
                "type": "NEW_MESSAGE",
                "timestamp": "2025-06-04T14:20:05Z",
                "data": {
                    "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
                    "content": "Olá, quero informações sobre alugar um apartamento.",
                    "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a",
                },
            },
            request_only=True,
        ),
        OpenApiExample(
            name="CLOSE_CONVERSATION",
            value={
                "type": "CLOSE_CONVERSATION",
                "timestamp": "2025-06-04T14:25:00Z",
                "data": {"id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"},
            },
            request_only=True,
        ),
    ],
)
@api_view(["POST"])
def webhook(request):
    """
    Webhook para receber eventos de conversas e mensagens.
    Processa os eventos de acordo com o tipo:
    - NEW_CONVERSATION: cria nova conversa.
    - NEW_MESSAGE: processa nova mensagem.
    - CLOSE_CONVERSATION: fecha conversa.
    """
    serializer = WebhookSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    event_type = serializer.validated_data["type"]
    timestamp_dt = serializer.validated_data["timestamp"]
    data = serializer.validated_data["data"]

    if event_type == WebhookEventType.NEW_CONVERSATION.value:
        conversation_id = data["id"]

        created, _ = Conversation.objects.get_or_create(id=conversation_id)
        if not created:
            return Response({"error": "Conversation already exists"}, status=400)

        return Response({"message": "Conversation created"}, status=201)

    elif event_type == WebhookEventType.NEW_MESSAGE.value:
        conversation_id = data["conversation_id"]
        message_id = data["id"]
        content = data["content"]

        now = timezone.now()
        conversation = Conversation.objects.filter(id=conversation_id).first()

        if not conversation:
            diff = now - timestamp_dt
            if diff.total_seconds() <= 6:
                process_delayed_message.apply_async(
                    (
                        str(message_id),
                        str(conversation_id),
                        content,
                        timestamp_dt.isoformat(),
                    ),
                    countdown=6 - diff.total_seconds(),
                )
                return Response({"message": "Message buffered"}, status=202)
            return Response({"error": "Conversation does not exist"}, status=400)

        if conversation.status == ConversationStatus.CLOSED.value:
            return Response({"error": "Conversation is closed"}, status=400)

        msg = Message.objects.create(
            id=message_id,
            conversation_id=conversation_id,
            type=MessageType.INBOUND.value,
            content=content,
            timestamp=timestamp_dt,
        )
        process_inbound_message.delay(str(msg.id))
        return Response({"message": "Message received"}, status=202)

    elif event_type == WebhookEventType.CLOSE_CONVERSATION.value:
        conversation_id = data["id"]
        conversation = Conversation.objects.filter(id=conversation_id).first()

        if not conversation:
            return Response({"error": "Conversation not found"}, status=404)

        if conversation.status == ConversationStatus.CLOSED.value:
            return Response({"error": "Conversation already closed"}, status=400)

        conversation.status = ConversationStatus.CLOSED.value
        conversation.updated_at = timezone.now()
        conversation.save()

        return Response({"message": "Conversation closed"}, status=200)

    return Response({"error": "Unknown event type"}, status=400)


@api_view(["GET"])
def conversation_detail(request, id):
    conversation = get_object_or_404(Conversation, id=id)
    serializer = ConversationSerializer(conversation)
    return Response(serializer.data)


@api_view(["GET"])
def conversation_list(request):
    conversations = Conversation.objects.all()
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)
