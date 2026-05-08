from django.urls import path
from . import views

urlpatterns = [
    path('comunicados/', views.comunicados_list, name='comunicados-list'),
    path('notificaciones/', views.notificaciones_list, name='notificaciones-list'),
]
