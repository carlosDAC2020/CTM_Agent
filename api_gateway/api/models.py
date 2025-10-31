# api/models.py
from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    # Si se borra el usuario, se borran sus proyectos.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')

    # Guardamos el título y la descripción
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # El ID de LangGraph para este proyecto
    thread_id = models.CharField(max_length=100, unique=True, blank=True)
    
    # Fecha de creación
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"