from django.urls import path
from . import views

urlpatterns = [
    # Inicio y Autenticación
    path('', views.root_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard Administrativo
    path('dashboard/', views.dashboard, name='dashboard'),

    # Mis Viajes (Conductor)
    path('mis-viajes/', views.mis_viajes, name='mis_viajes'),

    # Vehículos (Administrador)
    path('vehiculos/', views.vehiculos_lista, name='vehiculos_lista'),
    path('vehiculos/crear/', views.vehiculo_crear, name='vehiculo_crear'),
    path('vehiculos/<int:id>/', views.vehiculo_detalle, name='vehiculo_detalle'),

    # Conductores (Administrador)
    path('conductores/', views.conductores_lista, name='conductores_lista'),
    path('conductores/crear/', views.conductor_crear, name='conductor_crear'),
    path('conductores/<int:id>/', views.conductor_detalle, name='conductor_detalle'),

    # Viajes (Administrador)
    path('viajes/', views.viajes_lista, name='viajes_lista'),
    path('viajes/crear/', views.viaje_crear, name='viaje_crear'),
    path('viajes/<int:id>/', views.viaje_detalle, name='viaje_detalle'),

    # Combustible
    path('combustible/', views.combustible_lista, name='combustible_lista'),
    path('combustible/crear/', views.combustible_crear, name='combustible_crear'),
    path('combustible/<int:id>/', views.combustible_detalle, name='combustible_detalle'),

    # Mantenimiento (HU-008) - Administrador
    path('mantenimientos/', views.mantenimiento_lista, name='mantenimiento_lista'),
    path('mantenimientos/crear/', views.mantenimiento_crear, name='mantenimiento_crear'),
    path('mantenimientos/<int:id>/', views.mantenimiento_detalle, name='mantenimiento_detalle'),

    # Reportes (HU-009, HU-010) - Administrador
    path('reportes/', views.reportes_index, name='reportes_index'),
    path('reportes/consumo/', views.reporte_consumo, name='reporte_consumo'),
    path('reportes/operacional/', views.reporte_operacional, name='reporte_operacional'),
]
