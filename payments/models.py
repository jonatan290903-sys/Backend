from django.db import models
from django.utils import timezone
from accounts.models import Estudiante


class Pago(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
        ('parcial', 'Pago Parcial'),
        ('cancelado', 'Cancelado'),
    )

    CONCEPTO_CHOICES = (
        ('matricula', 'Matrícula'),
        ('pension', 'Pensión'),
        ('matricula_pension', 'Matrícula + Pensión'),
        ('actividades', 'Actividades Extras'),
        ('otros', 'Otros'),
    )

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=20, choices=CONCEPTO_CHOICES, db_index=True)
    fecha_vencimiento = models.DateField(db_index=True)
    fecha_pago = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', db_index=True)
    numero_comprobante = models.CharField(max_length=50, blank=True)
    metodo_pago = models.CharField(max_length=50, blank=True)
    referencia_pago = models.CharField(max_length=100, blank=True)
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_vencimiento']

    def __str__(self):
        return f"{self.estudiante} - ${self.monto} ({self.estado})"

    @property
    def dias_vencido(self):
        if self.estado == 'vencido':
            return (timezone.now().date() - self.fecha_vencimiento).days
        return 0
