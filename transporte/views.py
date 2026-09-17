from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.conf import settings
import os
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone

from .models import Vehiculo, Conductor, Viaje, CargaCombustible, Mantenimiento, Incidente, Viatico
from .forms import VehiculoForm, ConductorForm, ViajeForm, CargaCombustibleForm, MantenimientoForm, IncidenteForm, ViaticoForm
from .decorators import admin_required, conductor_required, is_admin_user, is_conductor_user



# ──────────────────────────────────────────────
# AUTENTICACIÓN Y ENRUTAMIENTO RAIZ
# ──────────────────────────────────────────────

def login_view(request):
    """
    Vista de inicio de sesión con Django Authentication nativo.
    Redirige según el rol:
    - ADMINISTRADOR -> /dashboard/
    - CONDUCTOR -> /mis-viajes/
    """
    if request.user.is_authenticated:
        if is_admin_user(request.user):
            return redirect('dashboard')
        elif is_conductor_user(request.user):
            return redirect('mis_viajes')
        return redirect('dashboard')

    error_message = None
    error_type = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                error_message = 'Su cuenta se encuentra inactiva. Contacte al administrador.'
                error_type = 'inactive_account'
            else:
                login(request, user)
                if is_admin_user(user):
                    return redirect('dashboard')
                elif is_conductor_user(user):
                    return redirect('mis_viajes')
                return redirect('dashboard')
        else:
            error_message = 'Credenciales inválidas. Verifique su usuario y contraseña.'
            error_type = 'auth_error'

    return render(request, 'auth/login.html', {
        'error_message': error_message,
        'error_type': error_type,
    })


def logout_view(request):
    """Cierra la sesión del usuario y redirige al login."""
    logout(request)
    return redirect('login')


def root_view(request):
    """Redirección inicial según estado de autenticación y rol."""
    if not request.user.is_authenticated:
        return redirect('login')
    if is_admin_user(request.user):
        return redirect('dashboard')
    elif is_conductor_user(request.user):
        return redirect('mis_viajes')
    return redirect('login')


# ──────────────────────────────────────────────
# DASHBOARD (ADMINISTRADOR)
# ──────────────────────────────────────────────

@admin_required
def dashboard(request):
    total_vehiculos = Vehiculo.objects.count()
    total_conductores = Conductor.objects.count()
    total_viajes = Viaje.objects.count()
    total_combustible = CargaCombustible.objects.count()
    total_mantenimientos = Mantenimiento.objects.count()
    mantenimientos_activos = Mantenimiento.objects.filter(estado__in=['Programado', 'En Proceso']).count()
    total_inversion_mantenimiento = Mantenimiento.objects.aggregate(total=Sum('costo'))['total'] or 0

    vehiculos_recientes = Vehiculo.objects.all()[:5]
    viajes_recientes = Viaje.objects.select_related('vehiculo', 'conductor', 'usuario_conductor').all()[:5]
    mantenimientos_recientes = Mantenimiento.objects.select_related('vehiculo').all()[:5]

    return render(request, 'Dashboard/dashboard.html', {
        'total_vehiculos': total_vehiculos,
        'total_conductores': total_conductores,
        'total_viajes': total_viajes,
        'total_combustible': total_combustible,
        'total_mantenimientos': total_mantenimientos,
        'mantenimientos_activos': mantenimientos_activos,
        'total_inversion_mantenimiento': total_inversion_mantenimiento,
        'vehiculos_recientes': vehiculos_recientes,
        'viajes_recientes': viajes_recientes,
        'mantenimientos_recientes': mantenimientos_recientes,
    })


# ──────────────────────────────────────────────
# VEHICULOS (ADMINISTRADOR)
# ──────────────────────────────────────────────

@admin_required
def vehiculos_lista(request):
    vehiculos = Vehiculo.objects.all()
    total_vehiculos = vehiculos.count()
    disponibles = vehiculos.filter(estado='Disponible').count()
    en_viaje = vehiculos.filter(estado='En viaje').count()
    en_mantenimiento = vehiculos.filter(estado='Mantenimiento').count()

    pct_disponibles = round((disponibles / total_vehiculos * 100), 1) if total_vehiculos > 0 else 0
    pct_en_viaje = round((en_viaje / total_vehiculos * 100), 1) if total_vehiculos > 0 else 0
    pct_mantenimiento = round((en_mantenimiento / total_vehiculos * 100), 1) if total_vehiculos > 0 else 0

    return render(request, 'Vehiculos/gestion_vehiculo.html', {
        'vehiculos': vehiculos,
        'total_vehiculos': total_vehiculos,
        'disponibles': disponibles,
        'en_viaje': en_viaje,
        'en_mantenimiento': en_mantenimiento,
        'pct_disponibles': pct_disponibles,
        'pct_en_viaje': pct_en_viaje,
        'pct_mantenimiento': pct_mantenimiento,
    })


