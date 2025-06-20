import uuid
from django.db import models


class Conversation(models.Model):
    """
    Modelo que representa uma conversa de atendimento via WhatsApp.

    Campos:
        id (UUIDField): Identificador único da conversa.
        status (CharField): Status atual da conversa ('OPEN' ou 'CLOSED').
        created_at (DateTimeField): Data e hora de criação da conversa.
        updated_at (DateTimeField): Data e hora da última atualização da conversa.

    Regras de negócio:
        - Apenas conversas com status 'OPEN' podem receber novas mensagens.
        - Conversas podem ser fechadas via evento de webhook (CLOSE_CONVERSATION).
    """

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.status}"


class Message(models.Model):
    """
    Modelo que representa uma mensagem dentro de uma conversa.

    Campos:
        id (UUIDField): Identificador único da mensagem.
        conversation (ForeignKey): Referência à conversa associada.
        type (CharField): Tipo da mensagem ('INBOUND' ou 'OUTBOUND').
        content (TextField): Conteúdo textual da mensagem.
        timestamp (DateTimeField): Data e hora da criação ou recebimento da mensagem.

    Regras de negócio:
        - Mensagens 'INBOUND' são criadas a partir de eventos recebidos via webhook.
        - Mensagens 'OUTBOUND' são geradas internamente pelo sistema via Celery.
    """

    MESSAGE_TYPES = [
        ("INBOUND", "Inbound"),
        ("OUTBOUND", "Outbound"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        """
        Retorna uma representação em string da mensagem.

        Exemplo:
            'Message <UUID> - INBOUND'
        """
        return f"Message {self.id} - {self.type}"
