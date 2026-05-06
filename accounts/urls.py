from django.urls import path
from . import views

urlpatterns = [
    path('mis-materias/', views.mis_materias, name='mis-materias'),
    path('register/', views.register, name='auth-register'),
    path('login/', views.login, name='auth-login'),
    path('refresh/', views.refresh_token, name='auth-refresh'),
    path('logout/', views.logout, name='auth-logout'),
    path('profile/', views.get_profile, name='auth-profile'),
    path('profile/update/', views.update_profile, name='auth-profile-update'),
    path('profile/change-password/', views.change_password, name='auth-change-password'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    path('config/', views.system_config, name='system-config'),
    path('anios/', views.anios_list, name='anios-list'),
    path('anios/<int:pk>/', views.anio_detail, name='anio-detail'),

    path('cursos/', views.cursos_list, name='cursos-nivel-list'),
    path('cursos/<int:pk>/', views.curso_detail, name='cursos-nivel-detail'),

    path('estudiantes/', views.estudiantes_list, name='estudiantes-list'),
    path('estudiantes/<int:pk>/', views.estudiante_detail, name='estudiante-detail'),

    path('docentes/', views.docentes_list, name='docentes-list'),
    path('docentes/<int:pk>/', views.docente_detail, name='docente-detail'),
]
