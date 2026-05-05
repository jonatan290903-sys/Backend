from django.urls import path
from . import views

urlpatterns = [
    # Materias
    path('', views.materias_list, name='materias-list'),
    path('<int:pk>/', views.materia_detail, name='materia-detail'),
    path('<int:pk>/estudiantes/', views.materia_estudiantes, name='materia-estudiantes'),

    # Inscripciones (solo administrativo)
    path('inscripciones/', views.inscripciones_list, name='inscripciones-list'),
    path('inscripciones/<int:pk>/', views.inscripcion_detail, name='inscripcion-detail'),

# Actividades
    path('actividades/plantillas/', views.mis_plantillas, name='plantillas-list'),
    path('actividades/<int:pk>/', views.actividad_detail, name='actividad-detail'),
    path('<int:pk>/actividades/', views.materia_actividades, name='materia-actividades'),
    path('<int:pk>/actividades/<int:plantilla_pk>/usar-plantilla/', views.usar_plantilla, name='usar-plantilla'),
    path('<int:pk>/actividades/<int:pk2>/guardar-plantilla/', views.guardar_plantilla, name='guardar-plantilla'),

    # Notas
    path('notas/', views.guardar_nota, name='guardar-nota'),
    path('<int:pk>/centro-notas/', views.centro_notas, name='centro-notas'),

    # Asistencia
    path('<int:pk>/asistencia/', views.asistencia_materia, name='asistencia-materia'),
    path('<int:pk>/asistencia/bulk/', views.registrar_asistencia_bulk, name='asistencia-bulk'),
    path('<int:pk>/resumen-asistencia/', views.resumen_asistencia, name='resumen-asistencia'),
    path('<int:pk>/ultima-asistencia/', views.ultima_asistencia, name='ultima-asistencia'),

    # Horario
    path('horario/<int:curso_pk>/', views.horario_curso, name='horario-curso'),

    # Exportación Excel
    path('<int:pk>/asistencia/exportar/', views.exportar_asistencia, name='exportar-asistencia'),
    path('<int:pk>/notas/exportar/', views.exportar_notas, name='exportar-notas'),
]
