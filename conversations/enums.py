from enum import Enum


class WebhookEventType(Enum):
    NEW_CONVERSATION = "NEW_CONVERSATION"
    NEW_MESSAGE = "NEW_MESSAGE"
    CLOSE_CONVERSATION = "CLOSE_CONVERSATION"

    @classmethod
    def choices(cls):
        return [(e.value, e.name) for e in cls]


class MessageType(Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"

    @classmethod
    def choices(cls):
        return [(e.value, e.name) for e in cls]


class ConversationStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

    @classmethod
    def choices(cls):
        return [(e.value, e.name) for e in cls]
