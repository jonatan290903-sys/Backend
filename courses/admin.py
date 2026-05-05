from django.contrib import admin
from .models import Materia, Inscripcion, Actividad, Calificacion, Asistencia, HorarioCurso, PeriodoHorario, ClaseHorario


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'curso', 'docente', 'numero_horas', 'estado')
    list_filter = ('estado', 'curso')
    search_fields = ('nombre', 'codigo')


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'curso', 'estado', 'fecha_inscripcion', 'registrada_por')
    list_filter = ('estado', 'curso')
    search_fields = ('estudiante__user__first_name', 'estudiante__user__last_name')



@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'materia', 'tipo', 'ponderacion', 'es_plantilla', 'creada_por')
    list_filter = ('tipo', 'es_plantilla')
    search_fields = ('nombre',)


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'actividad', 'nota')
    search_fields = ('estudiante__user__first_name', 'actividad__nombre')


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'materia', 'fecha', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('estudiante__user__first_name',)


@admin.register(HorarioCurso)
class HorarioCursoAdmin(admin.ModelAdmin):
    list_display = ('curso', 'updated_at')


@admin.register(PeriodoHorario)
class PeriodoHorarioAdmin(admin.ModelAdmin):
    list_display = ('horario', 'orden', 'hora_inicio', 'hora_fin')


@admin.register(ClaseHorario)
class ClaseHorarioAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'dia', 'materia')
    list_filter = ('dia',)
