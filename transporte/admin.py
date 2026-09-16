from django.contrib import admin
from .models import Vehiculo, Conductor, Viaje, CargaCombustible, Mantenimiento


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'modelo', 'capacidad_carga', 'kilometraje_actual', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('placa', 'modelo')


@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'numero_licencia', 'telefono', 'correo', 'fecha_creacion')
    search_fields = ('nombre_completo', 'numero_licencia', 'correo')


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehiculo', 'conductor', 'ciudad_origen', 'ciudad_destino', 'estado', 'fecha_hora_salida', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('ciudad_origen', 'ciudad_destino', 'vehiculo__placa', 'conductor__nombre_completo')
    raw_id_fields = ('vehiculo', 'conductor')


@admin.register(CargaCombustible)
class CargaCombustibleAdmin(admin.ModelAdmin):
    list_display = ('id', 'viaje', 'vehiculo', 'conductor', 'litros_cargados', 'costo_total', 'ciudad', 'fecha_carga')
    search_fields = ('ciudad', 'vehiculo__placa', 'conductor__nombre_completo')
    raw_id_fields = ('viaje', 'vehiculo', 'conductor')



@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehiculo', 'tipo_mantenimiento', 'taller_responsable', 'fecha_programada', 'costo', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'tipo_mantenimiento')
    search_fields = ('vehiculo__placa', 'taller_responsable', 'descripcion')
    raw_id_fields = ('vehiculo',)
