from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import time
import logging

from .models import Message, Conversation
from .enums import MessageType, ConversationStatus

logger = logging.getLogger(__name__)


@shared_task
def process_inbound_message(message_id: str) -> None:
    """
    Processa uma nova mensagem INBOUND.
    Aguarda 5 segundos para agrupar outras mensagens recentes
    e dispara a task que vai criar a resposta OUTBOUND
    se for a última mensagem do grupo.
    """
    try:
        message = Message.objects.get(id=message_id)
        conversation = message.conversation

        five_seconds_ago = timezone.now() - timedelta(seconds=5)
        time.sleep(5)

        recent_inbounds = Message.objects.filter(
            conversation=conversation,
            type=MessageType.INBOUND.value,
            timestamp__gte=five_seconds_ago,
        ).order_by("timestamp")

        if recent_inbounds.last().id == message.id:
            message_ids = [str(msg.id) for msg in recent_inbounds]
            logger.info(
                f"[process_inbound_message] Agendando OUTBOUND com mensagens: {message_ids}"
            )

            generate_outbound_message_task.apply_async(
                (str(conversation.id), message_ids), countdown=6
            )
        else:
            logger.debug(
                f"[process_inbound_message] Ignorando mensagem {message.id}; não é a última do grupo."
            )

    except Message.DoesNotExist:
        logger.warning(
            f"[process_inbound_message] Mensagem {message_id} não encontrada."
        )


@shared_task
def generate_outbound_message_task(
    conversation_id: str, inbound_message_ids: list
) -> None:
    """
    Gera a mensagem OUTBOUND de resposta,
    agrupando os conteúdos das mensagens INBOUND recebidas.
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        messages = Message.objects.filter(id__in=inbound_message_ids).order_by(
            "timestamp"
        )

        content_lines = [f"- {msg.content}" for msg in messages]
        response_text = "Mensagens recebidas:\n" + "\n".join(content_lines)

        Message.objects.create(
            conversation=conversation,
            type=MessageType.OUTBOUND.value,
            content=response_text,
            timestamp=timezone.now(),
        )

        logger.info(
            f"[generate_outbound_message_task] OUTBOUND criada para conversation {conversation_id}"
        )

    except Conversation.DoesNotExist:
        logger.error(
            f"[generate_outbound_message_task] Conversation {conversation_id} não encontrada."
        )


@shared_task
def process_delayed_message(
    message_id: str, conversation_id: str, content: str, timestamp_str: str
) -> None:
    """
    Processa mensagens atrasadas:
    Se a conversa for criada dentro do tempo permitido,
    a mensagem é salva e processada como INBOUND.
    """
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError:
        logger.error(f"[process_delayed_message] Timestamp inválido: {timestamp_str}")
        return

    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        logger.warning(
            f"[process_delayed_message] Conversation {conversation_id} ainda não existe. Ignorando."
        )
        return

    if conversation.status == ConversationStatus.CLOSED.value:
        logger.info(
            f"[process_delayed_message] Conversation {conversation_id} está fechada. Ignorando mensagem."
        )
        return

    msg = Message.objects.create(
        id=message_id,
        conversation_id=conversation_id,
        type=MessageType.INBOUND.value,
        content=content,
        timestamp=timestamp,
    )
    logger.info(
        f"[process_delayed_message] Mensagem {msg.id} criada. Agendando processamento INBOUND."
    )
    process_inbound_message.delay(str(msg.id))
