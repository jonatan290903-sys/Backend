from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagos_list, name='pagos-list'),
    path('<int:pk>/', views.pago_detail, name='pago-detail'),
    path('resumen/', views.resumen_pagos, name='pagos-resumen'),
]
