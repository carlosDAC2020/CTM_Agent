# api/consumers.py
import json
import httpx # Un cliente HTTP moderno y asíncrono. ¡Añádelo a requirements.txt!
from channels.generic.websocket import AsyncWebsocketConsumer

# El nombre del servicio de tu agente en docker-compose
AGENT_URL = "http://agent:8000"

class ChatConsumer(AsyncWebsocketConsumer):
    # Se llama cuando el frontend intenta conectar
    async def connect(self):
        # Extrae el 'thread_id' de la URL que definimos en routing.py
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'

        # Une este WebSocket a un "grupo" específico.
        # Esto nos permitirá enviar mensajes a este cliente desde cualquier parte de Django.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Acepta la conexión
        await self.accept()
        print(f"WebSocket conectado para el hilo: {self.thread_id}")

    # Se llama cuando la conexión se cierra
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket desconectado para el hilo: {self.thread_id}")

    # Se llama cuando Django recibe un mensaje desde el frontend (Angular)
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type') # ej: 'user_input', 'user_selection'
        payload = data.get('payload')   # ej: el texto del chat, la lista de índices [0, 1]

        print(f"Recibido desde el cliente ({self.thread_id}): {data}")

        # Aquí es donde orquestas la llamada al agente LangGraph.
        # Por ahora, es una lógica simple. Esto se volverá más complejo
        # para manejar los 'interrupts' y el streaming de eventos.
        
        # Ejemplo: reanudar una ejecución con el input del usuario
        # LangServe expone endpoints para actualizar un estado existente
        update_url = f"{AGENT_URL}/threads/{self.thread_id}/update"

        async with httpx.AsyncClient(timeout=None) as client:
            try:
                # El 'input' aquí es lo que el grafo espera para continuar
                # desde una interrupción.
                response = await client.post(update_url, json={"input": payload})
                response.raise_for_status()
                
                # La respuesta del agente puede ser un flujo de eventos.
                # Por simplicidad, aquí solo enviamos el resultado final.
                # En la versión final, procesarías el stream.
                agent_response = response.json()

                # Enviar la respuesta del agente de vuelta al frontend
                await self.send(text_data=json.dumps({
                    'type': 'agent_response',
                    'payload': agent_response
                }))

            except httpx.RequestError as e:
                # Manejar errores de conexión con el agente
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f"Error comunicándose con el agente: {e}"
                }))