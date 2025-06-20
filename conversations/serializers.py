from rest_framework import serializers
from .models import Conversation, Message
from .enums import WebhookEventType


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "type", "content", "timestamp"]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "status", "created_at", "updated_at", "messages"]


class NewConversationDataSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class NewMessageDataSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    conversation_id = serializers.UUIDField()
    content = serializers.CharField()


class CloseConversationDataSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class WebhookSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=WebhookEventType.choices())
    timestamp = serializers.DateTimeField()
    data = serializers.DictField()

    def validate(self, attrs):
        event_type = attrs.get("type")
        data = attrs.get("data")

        if event_type == WebhookEventType.NEW_CONVERSATION.value:
            serializer = NewConversationDataSerializer(data=data)
        elif event_type == WebhookEventType.NEW_MESSAGE.value:
            serializer = NewMessageDataSerializer(data=data)
        elif event_type == WebhookEventType.CLOSE_CONVERSATION.value:
            serializer = CloseConversationDataSerializer(data=data)
        else:
            raise serializers.ValidationError({"type": "Unknown event type"})

        serializer.is_valid(raise_exception=True)
        attrs["data"] = serializer.validated_data
        return attrs
