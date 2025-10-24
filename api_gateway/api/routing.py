# api/routing.py
from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    # Esta expresión regular captura un 'thread_id' alfanumérico de la URL
    # y lo pasa al Consumer.
    re_path(r'ws/chat/(?P<thread_id>\w+)/$', ChatConsumer.as_asgi()),
]