@admin_required
def vehiculo_crear(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, f"Vehículo con placa {vehiculo.placa} registrado correctamente.")
            return redirect('vehiculos_lista')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario de vehículo.")
    else:
        form = VehiculoForm()
    return render(request, 'Vehiculos/registrar_vehiculo.html', {'form': form})


@admin_required
def vehiculo_detalle(request, id):
    vehiculo = get_object_or_404(Vehiculo, pk=id)
    viajes = Viaje.objects.filter(vehiculo=vehiculo).select_related('conductor').order_by('-fecha_hora_salida')
    mantenimientos = Mantenimiento.objects.filter(vehiculo=vehiculo).order_by('-fecha_programada')
    cargas_combustible = CargaCombustible.objects.filter(vehiculo=vehiculo).select_related('conductor', 'viaje').order_by('-fecha_carga')
    incidentes = Incidente.objects.filter(viaje__vehiculo=vehiculo).select_related('viaje', 'viaje__conductor').order_by('-fecha_incidente')

    total_viajes = viajes.count()
    viajes_finalizados = viajes.filter(estado='Finalizado').count()
    viajes_en_curso = viajes.filter(estado='En curso').count()
    
    total_km = sum(
        (v.kilometraje_final - v.kilometraje_inicial)
        for v in viajes
        if v.kilometraje_final and v.kilometraje_final > v.kilometraje_inicial
    )
    
    costo_mantenimiento_total = mantenimientos.aggregate(total=Sum('costo'))['total'] or 0
    costo_combustible_total = cargas_combustible.aggregate(total=Sum('costo_total'))['total'] or 0
    total_litros = cargas_combustible.aggregate(total=Sum('litros_cargados'))['total'] or 0

    return render(request, 'Vehiculos/detalle.html', {
        'vehiculo': vehiculo,
        'viajes': viajes,
        'mantenimientos': mantenimientos,
        'cargas_combustible': cargas_combustible,
        'incidentes': incidentes,
        'total_viajes': total_viajes,
        'viajes_finalizados': viajes_finalizados,
        'viajes_en_curso': viajes_en_curso,
        'total_km': total_km,
        'costo_mantenimiento_total': costo_mantenimiento_total,
        'costo_combustible_total': costo_combustible_total,
        'total_litros': total_litros,
    })


@admin_required
def vehiculo_cambiar_estado(request, id):
    """Permite al administrador cambiar el estado operativo del vehículo (Disponible, En viaje, Mantenimiento)."""
    vehiculo = get_object_or_404(Vehiculo, pk=id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Vehiculo.ESTADO_CHOICES):
            vehiculo.estado = nuevo_estado
            vehiculo.save()
            messages.success(request, f"Estado del vehículo {vehiculo.placa} actualizado a '{nuevo_estado}'.")
        else:
            messages.error(request, "Estado de vehículo no válido.")
    return redirect(request.META.get('HTTP_REFERER') or 'vehiculo_detalle', id=vehiculo.id)


@admin_required
def mantenimiento_cambiar_estado(request, id):
    """Permite al administrador cambiar el estado de un mantenimiento (Programado, En Proceso, Finalizado)."""
    mantenimiento = get_object_or_404(Mantenimiento, pk=id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Mantenimiento.ESTADO_CHOICES):
            mantenimiento.estado = nuevo_estado
            if nuevo_estado == 'Finalizado' and not mantenimiento.fecha_realizada:
                mantenimiento.fecha_realizada = timezone.now().date()
            mantenimiento.save()
            messages.success(request, f"Mantenimiento MNT-{mantenimiento.id} actualizado a '{nuevo_estado}'.")
        else:
            messages.error(request, "Estado de mantenimiento no válido.")
    return redirect(request.META.get('HTTP_REFERER') or 'mantenimiento_lista')




# ──────────────────────────────────────────────
# CONDUCTORES (ADMINISTRADOR)
# ──────────────────────────────────────────────

