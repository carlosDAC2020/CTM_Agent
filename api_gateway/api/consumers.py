# api/consumers.py
import json
import httpx
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

from .models import Project # Importa tu modelo

AGENT_URL = "http://agent:8000"

# Wrapper para acceder a la BD de forma asíncrona desde el consumer
@sync_to_async
def get_project_data(thread_id, user):
    try:
        project = Project.objects.get(thread_id=thread_id, user_id=user.id)
        return {
            "title": project.title,
            "description": project.description,
        }
    except Project.DoesNotExist:
        return None

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'
        self.user = self.scope["user"] # Obtenido del AuthMiddlewareStack

        # --- Verificación de Seguridad ---
        project_data = await get_project_data(self.thread_id, self.user)
        if not project_data:
            # Si el proyecto no existe o no pertenece al usuario, rechaza la conexión
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # --- Iniciar la ejecución del agente al conectar ---
        await self.start_agent_run(project_data)

    async def start_agent_run(self, project_data):
        # Endpoint para iniciar un stream en un hilo existente
        stream_url = f"{AGENT_URL}/threads/{self.thread_id}/runs/stream"
        
        # El 'input' que espera tu primer nodo del grafo
        agent_input = {
            "project_title": project_data["title"],
            "project_description": project_data["description"],
            "document_paths": project_data.get("documents", [])
        }

        async with httpx.AsyncClient(timeout=None) as client:
            try:
                # Usamos un stream para recibir eventos en tiempo real
                async with client.stream("POST", stream_url, json={
                    "input": agent_input,
                    "assistant_id": "agent" # El ID de tu grafo/asistente
                }, headers={"Accept": "text/event-stream"}) as response:
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            # Procesa el evento SSE (Server-Sent Event)
                            event_data = json.loads(line[len("data:"):].strip())
                            # Retransmite el evento al frontend
                            await self.send(text_data=json.dumps(event_data))

            except httpx.RequestError as e:
                await self.send(text_data=json.dumps({'type': 'error', 'message': str(e)}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # Cuando el agente se interrumpe y el usuario responde
        data = json.loads(text_data)
        user_input = data.get('payload')

        # Reanudamos el stream pasándole el nuevo input
        stream_url = f"{AGENT_URL}/threads/{self.thread_id}/runs/stream"
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                async with client.stream("POST", stream_url, json={
                    "input": user_input, # El input del usuario para continuar
                    "assistant_id": "agent"
                }, headers={"Accept": "text/event-stream"}) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            event_data = json.loads(line[len("data:"):].strip())
                            await self.send(text_data=json.dumps(event_data))
            except httpx.RequestError as e:
                await self.send(text_data=json.dumps({'type': 'error', 'message': str(e)}))