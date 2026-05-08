from rest_framework import serializers
from .models import Comunicado, Notificacion

class ComunicadoSerializer(serializers.ModelSerializer):
    autor_name = serializers.CharField(source='autor.get_full_name', read_only=True)

    class Meta:
        model = Comunicado
        fields = '__all__'

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'
