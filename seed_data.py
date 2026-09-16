import os
import django
from decimal import Decimal
from datetime import datetime, date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from transporte.models import Vehiculo, Conductor, Viaje, CargaCombustible, Mantenimiento

def run_seed():
    print("Iniciando población de datos para LogiCarga...")

    # 1. Crear Grupos
    admin_group, _ = Group.objects.get_or_create(name='ADMINISTRADOR')
    conductor_group, _ = Group.objects.get_or_create(name='CONDUCTOR')

    # 2. Crear / Actualizar Administrador Principal
    admin_user, created = User.objects.get_or_create(username='admin', defaults={
        'first_name': 'Carlos',
        'last_name': 'Guzmán Vega',
        'email': 'admin@logicarga.com',
        'is_staff': True,
        'is_superuser': True,
    })
    admin_user.set_password('Admin1234!')
    admin_user.first_name = 'Carlos'
    admin_user.last_name = 'Guzmán Vega'
    admin_user.email = 'admin@logicarga.com'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    admin_user.groups.add(admin_group)
    print("✓ Administrador configurado: admin / Admin1234!")

    # 3. Datos de los 10 Camioneros / Conductores
    conductores_data = [
        {
            'username': 'conductor1',
            'password': 'Conductor123!',
            'first_name': 'Carlos Alberto',
            'last_name': 'Mendoza Rincón',
            'licencia': 'LIC-8829104-C3',
            'telefono': '+57 310 482 9104',
            'correo': 'carlos.mendoza@logicarga.com',
        },
        {
            'username': 'conductor2',
            'password': 'Conductor123!',
            'first_name': 'Jorge Eduardo',
            'last_name': 'Ramírez Ortiz',
            'licencia': 'LIC-7740192-C3',
            'telefono': '+57 312 774 0192',
            'correo': 'jorge.ramirez@logicarga.com',
        },
        {
            'username': 'conductor3',
            'password': 'Conductor123!',
            'first_name': 'Andrés Felipe',
            'last_name': 'Castro Pardo',
            'licencia': 'LIC-9018234-C3',
            'telefono': '+57 315 901 8234',
            'correo': 'andres.castro@logicarga.com',
        },
        {
            'username': 'conductor4',
            'password': 'Conductor123!',
            'first_name': 'Miguel Ángel',
            'last_name': 'Torres Salgado',
            'licencia': 'LIC-6523819-C3',
            'telefono': '+57 320 652 3819',
            'correo': 'miguel.torres@logicarga.com',
        },
        {
            'username': 'conductor5',
            'password': 'Conductor123!',
            'first_name': 'Diego Fernando',
            'last_name': 'Morales Gil',
            'licencia': 'LIC-5419082-C2',
            'telefono': '+57 318 541 9082',
            'correo': 'diego.morales@logicarga.com',
        },
        {
            'username': 'conductor6',
            'password': 'Conductor123!',
            'first_name': 'Álvaro José',
            'last_name': 'Gómez Beltrán',
            'licencia': 'LIC-4392018-C3',
            'telefono': '+57 311 439 2018',
            'correo': 'alvaro.gomez@logicarga.com',
        },
        {
            'username': 'conductor7',
            'password': 'Conductor123!',
            'first_name': 'Felipe Esteban',
            'last_name': 'Herrera Marín',
            'licencia': 'LIC-3281904-C3',
            'telefono': '+57 314 328 1904',
            'correo': 'felipe.herrera@logicarga.com',
        },
        {
            'username': 'conductor8',
            'password': 'Conductor123!',
            'first_name': 'Ricardo Alfonso',
            'last_name': 'Silva Caicedo',
            'licencia': 'LIC-2170938-C2',
            'telefono': '+57 317 217 0938',
            'correo': 'ricardo.silva@logicarga.com',
        },
        {
            'username': 'conductor9',
            'password': 'Conductor123!',
            'first_name': 'Gustavo Adolfo',
            'last_name': 'Vargas Osorio',
            'licencia': 'LIC-1069827-C3',
            'telefono': '+57 321 106 9827',
            'correo': 'gustavo.vargas@logicarga.com',
        },
        {
            'username': 'conductor10',
            'password': 'Conductor123!',
            'first_name': 'Julián Darío',
            'last_name': 'Martínez Lozano',
            'licencia': 'LIC-9958716-C3',
            'telefono': '+57 301 995 8716',
            'correo': 'julian.martinez@logicarga.com',
        },
    ]

    conductor_objs = []
    user_driver_map = {}

    for item in conductores_data:
        # Crear User
        u, _ = User.objects.get_or_create(username=item['username'], defaults={
            'first_name': item['first_name'],
            'last_name': item['last_name'],
            'email': item['correo'],
        })
        u.first_name = item['first_name']
        u.last_name = item['last_name']
        u.email = item['correo']
        u.set_password(item['password'])
        u.save()
        u.groups.add(conductor_group)

        # Crear o Actualizar Conductor
        c, _ = Conductor.objects.get_or_create(numero_licencia=item['licencia'], defaults={
            'nombre_completo': f"{item['first_name']} {item['last_name']}",
            'telefono': item['telefono'],
            'correo': item['correo'],
        })
        c.nombre_completo = f"{item['first_name']} {item['last_name']}"
        c.telefono = item['telefono']
        c.correo = item['correo']
        c.save()

        conductor_objs.append(c)
        user_driver_map[item['username']] = (u, c)

    print(f"✓ {len(conductor_objs)} Conductores y usuarios creados.")

    # 4. Crear Flota de Vehículos
    vehiculos_data = [
        {'placa': 'WCO-812', 'modelo': 'Volvo FH 540 Tractomula 6x4', 'capacidad_carga': Decimal('34000.00'), 'kilometraje_actual': 142850, 'estado': 'En viaje'},
        {'placa': 'SZL-492', 'modelo': 'Scania R450 Streamline 6x2', 'capacidad_carga': Decimal('32000.00'), 'kilometraje_actual': 189400, 'estado': 'En viaje'},
        {'placa': 'TLM-731', 'modelo': 'Kenworth T680 Next Gen', 'capacidad_carga': Decimal('35000.00'), 'kilometraje_actual': 95300, 'estado': 'Disponible'},
        {'placa': 'KJR-204', 'modelo': 'International LT 625 Diamond', 'capacidad_carga': Decimal('32500.00'), 'kilometraje_actual': 210450, 'estado': 'En viaje'},
        {'placa': 'FGN-618', 'modelo': 'Freightliner Cascadia Evolution', 'capacidad_carga': Decimal('33000.00'), 'kilometraje_actual': 167200, 'estado': 'Mantenimiento'},
        {'placa': 'BVM-935', 'modelo': 'Mercedes-Benz Actros 2645', 'capacidad_carga': Decimal('31000.00'), 'kilometraje_actual': 118600, 'estado': 'En viaje'},
        {'placa': 'HQX-147', 'modelo': 'Mack Anthem 70" Stand-Up Sleeper', 'capacidad_carga': Decimal('34500.00'), 'kilometraje_actual': 84100, 'estado': 'Disponible'},
        {'placa': 'UPR-583', 'modelo': 'Volvo FMX 460 Volqueta Dobletroque', 'capacidad_carga': Decimal('28000.00'), 'kilometraje_actual': 234100, 'estado': 'Mantenimiento'},
        {'placa': 'XNT-826', 'modelo': 'Scania G410 Rígido Pesado', 'capacidad_carga': Decimal('26000.00'), 'kilometraje_actual': 156800, 'estado': 'Disponible'},
        {'placa': 'DKZ-359', 'modelo': 'Kenworth T800 Classic Heavy Haul', 'capacidad_carga': Decimal('36000.00'), 'kilometraje_actual': 298400, 'estado': 'Disponible'},
        {'placa': 'JTW-470', 'modelo': 'Hino 700 Series Chasis Corto', 'capacidad_carga': Decimal('22000.00'), 'kilometraje_actual': 134200, 'estado': 'Disponible'},
        {'placa': 'VRL-915', 'modelo': 'Chevrolet FVR Forward Camión', 'capacidad_carga': Decimal('18000.00'), 'kilometraje_actual': 112000, 'estado': 'Disponible'},
    ]

    vehiculo_objs = []
    for vdata in vehiculos_data:
        v, _ = Vehiculo.objects.get_or_create(placa=vdata['placa'], defaults=vdata)
        for key, val in vdata.items():
            setattr(v, key, val)
        v.save()
        vehiculo_objs.append(v)

    print(f"✓ {len(vehiculo_objs)} Vehículos registrados.")

    # 5. Crear Viajes
    now = timezone.now()
    viajes_data = [
        {
            'vehiculo': vehiculo_objs[0], # WCO-812
            'conductor_user': 'conductor1',
            'ciudad_origen': 'Bogotá D.C.',
            'ciudad_destino': 'Medellín (Antioquia)',
            'salida': now - timedelta(hours=6),
            'llegada': None,
            'tipo_carga': 'Electrodomésticos y Paquetería Pesada',
            'km_ini': 142400,
            'km_fin': None,
            'comb_ini': Decimal('380.00'),
            'comb_fin': None,
            'estado': 'En curso',
        },
        {
            'vehiculo': vehiculo_objs[1], # SZL-492
            'conductor_user': 'conductor2',
            'ciudad_origen': 'Cali (Valle del Cauca)',
            'ciudad_destino': 'Buenaventura (Puerto Marítimo)',
            'salida': now - timedelta(hours=4),
            'llegada': None,
            'tipo_carga': 'Contenedor Refrigerado 40ft (Exportación)',
            'km_ini': 189250,
            'km_fin': None,
            'comb_ini': Decimal('320.00'),
            'comb_fin': None,
            'estado': 'En curso',
        },
        {
            'vehiculo': vehiculo_objs[3], # KJR-204
            'conductor_user': 'conductor3',
            'ciudad_origen': 'Barranquilla (Atlántico)',
            'ciudad_destino': 'Cartagena (Bolívar)',
            'salida': now - timedelta(hours=2),
            'llegada': None,
            'tipo_carga': 'Materiales de Construcción a Granel',
            'km_ini': 210330,
            'km_fin': None,
            'comb_ini': Decimal('290.00'),
            'comb_fin': None,
            'estado': 'En curso',
        },
        {
            'vehiculo': vehiculo_objs[5], # BVM-935
            'conductor_user': 'conductor4',
            'ciudad_origen': 'Bucaramanga (Santander)',
            'ciudad_destino': 'Cúcuta (Norte de Santander)',
            'salida': now - timedelta(hours=5),
            'llegada': None,
            'tipo_carga': 'Insumos Industriales y Químicos',
            'km_ini': 118400,
            'km_fin': None,
            'comb_ini': Decimal('310.00'),
            'comb_fin': None,
            'estado': 'En curso',
        },
        {
            'vehiculo': vehiculo_objs[2], # TLM-731
            'conductor_user': 'conductor5',
            'ciudad_origen': 'Bogotá D.C.',
            'ciudad_destino': 'Villavicencio (Meta)',
            'salida': now + timedelta(hours=14),
            'llegada': None,
            'tipo_carga': 'Maquinaria Agrícola y Repuestos',
            'km_ini': 95300,
            'km_fin': None,
            'comb_ini': Decimal('350.00'),
            'comb_fin': None,
            'estado': 'Programado',
        },
        {
            'vehiculo': vehiculo_objs[6], # HQX-147
            'conductor_user': 'conductor6',
            'ciudad_origen': 'Medellín (Antioquia)',
            'ciudad_destino': 'Manizales (Caldas)',
            'salida': now + timedelta(hours=20),
            'llegada': None,
            'tipo_carga': 'Carga Seca de Alimentos Procesados',
            'km_ini': 84100,
            'km_fin': None,
            'comb_ini': Decimal('300.00'),
            'comb_fin': None,
            'estado': 'Programado',
        },
        {
            'vehiculo': vehiculo_objs[8], # XNT-826
            'conductor_user': 'conductor7',
            'ciudad_origen': 'Pereira (Risaralda)',
            'ciudad_destino': 'Armenia (Quindío)',
            'salida': now + timedelta(days=1, hours=8),
            'llegada': None,
            'tipo_carga': 'Café Pergamino Especial Exportación',
            'km_ini': 156800,
            'km_fin': None,
            'comb_ini': Decimal('280.00'),
            'comb_fin': None,
            'estado': 'Programado',
        },
        {
            'vehiculo': vehiculo_objs[9], # DKZ-359
            'conductor_user': 'conductor8',
            'ciudad_origen': 'Santa Marta (Magdalena)',
            'ciudad_destino': 'Bogotá D.C.',
            'salida': now - timedelta(days=3),
            'llegada': now - timedelta(days=1, hours=4),
            'tipo_carga': 'Carbón Térmico y Minerales',
            'km_ini': 297450,
            'km_fin': 298400,
            'comb_ini': Decimal('420.00'),
            'comb_fin': Decimal('85.00'),
            'estado': 'Finalizado',
        },
        {
            'vehiculo': vehiculo_objs[10], # JTW-470
            'conductor_user': 'conductor9',
            'ciudad_origen': 'Ibagué (Tolima)',
            'ciudad_destino': 'Neiva (Huila)',
            'salida': now - timedelta(days=2),
            'llegada': now - timedelta(days=1, hours=10),
            'tipo_carga': 'Arroz Empacado y Harinas',
            'km_ini': 133980,
            'km_fin': 134200,
            'comb_ini': Decimal('220.00'),
            'comb_fin': Decimal('90.00'),
            'estado': 'Finalizado',
        },
        {
            'vehiculo': vehiculo_objs[11], # VRL-915
            'conductor_user': 'conductor10',
            'ciudad_origen': 'Pasto (Nariño)',
            'ciudad_destino': 'Popayán (Cauca)',
            'salida': now - timedelta(days=4),
            'llegada': now - timedelta(days=3, hours=2),
            'tipo_carga': 'Productos Lácteos Refrigerados',
            'km_ini': 111750,
            'km_fin': 112000,
            'comb_ini': Decimal('190.00'),
            'comb_fin': Decimal('60.00'),
            'estado': 'Finalizado',
        },
        {
            'vehiculo': vehiculo_objs[0], # WCO-812
            'conductor_user': 'conductor1',
            'ciudad_origen': 'Medellín (Antioquia)',
            'ciudad_destino': 'Bogotá D.C.',
            'salida': now - timedelta(days=5),
            'llegada': now - timedelta(days=4, hours=6),
            'tipo_carga': 'Textiles y Confecciones',
            'km_ini': 141950,
            'km_fin': 142400,
            'comb_ini': Decimal('400.00'),
            'comb_fin': Decimal('75.00'),
            'estado': 'Finalizado',
        },
        {
            'vehiculo': vehiculo_objs[1], # SZL-492
            'conductor_user': 'conductor2',
            'ciudad_origen': 'Buenaventura (Puerto)',
            'ciudad_destino': 'Cali (Valle)',
            'salida': now - timedelta(days=6),
            'llegada': now - timedelta(days=5, hours=12),
            'tipo_carga': 'Materias Primas de Importación',
            'km_ini': 189100,
            'km_fin': 189250,
            'comb_ini': Decimal('310.00'),
            'comb_fin': Decimal('120.00'),
            'estado': 'Finalizado',
        },
    ]

    viaje_objs = []
    for vdata in viajes_data:
        u, c = user_driver_map[vdata['conductor_user']]
        viaje, _ = Viaje.objects.get_or_create(
            vehiculo=vdata['vehiculo'],
            conductor=c,
            ciudad_origen=vdata['ciudad_origen'],
            ciudad_destino=vdata['ciudad_destino'],
            fecha_hora_salida=vdata['salida'],
            defaults={
                'usuario_conductor': u,
                'fecha_hora_llegada': vdata['llegada'],
                'tipo_carga': vdata['tipo_carga'],
                'kilometraje_inicial': vdata['km_ini'],
                'kilometraje_final': vdata['km_fin'],
                'combustible_inicial': vdata['comb_ini'],
                'combustible_final': vdata['comb_fin'],
                'estado': vdata['estado'],
            }
        )
        viaje.usuario_conductor = u
        viaje.fecha_hora_llegada = vdata['llegada']
        viaje.tipo_carga = vdata['tipo_carga']
        viaje.kilometraje_inicial = vdata['km_ini']
        viaje.kilometraje_final = vdata['km_fin']
        viaje.combustible_inicial = vdata['comb_ini']
        viaje.combustible_final = vdata['comb_fin']
        viaje.estado = vdata['estado']
        viaje.save()
        viaje_objs.append(viaje)

    print(f"✓ {len(viaje_objs)} Viajes generados con conductores asignados.")

    # 6. Crear Cargas de Combustible
    combustible_data = [
        {'viaje': viaje_objs[0], 'litros': Decimal('165.50'), 'costo': Decimal('1620000.00'), 'ciudad': 'La Dorada (Caldas)', 'fecha': date.today() - timedelta(days=1)},
        {'viaje': viaje_objs[1], 'litros': Decimal('140.00'), 'costo': Decimal('1372000.00'), 'ciudad': 'Dagua (Valle)', 'fecha': date.today()},
        {'viaje': viaje_objs[2], 'litros': Decimal('95.20'), 'costo': Decimal('933000.00'), 'ciudad': 'Barranquilla (EDS Cordialidad)', 'fecha': date.today()},
        {'viaje': viaje_objs[3], 'litros': Decimal('120.00'), 'costo': Decimal('1176000.00'), 'ciudad': 'Pamplona (Norte de Santander)', 'fecha': date.today() - timedelta(days=1)},
        {'viaje': viaje_objs[7], 'litros': Decimal('280.00'), 'costo': Decimal('2744000.00'), 'ciudad': 'Aguachica (Cesar)', 'fecha': date.today() - timedelta(days=2)},
        {'viaje': viaje_objs[8], 'litros': Decimal('110.00'), 'costo': Decimal('1078000.00'), 'ciudad': 'El Espinal (Tolima)', 'fecha': date.today() - timedelta(days=2)},
        {'viaje': viaje_objs[9], 'litros': Decimal('90.00'), 'costo': Decimal('882000.00'), 'ciudad': 'El Bordo (Cauca)', 'fecha': date.today() - timedelta(days=3)},
        {'viaje': viaje_objs[10], 'litros': Decimal('180.00'), 'costo': Decimal('1764000.00'), 'ciudad': 'Guaduas (Cundinamarca)', 'fecha': date.today() - timedelta(days=4)},
    ]

    for cdata in combustible_data:
        v = cdata['viaje']
        CargaCombustible.objects.get_or_create(
            viaje=v,
            vehiculo=v.vehiculo,
            conductor=v.conductor,
            fecha_carga=cdata['fecha'],
            defaults={
                'litros_cargados': cdata['litros'],
                'costo_total': cdata['costo'],
                'ciudad': cdata['ciudad'],
            }
        )

    print("✓ Cargas de combustible registradas.")

    # 7. Crear Mantenimientos
    mantenimientos_data = [
        {
            'vehiculo': vehiculo_objs[4], # FGN-618
            'tipo': 'Preventivo',
            'taller': 'Taller Central LogiCarga - Fontibón Bogotá D.C.',
            'fecha_prog': date.today() - timedelta(days=2),
            'fecha_real': None,
            'desc': 'Overhaul completo del sistema de frenos neumáticos, cambio de pastillas y calibración de zapatas en los 3 ejes.',
            'costo': Decimal('2850000.00'),
            'estado': 'En Proceso',
        },
        {
            'vehiculo': vehiculo_objs[7], # UPR-583
            'tipo': 'Correctivo',
            'taller': 'Serviteca & Inyección Diésel del Valle - Cali',
            'fecha_prog': date.today() - timedelta(days=1),
            'fecha_real': None,
            'desc': 'Reparación de bomba de inyección common rail e intercambio de dos inyectores Bosch de alta presión.',
            'costo': Decimal('4320000.00'),
            'estado': 'En Proceso',
        },
        {
            'vehiculo': vehiculo_objs[2], # TLM-731
            'tipo': 'Preventivo',
            'taller': 'Taller Kenworth Autorizado - Medellín Autopista Sur',
            'fecha_prog': date.today() + timedelta(days=5),
            'fecha_real': None,
            'desc': 'Mantenimiento preventivo de los 100.000 km: cambio de aceite sintético 15W40, filtros de combustible y aire primario.',
            'costo': Decimal('1450000.00'),
            'estado': 'Programado',
        },
        {
            'vehiculo': vehiculo_objs[6], # Mack Anthem
            'tipo': 'Predictivo',
            'taller': 'Centro de Diagnóstico Telemático Mack - Bogotá',
            'fecha_prog': date.today() + timedelta(days=8),
            'fecha_real': None,
            'desc': 'Análisis espectrométrico de aceite de motor y transmisión; escaneo electrónico del tren motriz mDRIVE.',
            'costo': Decimal('890000.00'),
            'estado': 'Programado',
        },
        {
            'vehiculo': vehiculo_objs[0], # Volvo FH 540
            'tipo': 'Preventivo',
            'taller': 'Taller Central LogiCarga - Fontibón Bogotá D.C.',
            'fecha_prog': date.today() - timedelta(days=25),
            'fecha_real': date.today() - timedelta(days=24),
            'desc': 'Alineación láser de ejes direccionales y traseros, balanceo dinámico de rines de aluminio y rotación de llantas Michelin.',
            'costo': Decimal('1120000.00'),
            'estado': 'Finalizado',
        },
        {
            'vehiculo': vehiculo_objs[1], # Scania R450
            'tipo': 'Preventivo',
            'taller': 'Scania Colombia S.A.S. - Centro de Servicio Yumbo',
            'fecha_prog': date.today() - timedelta(days=40),
            'fecha_real': date.today() - timedelta(days=39),
            'desc': 'Cambio preventivo de embrague automatizado Opticruise y purga del sistema hidráulico del retardador.',
            'costo': Decimal('5600000.00'),
            'estado': 'Finalizado',
        },
    ]

    for mdata in mantenimientos_data:
        Mantenimiento.objects.get_or_create(
            vehiculo=mdata['vehiculo'],
            taller_responsable=mdata['taller'],
            fecha_programada=mdata['fecha_prog'],
            defaults={
                'tipo_mantenimiento': mdata['tipo'],
                'fecha_realizada': mdata['fecha_real'],
                'descripcion': mdata['desc'],
                'costo': mdata['costo'],
                'estado': mdata['estado'],
            }
        )

    print("✓ Mantenimientos registrados.")
    print("✓ Población de datos completada exitosamente.")

if __name__ == '__main__':
    run_seed()