@admin_required
def conductores_lista(request):
    conductores = Conductor.objects.all()
    total_conductores = conductores.count()
    
    # Conductores actualmente en ruta (con viajes en curso)
    conductores_en_ruta_ids = Viaje.objects.filter(estado='En curso').values_list('conductor_id', flat=True).distinct()
    activos_en_ruta = len(set(conductores_en_ruta_ids))
    disponibles = max(0, total_conductores - activos_en_ruta)
    
    pct_en_ruta = round((activos_en_ruta / total_conductores * 100), 1) if total_conductores > 0 else 0

    return render(request, 'Conductores/gestion_conductores.html', {
        'conductores': conductores,
        'total_conductores': total_conductores,
        'activos_en_ruta': activos_en_ruta,
        'disponibles': disponibles,
        'pct_en_ruta': pct_en_ruta,
    })


@admin_required
def conductor_crear(request):
    if request.method == 'POST':
        form = ConductorForm(request.POST)
        if form.is_valid():
            conductor = form.save()
            messages.success(request, f"Conductor {conductor.nombre_completo} registrado correctamente.")
            return redirect('conductores_lista')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario de conductor.")
    else:
        form = ConductorForm()
    return render(request, 'Conductores/registrar_conductor.html', {'form': form})


@admin_required
def conductor_detalle(request, id):
    conductor = get_object_or_404(Conductor, pk=id)
    viajes_relacionados = Viaje.objects.filter(conductor=conductor).select_related('vehiculo')
    return render(request, 'Conductores/detal_conductor.html', {
        'conductor': conductor,
        'viajes_relacionados': viajes_relacionados,
    })


# ──────────────────────────────────────────────
# VIAJES (ADMINISTRADOR)
# ──────────────────────────────────────────────

@admin_required
def viajes_lista(request):
    viajes = Viaje.objects.select_related('vehiculo', 'conductor', 'usuario_conductor').all()
    total_viajes = viajes.count()
    viajes_en_curso = viajes.filter(estado='En curso').count()
    viajes_programados = viajes.filter(estado='Programado').count()
    viajes_finalizados = viajes.filter(estado='Finalizado').count()

    return render(request, 'Viajes/gestion_viaje.html', {
        'viajes': viajes,
        'total_viajes': total_viajes,
        'viajes_en_curso': viajes_en_curso,
        'viajes_programados': viajes_programados,
        'viajes_finalizados': viajes_finalizados,
    })


@admin_required
def viaje_crear(request):
    if request.method == 'POST':
        form = ViajeForm(request.POST)
        if form.is_valid():
            viaje = form.save()
            
            # Sincronización automática de estado del vehículo
            vehiculo = viaje.vehiculo
            if viaje.estado == 'En curso':
                vehiculo.estado = 'En viaje'
                vehiculo.save()
            elif viaje.estado == 'Finalizado':
                vehiculo.estado = 'Disponible'
                if viaje.kilometraje_final and viaje.kilometraje_final > vehiculo.kilometraje_actual:
                    vehiculo.kilometraje_actual = viaje.kilometraje_final
                vehiculo.save()

            messages.success(request, f"Viaje VJ-{viaje.id:05d} programado exitosamente.")
            return redirect('viajes_lista')
        else:
            messages.error(request, "No se pudo registrar el viaje. Verifique los campos marcados.")
    else:
        form = ViajeForm()
    
    vehiculos = Vehiculo.objects.all()
    conductores = Conductor.objects.all()
    return render(request, 'Viajes/registro_viaje.html', {
        'form': form,
        'vehiculos': vehiculos,
        'conductores': conductores,
    })


@admin_required
def viaje_detalle(request, id):
    viaje = get_object_or_404(Viaje, pk=id)
    return redirect('viajes_lista')


# ──────────────────────────────────────────────
# MIS VIAJES (CONDUCTOR)
# ──────────────────────────────────────────────

@conductor_required
def mis_viajes(request):
    """
    Muestra únicamente los viajes asociados al usuario conductor autenticado.
    """
    viajes = Viaje.objects.filter(usuario_conductor=request.user).select_related('vehiculo', 'conductor')
    return render(request, 'Viajes/mis_viajes.html', {
        'viajes': viajes,
    })


# ──────────────────────────────────────────────
# COMBUSTIBLE (ADMINISTRADOR Y CONDUCTOR)
# ──────────────────────────────────────────────

