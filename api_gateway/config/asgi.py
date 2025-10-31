# config/asgi.py
import os
from django.core.asgi import get_asgi_application
from django.urls import path

# --- PASO 1: Establecer la variable de entorno ---
# Esto le dice a Django dónde encontrar tu archivo de configuración.
# DEBE estar antes de cualquier otra importación de Django.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# --- PASO 2: Inicializar la aplicación HTTP de Django ---
# Al llamar a esta función, Django carga sus settings.
django_asgi_app = get_asgi_application()

# --- PASO 3: Importar componentes de Channels DESPUÉS de la inicialización ---
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import api.routing # Ahora esta importación es segura

application = ProtocolTypeRouter({
    "http": django_asgi_app, # Usa la aplicación HTTP ya inicializada
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("api/", URLRouter(api.routing.websocket_urlpatterns))
        ])
    ),
})