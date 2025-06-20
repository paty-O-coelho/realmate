import requests
import time
import uuid
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/webhook/"
CONVERSATION_ID = str(uuid.uuid4())

def iso_now():
    return datetime.now(timezone.utc).isoformat()

def post_event(event_type, data, timestamp=None):
    payload = {
        "type": event_type,
        "timestamp": timestamp or iso_now(),
        "data": data
    }
    response = requests.post(BASE_URL, json=payload)
    print(f"{event_type} -> {response.status_code}: {response.json()}")
    return response

def get_conversation(conv_id):
    url = f"http://localhost:8000/conversations/{conv_id}/"
    response = requests.get(url)
    print(f"GET /conversations/{conv_id}/ -> {response.status_code}")
    print(response.json())
    return response

def list_conversations():
    url = "http://localhost:8000/conversations/"
    response = requests.get(url)
    print(f"GET /conversations/ -> {response.status_code}")
    print(response.json())
    return response

def main():
    print("\n📌 Criando nova conversa")
    post_event("NEW_CONVERSATION", {"id": CONVERSATION_ID})

    print("\n📌 Enviando mensagens INBOUND")
    for content in ["Oi,gostaria", "de comprar um gato","gato amarelo" ]:
        time.sleep(1)
        post_event("NEW_MESSAGE", {
            "id": str(uuid.uuid4()),
            "conversation_id": CONVERSATION_ID,
            "content": content
        })

    print("\n📌 Aguardando Celery processar OUTBOUND")
    time.sleep(10)

    print("\n📌 Consultando detalhes da conversa")
    get_conversation(CONVERSATION_ID)

    print("\n📌 Fechando conversa")
    post_event("CLOSE_CONVERSATION", {"id": CONVERSATION_ID})

    print("\n📌 Tentando mandar mensagem em conversa fechada (esperado: erro)")
    post_event("NEW_MESSAGE", {
        "id": str(uuid.uuid4()),
        "conversation_id": CONVERSATION_ID,
        "content": "Ainda está aí?"
    })

    print("\n📌 Testando evento desconhecido (esperado: erro)")
    post_event("UNKNOWN_EVENT", {"foo": "bar"})

    print("\n📌 Testando timestamp inválido (esperado: erro)")
    post_event("NEW_CONVERSATION", {"id": str(uuid.uuid4())}, timestamp="invalid-timestamp")

    print("\n📌 Listando todas as conversas")
    list_conversations()

if __name__ == "__main__":
    main()









