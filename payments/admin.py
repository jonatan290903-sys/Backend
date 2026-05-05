from django.contrib import admin
from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'concepto', 'monto', 'fecha_vencimiento', 'estado')
    list_filter = ('estado', 'concepto')
    search_fields = ('estudiante__user__first_name', 'estudiante__user__last_name', 'numero_comprobante')
    date_hierarchy = 'fecha_vencimiento'
