# api/views.py
import os
import boto3
import httpx
import uuid
from asgiref.sync import async_to_sync
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from botocore.client import Config
from botocore.exceptions import NoCredentialsError

from django.views.generic import TemplateView
from django.contrib.auth.models import User
from .models import Project
from .serializers import ProjectSerializer, UserSerializer

# --- CONFIGURACIÓN DE SERVICIOS ---
AGENT_URL = "http://agent:8000"
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ROOT_USER')
MINIO_SECRET_KEY = os.environ.get('MINIO_ROOT_PASSWORD')
MINIO_BUCKET_NAME = 'projects'

# --- CLIENTE S3 (MinIO) ---
s3_client = None
if MINIO_ENDPOINT and MINIO_ACCESS_KEY and MINIO_SECRET_KEY:
    s3_client = boto3.client('s3',
                             endpoint_url=f'http://{MINIO_ENDPOINT}',
                             aws_access_key_id=MINIO_ACCESS_KEY,
                             aws_secret_access_key=MINIO_SECRET_KEY,
                             config=Config(signature_version='s3v4'))

    # Asegurarse de que el bucket exista al iniciar
    try:
        s3_client.head_bucket(Bucket=MINIO_BUCKET_NAME)
    except Exception:
        s3_client.create_bucket(Bucket=MINIO_BUCKET_NAME)


class HomeView(TemplateView):
    template_name = "api/test.html"

# --- Excepción Personalizada para Errores del Agente ---
class AgentCommunicationError(APIException):
    status_code = 503  # Service Unavailable
    default_detail = 'El servicio del agente no está disponible o falló al procesar la solicitud.'
    default_code = 'agent_service_unavailable'

class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión completa (CRUD) de proyectos.
    Orquesta la subida de archivos y la creación de hilos en el agente.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Devuelve solo los proyectos del usuario autenticado."""
        return Project.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Este método síncrono orquesta todo el proceso de creación.
        Es llamado por DRF después de validar los datos del serializer.
        """
        # 1. Obtener los archivos de la petición
        files = self.request.FILES.getlist('documents')
        
        # 2. Subir archivos a una carpeta temporal en MinIO
        temp_folder_id, document_keys = self.upload_files_to_temp(files)

        # 3. Llamar a la lógica asíncrona para crear el hilo en el agente
        try:
            thread_id = async_to_sync(self.create_agent_thread)()
        except httpx.RequestError as e:
            # Si el agente falla, limpiamos los archivos temporales y lanzamos un error claro.
            self.cleanup_temp_files(temp_folder_id)
            raise AgentCommunicationError(f"Fallo al contactar al agente: {str(e)}") from e
        
        # 4. Si la creación del hilo fue exitosa, movemos los archivos a su ubicación final
        final_document_keys = self.move_files_to_final(temp_folder_id, thread_id, document_keys)

        # 5. Finalmente, guardamos el objeto en la base de datos con todos los datos
        #    Asignamos el usuario, el thread_id y las claves de los documentos.
        #    (Asegúrate de que tu modelo Project tenga un campo JSON para 'document_keys')
        serializer.save(
            user=self.request.user, 
            thread_id=thread_id
            # document_keys=final_document_keys  # Descomentar si tienes el campo en el modelo
        )

    # --- Métodos Auxiliares ---

    def upload_files_to_temp(self, files):
        """Sube archivos a una carpeta temporal en MinIO."""
        if not s3_client or not files:
            return None, []
        
        temp_folder_id = str(uuid.uuid4())
        document_keys = []
        for file in files:
            try:
                object_key = f"temp/{temp_folder_id}/{file.name}"
                s3_client.upload_fileobj(file, MINIO_BUCKET_NAME, object_key)
                document_keys.append({"bucket": MINIO_BUCKET_NAME, "key": object_key})
            except NoCredentialsError:
                raise APIException("Credenciales de MinIO no configuradas.", code=500)
        return temp_folder_id, document_keys

    def move_files_to_final(self, temp_folder_id, thread_id, document_keys):
        """Mueve archivos de la carpeta temporal a la carpeta final del thread."""
        if not s3_client or not temp_folder_id:
            return []

        final_keys = []
        for doc in document_keys:
            old_key = doc["key"]
            new_key = old_key.replace(f"temp/{temp_folder_id}", thread_id)
            
            s3_client.copy_object(
                Bucket=MINIO_BUCKET_NAME, 
                CopySource={'Bucket': MINIO_BUCKET_NAME, 'Key': old_key}, 
                Key=new_key
            )
            s3_client.delete_object(Bucket=MINIO_BUCKET_NAME, Key=old_key)
            final_keys.append({"bucket": MINIO_BUCKET_NAME, "key": new_key})
        return final_keys

    def cleanup_temp_files(self, temp_folder_id):
        """Elimina archivos de una carpeta temporal si algo sale mal."""
        if not s3_client or not temp_folder_id:
            return
        
        objects_to_delete = s3_client.list_objects_v2(
            Bucket=MINIO_BUCKET_NAME, 
            Prefix=f"temp/{temp_folder_id}/"
        )
        if 'Contents' in objects_to_delete:
            delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]}
            s3_client.delete_objects(Bucket=MINIO_BUCKET_NAME, Delete=delete_keys)

    async def create_agent_thread(self):
        """Método asíncrono que se comunica con la API de LangGraph."""
        create_thread_url = f"{AGENT_URL}/threads"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(create_thread_url, json={
                "metadata": {"user": self.request.user.username}
            })
            response.raise_for_status() # Lanza una excepción si la respuesta no es 2xx
            
            thread_data = response.json()
            thread_id = thread_data.get("thread_id")
            if not thread_id:
                raise httpx.RequestError("La API de LangGraph no devolvió un thread_id válido.")
            return thread_id

    

# --- VISTA 1: REGISTRO DE USUARIO (PÚBLICA) ---
class UserRegistrationView(generics.CreateAPIView):
    """
    Vista para que nuevos usuarios puedan registrarse.
    Accesible por cualquiera (AllowAny).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Permite el acceso sin autenticación


# --- VISTA 2: GESTIÓN DEL PERFIL PROPIO (AUTENTICADO) ---
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Vista para que un usuario vea y edite su propio perfil.
    Requiere que el usuario esté autenticado.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Devuelve el objeto del usuario que está haciendo la petición.
        """
        return self.request.user