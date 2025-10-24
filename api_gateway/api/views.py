# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import httpx
import uuid

AGENT_URL = "http://agent:8000"

class HealthCheckView(APIView):
    """
    Una vista de prueba extremadamente simple.
    Solo responde 'Hello, World!' para confirmar que la API está en línea.
    """
    def get(self, request, *args, **kwargs):
        """
        Maneja peticiones GET. No necesita datos, solo responde.
        """
        return Response(
            {"message": "Hello, World! The API Gateway is running!"}, 
            status=status.HTTP_200_OK
        )

class ProjectStartView(APIView):
    """
    Endpoint para iniciar una nueva ejecución de un proyecto en el agente.
    """
    async def post(self, request, *args, **kwargs):
        project_title = request.data.get("project_title")
        project_description = request.data.get("project_description")
        
        if not project_title or not project_description:
            return Response({"error": "project_title y project_description son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        # Generamos un ID único para este hilo de ejecución
        thread_id = str(uuid.uuid4())
        
        # El endpoint de LangServe para iniciar un nuevo stream/hilo
        start_url = f"{AGENT_URL}/invoke"

        try:
            # Hacemos la llamada inicial al agente para que comience su trabajo
            async with httpx.AsyncClient(timeout=30.0) as client:
                # El input debe coincidir con lo que espera tu nodo 'ingest_info'
                # y la configuración necesita el 'thread_id' para el checkpointer.
                response = await client.post(
                    start_url,
                    json={
                        "input": {"project_title": project_title, "project_description": project_description},
                        "config": {"configurable": {"thread_id": thread_id}}
                    }
                )
                response.raise_for_status()
        except httpx.RequestError as e:
            return Response({"error": f"No se pudo comunicar con el agente: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Devolvemos el ID para que el frontend pueda conectarse al WebSocket
        return Response({"thread_id": thread_id}, status=status.HTTP_201_CREATED)