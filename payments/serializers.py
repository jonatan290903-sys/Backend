from rest_framework import serializers
from .models import Pago
from accounts.serializers import EstudianteSerializer


class PagoSerializer(serializers.ModelSerializer):
    estudiante_info = EstudianteSerializer(source='estudiante', read_only=True)
    estudiante_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('accounts.models', fromlist=['Estudiante']).Estudiante.objects.all(),
        source='estudiante',
        write_only=True
    )
    dias_vencido = serializers.ReadOnlyField()

    class Meta:
        model = Pago
        fields = (
            'id', 'estudiante_info', 'estudiante_id', 'monto', 'concepto',
            'fecha_vencimiento', 'fecha_pago', 'estado', 'numero_comprobante',
            'metodo_pago', 'referencia_pago', 'notas', 'dias_vencido',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
