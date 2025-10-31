# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),

    # Rutas para el manejo de usuarios
    path('user/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('user/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('test/', views.HomeView.as_view(), name='home'),
]