from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project


class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo User.
    Maneja la creación y actualización de usuarios de forma segura.
    """
    class Meta:
        model = User
        # Campos que se expondrán en la API
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        
        # Configuración extra para el campo 'password'
        extra_kwargs = {
            'password': {
                'write_only': True,  # La contraseña solo se usa para escribir (crear/actualizar), nunca se devuelve.
                'style': {'input_type': 'password'} # Para que se muestre como un campo de contraseña en la UI de DRF.
            }
        }

    def create(self, validated_data):
        """
        Sobrescribe el método 'create' para hashear la contraseña.
        """
        # Usamos create_user para asegurarnos de que la contraseña se guarde
        # hasheada y no en texto plano.
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

    def update(self, instance, validated_data):
        """
        Sobrescribe el método 'update' para manejar la actualización de la contraseña.
        """
        # Si se proporciona una nueva contraseña, la hasheamos.
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        # Actualizamos el resto de los campos.
        return super().update(instance, validated_data)

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Project.
    """
    # Para mostrar el nombre de usuario en lugar del ID
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Project
        # Campos que se mostrarán en la API
        fields = ['id', 'user', 'thread_id', 'title', 'description', 'created_at']
        
        # Campos que el cliente no puede editar directamente
        # El 'user' y el 'thread_id' se asignarán automáticamente en la vista.
        read_only_fields = ['id', 'user', 'thread_id', 'created_at']