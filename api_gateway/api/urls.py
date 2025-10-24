# api/urls.py
from django.urls import path
from .views import ProjectStartView, HealthCheckView

urlpatterns = [
    path('projects/start/', ProjectStartView.as_view(), name='project-start'),
    path('', HealthCheckView.as_view(), name='health-check'),
]