@admin_required
def combustible_lista(request):
    """Listado general de combustible exclusivo para administradores."""
    cargas = CargaCombustible.objects.select_related('viaje', 'vehiculo', 'conductor').all()
    
    totales = cargas.aggregate(
        total_litros=Sum('litros_cargados'),
        total_costo=Sum('costo_total'),
        total_cargas=Count('id')
    )
    total_litros = totales['total_litros'] or 0
    total_costo = totales['total_costo'] or 0
    total_cargas = totales['total_cargas'] or 0
    promedio_litros = round(total_litros / total_cargas, 2) if total_cargas > 0 else 0

    return render(request, 'Combustible/listad_comb.html', {
        'cargas': cargas,
        'total_litros': total_litros,
        'total_costo': total_costo,
        'total_cargas': total_cargas,
        'promedio_litros': promedio_litros,
    })


@login_required
def combustible_crear(request):
    """
    Registro de combustible.
    - Si es Conductor: Solo puede seleccionar y registrar combustible para sus propios viajes.
    - Si es Administrador: Puede registrar para cualquier viaje.
    """
    user = request.user
    is_admin = is_admin_user(user)

    if is_admin:
        viajes = Viaje.objects.select_related('vehiculo', 'conductor').all()
        vehiculos = Vehiculo.objects.all()
        conductores = Conductor.objects.all()
    else:
        # Conductor: solo sus viajes asignados
        viajes = Viaje.objects.filter(usuario_conductor=user).select_related('vehiculo', 'conductor')
        vehiculos = Vehiculo.objects.filter(viajes__in=viajes).distinct()
        conductores = Conductor.objects.filter(viajes__in=viajes).distinct()

    error_msg = None

    if request.method == 'POST':
        form = CargaCombustibleForm(request.POST, request.FILES)
        if form.is_valid():
            carga = form.save(commit=False)
            
            # Validación backend de seguridad para conductores
            if not is_admin:
                if carga.viaje.usuario_conductor != user:
                    return HttpResponseForbidden("Acceso denegado: No puede registrar combustible para viajes de otros conductores.")
                # Asegurar vehículo y conductor del viaje
                carga.vehiculo = carga.viaje.vehiculo
                carga.conductor = carga.viaje.conductor

            carga.save()
            messages.success(request, f"Carga de {carga.litros_cargados}L registrada exitosamente.")
            
            if is_admin:
                return redirect('combustible_lista')
            else:
                return redirect('combustible_detalle', id=carga.id)
        else:
            error_msg = "Por favor verifique los datos del formulario de combustible."
            messages.error(request, error_msg)
    else:
        form = CargaCombustibleForm()

    return render(request, 'Combustible/registro_comb.html', {
        'form': form,
        'viajes': viajes,
        'vehiculos': vehiculos,
        'conductores': conductores,
        'error_msg': error_msg,
    })


@login_required
def combustible_detalle(request, id):
    """
    Detalle de carga de combustible.
    - Administrador: Puede ver cualquier carga y validarla/rechazarla.
    - Conductor: Únicamente puede ver cargas pertenecientes a sus propios viajes.
    """
    carga = get_object_or_404(CargaCombustible.objects.select_related('viaje', 'vehiculo', 'conductor'), pk=id)
    
    if not is_admin_user(request.user):
        if carga.viaje.usuario_conductor != request.user:
            return HttpResponseForbidden("Acceso denegado: No tiene permisos para consultar este registro de combustible.")

    return render(request, 'Combustible/detal_comb.html', {
        'carga': carga,
        'is_admin': is_admin_user(request.user),
    })


