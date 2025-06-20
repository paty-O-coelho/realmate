from django.urls import path
from .views import webhook, conversation_detail, conversation_list

urlpatterns = [
    path("webhook/", webhook, name="webhook"),
    path("conversations/", conversation_list, name="conversation_list"),
    path("conversations/<uuid:id>/", conversation_detail, name="conversation_detail"),
]