@admin_required
def combustible_cambiar_estado(request, id):
    """Acción del administrador para aprobar o rechazar una carga de combustible."""
    carga = get_object_or_404(CargaCombustible, pk=id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(CargaCombustible.ESTADO_CHOICES):
            carga.estado = nuevo_estado
            carga.observacion_admin = request.POST.get('observacion_admin', '').strip()
            carga.fecha_validacion = timezone.now()
            carga.save()
            messages.success(request, f"Carga de combustible #{carga.id} actualizada a '{nuevo_estado}'.")
        else:
            messages.error(request, "Estado no válido.")
    return redirect(request.META.get('HTTP_REFERER') or 'combustible_lista')



# ──────────────────────────────────────────────
# MANTENIMIENTO (HU-008) (ADMINISTRADOR)
# ──────────────────────────────────────────────

@admin_required
def mantenimiento_lista(request):
    """Lista de todos los mantenimientos de la flota."""
    mantenimientos = Mantenimiento.objects.select_related('vehiculo').all()

    # KPIs
    total_activos = mantenimientos.filter(estado__in=['Programado', 'En Proceso']).count()
    total_programados = mantenimientos.filter(estado='Programado').count()
    total_en_proceso = mantenimientos.filter(estado='En Proceso').count()
    total_finalizados = mantenimientos.filter(estado='Finalizado').count()
    inversion_total = mantenimientos.aggregate(total=Sum('costo'))['total'] or 0
    total_registros = mantenimientos.count()

    return render(request, 'Mantenimientos/lista.html', {
        'mantenimientos': mantenimientos,
        'total_activos': total_activos,
        'total_programados': total_programados,
        'total_en_proceso': total_en_proceso,
        'total_finalizados': total_finalizados,
        'inversion_total': inversion_total,
        'total_registros': total_registros,
    })


@admin_required
def mantenimiento_crear(request):
    """Registro de un nuevo mantenimiento."""
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            mantenimiento = form.save()
            
            # Sincronización de estado del vehículo
            vehiculo = mantenimiento.vehiculo
            if mantenimiento.estado == 'En Proceso':
                vehiculo.estado = 'Mantenimiento'
                vehiculo.save()
            elif mantenimiento.estado == 'Finalizado':
                if not vehiculo.viajes.filter(estado='En curso').exists():
                    vehiculo.estado = 'Disponible'
                    vehiculo.save()

            messages.success(request, f"Mantenimiento MNT-{mantenimiento.id:04d} programado correctamente.")
            return redirect('mantenimiento_lista')
        else:
            messages.error(request, "Por favor verifique los campos del mantenimiento.")
    else:
        form = MantenimientoForm()
    
    vehiculos = Vehiculo.objects.all()
    return render(request, 'Mantenimientos/crear.html', {
        'form': form,
        'vehiculos': vehiculos,
    })


@admin_required
def mantenimiento_detalle(request, id):
    """Detalle de un mantenimiento."""
    mantenimiento = get_object_or_404(Mantenimiento.objects.select_related('vehiculo'), pk=id)
    return render(request, 'Mantenimientos/detalle.html', {
        'mantenimiento': mantenimiento,
    })


# ──────────────────────────────────────────────
# REPORTES (HU-009, HU-010) (ADMINISTRADOR)
# ──────────────────────────────────────────────

@admin_required
def reportes_index(request):
    """Centro de reportes: índice principal."""
    total_viajes = Viaje.objects.count()
    total_vehiculos = Vehiculo.objects.count()
    total_conductores = Conductor.objects.count()
    total_mantenimientos = Mantenimiento.objects.count()

    # KPIs rápidos
    viajes_finalizados = Viaje.objects.filter(estado='Finalizado').count()
    viajes_en_curso = Viaje.objects.filter(estado='En curso').count()
    total_combustible_litros = CargaCombustible.objects.aggregate(
        total=Sum('litros_cargados'))['total'] or 0
    total_combustible_costo = CargaCombustible.objects.aggregate(
        total=Sum('costo_total'))['total'] or 0
    total_inversion_mantenimiento = Mantenimiento.objects.aggregate(
        total=Sum('costo'))['total'] or 0

    return render(request, 'Reportes/index.html', {
        'total_viajes': total_viajes,
        'total_vehiculos': total_vehiculos,
        'total_conductores': total_conductores,
        'total_mantenimientos': total_mantenimientos,
        'viajes_finalizados': viajes_finalizados,
        'viajes_en_curso': viajes_en_curso,
        'total_combustible_litros': total_combustible_litros,
        'total_combustible_costo': total_combustible_costo,
        'total_inversion_mantenimiento': total_inversion_mantenimiento,
    })


@admin_required
def reporte_consumo(request):
    """HU-009: Reporte de consumo de combustible por vehículo."""
    consumo_por_vehiculo = (
        CargaCombustible.objects
        .values('vehiculo__placa', 'vehiculo__modelo')
        .annotate(
            total_litros=Sum('litros_cargados'),
            total_costo=Sum('costo_total'),
            total_cargas=Count('id'),
        )
        .order_by('-total_litros')
    )

    totales = CargaCombustible.objects.aggregate(
        total_litros=Sum('litros_cargados'),
        total_costo=Sum('costo_total'),
        total_registros=Count('id'),
    )
    total_litros = totales['total_litros'] or 0
    total_costo = totales['total_costo'] or 0
    total_registros = totales['total_registros'] or 0

    num_vehiculos = consumo_por_vehiculo.count()
    promedio_litros = round(total_litros / num_vehiculos, 2) if num_vehiculos > 0 else 0

    max_litros = consumo_por_vehiculo.first()['total_litros'] if consumo_por_vehiculo.exists() else 1

    consumo_lista = []
    for item in consumo_por_vehiculo:
        pct = round((item['total_litros'] / max_litros) * 100, 2) if max_litros else 0
        consumo_lista.append({**item, 'pct_barra': pct})

    return render(request, 'Reportes/consumo.html', {
        'consumo_por_vehiculo': consumo_lista,
        'total_litros': total_litros,
        'total_costo': total_costo,
        'total_registros': total_registros,
        'promedio_litros': promedio_litros,
        'num_vehiculos': num_vehiculos,
    })


@admin_required
def reporte_operacional(request):
    """HU-010: Reporte operacional de viajes."""
    viajes = Viaje.objects.select_related('vehiculo', 'conductor').all()

    total_viajes = viajes.count()
    viajes_finalizados = viajes.filter(estado='Finalizado').count()
    viajes_en_curso = viajes.filter(estado='En curso').count()
    viajes_programados = viajes.filter(estado='Programado').count()

    km_recorridos = sum(
        (v.kilometraje_final - v.kilometraje_inicial)
        for v in viajes
        if v.kilometraje_final and v.kilometraje_final > v.kilometraje_inicial
    )

    viajes_por_conductor = (
        Viaje.objects
        .values('conductor__nombre_completo')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )

    viajes_por_vehiculo = (
        Viaje.objects
        .values('vehiculo__placa', 'vehiculo__modelo')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )

    viajes_recientes = viajes.order_by('-fecha_creacion')[:10]

    return render(request, 'Reportes/operacional.html', {
        'total_viajes': total_viajes,
        'viajes_finalizados': viajes_finalizados,
        'viajes_en_curso': viajes_en_curso,
        'viajes_programados': viajes_programados,
        'km_recorridos': km_recorridos,
        'viajes_por_conductor': viajes_por_conductor,
        'viajes_por_vehiculo': viajes_por_vehiculo,
        'viajes_recientes': viajes_recientes,
    })


# ──────────────────────────────────────────────
# INCIDENTES (CONDUCTOR)
# ──────────────────────────────────────────────

@conductor_required
def mis_incidentes(request):
    """
    Lista los incidentes de los viajes asignados al conductor autenticado.
    """
    viajes_conductor = Viaje.objects.filter(usuario_conductor=request.user)
    incidentes = Incidente.objects.filter(viaje__in=viajes_conductor).select_related('viaje')

    total = incidentes.count()
    pendientes = incidentes.filter(estado__in=['Reportado', 'En Revisión']).count()
    resueltos = incidentes.filter(estado='Resuelto').count()
    tasa_resolucion = round((resueltos / total) * 100) if total > 0 else 0

    return render(request, 'Incidentes/lista.html', {
        'incidentes': incidentes,
        'total': total,
        'pendientes': pendientes,
        'resueltos': resueltos,
        'tasa_resolucion': tasa_resolucion,
    })


@conductor_required
def incidente_reportar(request):
    """
    Permite al conductor reportar un nuevo incidente en uno de sus viajes asignados.
    """
    viajes = Viaje.objects.filter(usuario_conductor=request.user).select_related('vehiculo')

    if request.method == 'POST':
        form = IncidenteForm(request.POST, request.FILES)
        if form.is_valid():
            incidente = form.save(commit=False)
            # Validación de seguridad: el viaje debe pertenecer al conductor
            if incidente.viaje not in viajes:
                return HttpResponseForbidden('No tiene permiso para reportar incidentes en ese viaje.')
            incidente.save()
            messages.success(request, f'Incidente INC-{incidente.id:04d} reportado exitosamente.')
            return redirect('mis_incidentes')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = IncidenteForm()

    # Limitar el queryset del campo viaje al conductor actual
    form.fields['viaje'].queryset = viajes

    return render(request, 'Incidentes/reportar.html', {
        'form': form,
        'viajes': viajes,
    })


@conductor_required
def incidente_detalle(request, id):
    """
    Muestra el detalle de un incidente. Sólo accesible si el viaje pertenece al conductor.
    """
    incidente = get_object_or_404(Incidente.objects.select_related('viaje', 'viaje__vehiculo', 'viaje__conductor'), pk=id)
    if incidente.viaje.usuario_conductor != request.user:
        return HttpResponseForbidden('No tiene permiso para ver este incidente.')

    return render(request, 'Incidentes/detalle.html', {
        'incidente': incidente,
    })


# ──────────────────────────────────────────────
# VIÁTICOS (CONDUCTOR)
# ──────────────────────────────────────────────

@conductor_required
def mis_viaticos(request):
    """
    Lista los viáticos registrados por el conductor autenticado.
    """
    viajes_conductor = Viaje.objects.filter(usuario_conductor=request.user)
    viaticos = Viatico.objects.filter(viaje__in=viajes_conductor).select_related('viaje', 'conductor')

    total = viaticos.count()
    total_monto = viaticos.aggregate(total=Sum('monto'))['total'] or 0
    pendiente_reembolso = viaticos.filter(estado__in=['En validación', 'Aprobado']).aggregate(total=Sum('monto'))['total'] or 0
    aprobados = viaticos.filter(estado='Aprobado').count()
    en_validacion = viaticos.filter(estado='En validación').count()

    return render(request, 'Viaticos/lista.html', {
        'viaticos': viaticos,
        'total': total,
        'total_monto': total_monto,
        'pendiente_reembolso': pendiente_reembolso,
        'aprobados': aprobados,
        'en_validacion': en_validacion,
    })


@conductor_required
def viatico_crear(request):
    """
    Permite al conductor registrar un nuevo viático en uno de sus viajes.
    """
    viajes = Viaje.objects.filter(usuario_conductor=request.user).select_related('vehiculo')

    if request.method == 'POST':
        form = ViaticoForm(request.POST, request.FILES)
        if form.is_valid():
            viatico = form.save(commit=False)
            if viatico.viaje not in viajes:
                return HttpResponseForbidden('No tiene permiso para registrar viáticos en ese viaje.')
            # Asignar el conductor del viaje automáticamente
            viatico.conductor = viatico.viaje.conductor
            viatico.save()
            messages.success(request, f'Viático VTC-{viatico.id:04d} registrado exitosamente.')
            return redirect('mis_viaticos')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ViaticoForm()

    form.fields['viaje'].queryset = viajes

    return render(request, 'Viaticos/crear.html', {
        'form': form,
        'viajes': viajes,
    })


@conductor_required
def viatico_detalle(request, id):
    """
    Muestra el detalle de un viático. Sólo accesible si el viaje pertenece al conductor.
    """
    viatico = get_object_or_404(Viatico.objects.select_related('viaje', 'conductor', 'viaje__vehiculo'), pk=id)
    if viatico.viaje.usuario_conductor != request.user:
        return HttpResponseForbidden('No tiene permiso para ver este viático.')

    return render(request, 'Viaticos/detalle.html', {
        'viatico': viatico,
    })


# ──────────────────────────────────────────────
# INCIDENTES (ADMINISTRADOR)
# ──────────────────────────────────────────────

@admin_required
def incidentes_admin(request):
    """
    Panel de administración para gestión, auditoría y resolución de incidentes.
    """
    incidentes = Incidente.objects.select_related('viaje', 'viaje__vehiculo', 'viaje__conductor').all()

    estado_filtro = request.GET.get('estado', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip()
    conductor_filtro = request.GET.get('conductor', '').strip()
    q = request.GET.get('q', '').strip()

    if estado_filtro:
        incidentes = incidentes.filter(estado=estado_filtro)
    if tipo_filtro:
        incidentes = incidentes.filter(tipo_incidente=tipo_filtro)
    if conductor_filtro:
        incidentes = incidentes.filter(viaje__conductor_id=conductor_filtro)
    if q:
        incidentes = incidentes.filter(
            Q(lugar__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(viaje__vehiculo__placa__icontains=q) |
            Q(viaje__conductor__nombre_completo__icontains=q)
        )

    all_incidentes = Incidente.objects.all()
    total_incidentes = all_incidentes.count()
    pendientes = all_incidentes.filter(estado='Reportado').count()
    en_revision = all_incidentes.filter(estado='En Revisión').count()
    resueltos = all_incidentes.filter(estado='Resuelto').count()
    rechazados = all_incidentes.filter(estado='Rechazado').count()

    conductores = Conductor.objects.all()

    return render(request, 'Incidentes/admin.html', {
        'incidentes': incidentes,
        'total_incidentes': total_incidentes,
        'pendientes': pendientes,
        'en_revision': en_revision,
        'resueltos': resueltos,
        'rechazados': rechazados,
        'conductores': conductores,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
        'conductor_filtro': conductor_filtro,
        'q': q,
        'tipo_choices': Incidente.TIPO_CHOICES,
        'estado_choices': Incidente.ESTADO_CHOICES,
    })


@admin_required
def incidente_cambiar_estado(request, id):
    """Acción del administrador para cambiar estado de un incidente (Revisión, Resuelto, Rechazado)."""
    incidente = get_object_or_404(Incidente, pk=id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Incidente.ESTADO_CHOICES):
            incidente.estado = nuevo_estado
            incidente.respuesta_admin = request.POST.get('respuesta_admin', '').strip()
            if nuevo_estado in ['Resuelto', 'Rechazado']:
                incidente.fecha_resolucion = timezone.now()
            incidente.save()
            messages.success(request, f"Incidente INC-{incidente.id:04d} actualizado a '{nuevo_estado}'.")
        else:
            messages.error(request, "Estado no válido.")
    return redirect(request.META.get('HTTP_REFERER') or 'incidentes_admin')


# ──────────────────────────────────────────────
# VIÁTICOS (ADMINISTRADOR)
# ──────────────────────────────────────────────

@admin_required
def viaticos_admin(request):
    """
    Panel financiero de auditoría, aprobación y reembolso de viáticos.
    """
    viaticos = Viatico.objects.select_related('conductor', 'viaje', 'viaje__vehiculo').all()

    estado_filtro = request.GET.get('estado', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip()
    conductor_filtro = request.GET.get('conductor', '').strip()
    q = request.GET.get('q', '').strip()

    if estado_filtro:
        viaticos = viaticos.filter(estado=estado_filtro)
    if tipo_filtro:
        viaticos = viaticos.filter(tipo_gasto=tipo_filtro)
    if conductor_filtro:
        viaticos = viaticos.filter(conductor_id=conductor_filtro)
    if q:
        viaticos = viaticos.filter(
            Q(descripcion__icontains=q) |
            Q(conductor__nombre_completo__icontains=q) |
            Q(viaje__vehiculo__placa__icontains=q)
        )

    all_viaticos = Viatico.objects.all()
    total_viaticos = all_viaticos.count()
    monto_total = all_viaticos.aggregate(total=Sum('monto'))['total'] or 0
    monto_aprobado = all_viaticos.filter(estado__in=['Aprobado', 'Reembolsado']).aggregate(total=Sum('monto'))['total'] or 0
    monto_pendiente = all_viaticos.filter(estado='En validación').aggregate(total=Sum('monto'))['total'] or 0

    pendientes_count = all_viaticos.filter(estado='En validación').count()
    aprobados_count = all_viaticos.filter(estado='Aprobado').count()
    reembolsados_count = all_viaticos.filter(estado='Reembolsado').count()
    rechazados_count = all_viaticos.filter(estado='Rechazado').count()

    conductores = Conductor.objects.all()

    return render(request, 'Viaticos/admin.html', {
        'viaticos': viaticos,
        'total_viaticos': total_viaticos,
        'monto_total': monto_total,
        'monto_aprobado': monto_aprobado,
        'monto_pendiente': monto_pendiente,
        'pendientes_count': pendientes_count,
        'aprobados_count': aprobados_count,
        'reembolsados_count': reembolsados_count,
        'rechazados_count': rechazados_count,
        'conductores': conductores,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
        'conductor_filtro': conductor_filtro,
        'q': q,
        'tipo_choices': Viatico.TIPO_GASTO_CHOICES,
        'estado_choices': Viatico.ESTADO_CHOICES,
    })


@admin_required
def viatico_cambiar_estado(request, id):
    """Acción del administrador para aprobar, rechazar o reembolsar un viático."""
    viatico = get_object_or_404(Viatico, pk=id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Viatico.ESTADO_CHOICES):
            viatico.estado = nuevo_estado
            viatico.observacion_admin = request.POST.get('observacion_admin', '').strip()
            viatico.fecha_validacion = timezone.now()
            viatico.save()
            messages.success(request, f"Viático VTC-{viatico.id:04d} actualizado a '{nuevo_estado}'.")
        else:
            messages.error(request, "Estado no válido.")
    return redirect(request.META.get('HTTP_REFERER') or 'viaticos_admin')


# ──────────────────────────────────────────────
# PWA (PROGRESSIVE WEB APP)
# ──────────────────────────────────────────────

def offline_view(request):
    """Página fallback cuando el usuario o conductor pierde la conexión."""
    return render(request, 'offline.html')


def manifest_view(request):
    """Sirve el manifest.json con el MIME type correcto para PWA."""
    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/manifest+json')
    return HttpResponse('{}', content_type='application/manifest+json')


def service_worker_view(request):
    """Sirve el Service Worker sw.js con scope root (/) y header Service-Worker-Allowed."""
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
    if os.path.exists(sw_path):
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
        response = HttpResponse(content, content_type='application/javascript')
        response['Service-Worker-Allowed'] = '/'
        return response
    return HttpResponse('', content_type='application/javascript')

