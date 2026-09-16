from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from transporte.models import Vehiculo, Conductor, Viaje, CargaCombustible, Mantenimiento
from transporte.forms import (
    VehiculoForm, ConductorForm, ViajeForm,
    CargaCombustibleForm, MantenimientoForm
)
from datetime import datetime, date, timedelta


class AuthAndRoleAccessTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Crear grupos
        self.grupo_admin = Group.objects.create(name='ADMINISTRADOR')
        self.grupo_conductor = Group.objects.create(name='CONDUCTOR')

        # 2. Crear usuarios
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            first_name='Carlos',
            last_name='Guzman',
            is_staff=True,
            is_superuser=True
        )
        self.admin.groups.add(self.grupo_admin)

        self.conductor1 = User.objects.create_user(
            username='conductor1',
            password='conductor123',
            first_name='Andres',
            last_name='Martinez'
        )
        self.conductor1.groups.add(self.grupo_conductor)

        self.conductor2 = User.objects.create_user(
            username='conductor2',
            password='conductor123',
            first_name='Pedro',
            last_name='Perez'
        )
        self.conductor2.groups.add(self.grupo_conductor)

        # 3. Modelos de apoyo
        self.vehiculo1 = Vehiculo.objects.create(
            placa='TRK-101',
            modelo='Volvo FH 540',
            capacidad_carga=30000,
            kilometraje_actual=10000,
            estado='Disponible'
        )
        self.cond_model = Conductor.objects.create(
            nombre_completo='Andres Martinez',
            numero_licencia='LIC-101',
            telefono='3001234567',
            correo='andres@logicarga.com'
        )
        self.viaje1 = Viaje.objects.create(
            vehiculo=self.vehiculo1,
            conductor=self.cond_model,
            usuario_conductor=self.conductor1,
            ciudad_origen='Bogota',
            ciudad_destino='Medellin',
            fecha_hora_salida=datetime(2026, 9, 20, 8, 0),
            tipo_carga='Alimentos',
            estado='Programado'
        )
        self.viaje2 = Viaje.objects.create(
            vehiculo=self.vehiculo1,
            conductor=self.cond_model,
            usuario_conductor=self.conductor2,
            ciudad_origen='Cali',
            ciudad_destino='Barranquilla',
            fecha_hora_salida=datetime(2026, 9, 21, 8, 0),
            tipo_carga='Textiles',
            estado='Programado'
        )

    # ──────────────────────────────────────────────
    # TESTS DE LOGIN Y REDIRECCIONES
    # ──────────────────────────────────────────────

    def test_login_admin_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_conductor_redirects_to_mis_viajes(self):
        response = self.client.post(reverse('login'), {
            'username': 'conductor1',
            'password': 'conductor123'
        })
        self.assertRedirects(response, reverse('mis_viajes'))

    def test_login_invalid_credentials_shows_error(self):
        response = self.client.post(reverse('login'), {
            'username': 'conductor1',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Credenciales')

    def test_root_redirects_unauthenticated_to_login(self):
        response = self.client.get(reverse('root'))
        self.assertRedirects(response, reverse('login'))

    def test_root_redirects_admin_to_dashboard(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('root'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_root_redirects_conductor_to_mis_viajes(self):
        self.client.login(username='conductor1', password='conductor123')
        response = self.client.get(reverse('root'))
        self.assertRedirects(response, reverse('mis_viajes'))

    def test_logout_redirects_to_login(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    # ──────────────────────────────────────────────
    # TESTS DE PERMISOS DE ADMINISTRADOR
    # ──────────────────────────────────────────────

    def test_admin_can_access_all_modules(self):
        self.client.login(username='admin', password='admin123')
        admin_urls = [
            reverse('dashboard'),
            reverse('vehiculos_lista'),
            reverse('vehiculo_crear'),
            reverse('vehiculo_detalle', kwargs={'id': self.vehiculo1.id}),
            reverse('conductores_lista'),
            reverse('conductor_crear'),
            reverse('conductor_detalle', kwargs={'id': self.cond_model.id}),
            reverse('viajes_lista'),
            reverse('viaje_crear'),
            reverse('combustible_lista'),
            reverse('combustible_crear'),
            reverse('mantenimiento_lista'),
            reverse('mantenimiento_crear'),
            reverse('reportes_index'),
            reverse('reporte_consumo'),
            reverse('reporte_operacional'),
        ]
        for url in admin_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    # ──────────────────────────────────────────────
    # TESTS DE PERMISOS DE CONDUCTOR
    # ──────────────────────────────────────────────

    def test_conductor_forbidden_from_admin_modules(self):
        self.client.login(username='conductor1', password='conductor123')
        restricted_urls = [
            reverse('dashboard'),
            reverse('vehiculos_lista'),
            reverse('vehiculo_crear'),
            reverse('vehiculo_detalle', kwargs={'id': self.vehiculo1.id}),
            reverse('conductores_lista'),
            reverse('conductor_crear'),
            reverse('conductor_detalle', kwargs={'id': self.cond_model.id}),
            reverse('viajes_lista'),
            reverse('viaje_crear'),
            reverse('combustible_lista'),
            reverse('mantenimiento_lista'),
            reverse('mantenimiento_crear'),
            reverse('reportes_index'),
            reverse('reporte_consumo'),
            reverse('reporte_operacional'),
        ]
        for url in restricted_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_conductor_can_access_mis_viajes_and_see_only_own_trips(self):
        self.client.login(username='conductor1', password='conductor123')
        response = self.client.get(reverse('mis_viajes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bogota')
        self.assertNotContains(response, 'Barranquilla')

    def test_conductor_fuel_creation_filtered_and_security(self):
        self.client.login(username='conductor1', password='conductor123')
        response = self.client.get(reverse('combustible_crear'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'VJ-{self.viaje1.id:05d}')
        self.assertNotContains(response, f'VJ-{self.viaje2.id:05d}')

        # POST for own trip should succeed
        post_response = self.client.post(reverse('combustible_crear'), {
            'viaje': self.viaje1.id,
            'vehiculo': self.vehiculo1.id,
            'conductor': self.cond_model.id,
            'litros_cargados': '150.50',
            'costo_total': '450000.00',
            'ciudad': 'La Dorada',
            'fecha_carga': date.today().isoformat()
        })
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(CargaCombustible.objects.filter(ciudad='La Dorada').exists())

        # POST trying to register fuel for another conductor's trip should be 403 Forbidden
        tamper_response = self.client.post(reverse('combustible_crear'), {
            'viaje': self.viaje2.id,
            'vehiculo': self.vehiculo1.id,
            'conductor': self.cond_model.id,
            'litros_cargados': '200.00',
            'costo_total': '600000.00',
            'ciudad': 'Buga',
            'fecha_carga': date.today().isoformat()
        })
        self.assertEqual(tamper_response.status_code, 403)

    # ──────────────────────────────────────────────
    # TESTS DE VALIDACIONES Y RESTRICCIONES RIGUROSAS
    # ──────────────────────────────────────────────

    def test_vehiculo_form_validations(self):
        # Negative mileage should fail
        form = VehiculoForm(data={
            'placa': 'XYZ-999',
            'modelo': 'FH 540',
            'capacidad_carga': 25000,
            'kilometraje_actual': -100,
            'estado': 'Disponible'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('kilometraje_actual', form.errors)

        # Negative capacity should fail
        form_neg_cap = VehiculoForm(data={
            'placa': 'XYZ-999',
            'modelo': 'FH 540',
            'capacidad_carga': -500,
            'kilometraje_actual': 1000,
            'estado': 'Disponible'
        })
        self.assertFalse(form_neg_cap.is_valid())
        self.assertIn('capacidad_carga', form_neg_cap.errors)

    def test_conductor_form_validations(self):
        # Duplicate license should fail
        form = ConductorForm(data={
            'nombre_completo': 'Otro Conductor',
            'numero_licencia': 'LIC-101',  # already used by cond_model
            'telefono': '3109876543',
            'correo': 'otro@logicarga.com'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('numero_licencia', form.errors)

    def test_viaje_form_origin_destination_restriction(self):
        # Same origin and destination should fail
        form = ViajeForm(data={
            'vehiculo': self.vehiculo1.id,
            'conductor': self.cond_model.id,
            'ciudad_origen': 'Bogota',
            'ciudad_destino': 'Bogota',
            'fecha_hora_salida': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
            'fecha_hora_llegada': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M'),
            'tipo_carga': 'Contenedor',
            'estado': 'Programado'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('ciudad_destino', form.errors)

    def test_viaje_arrival_before_departure_restriction(self):
        departure = datetime.now() + timedelta(days=2)
        arrival = datetime.now() + timedelta(days=1)
        form = ViajeForm(data={
            'vehiculo': self.vehiculo1.id,
            'conductor': self.cond_model.id,
            'ciudad_origen': 'Bogota',
            'ciudad_destino': 'Medellin',
            'fecha_hora_salida': departure.strftime('%Y-%m-%d %H:%M'),
            'fecha_hora_llegada': arrival.strftime('%Y-%m-%d %H:%M'),
            'tipo_carga': 'Contenedor',
            'estado': 'Programado'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_hora_llegada', form.errors)

    def test_carga_combustible_future_date_and_negatives_restriction(self):
        future_date = date.today() + timedelta(days=5)
        form = CargaCombustibleForm(data={
            'viaje': self.viaje1.id,
            'vehiculo': self.vehiculo1.id,
            'conductor': self.cond_model.id,
            'litros_cargados': -50,
            'costo_total': 100000,
            'ciudad': 'Bogota',
            'fecha_carga': future_date.isoformat()
        })
        self.assertFalse(form.is_valid())
        self.assertIn('litros_cargados', form.errors)
        self.assertIn('fecha_carga', form.errors)

    def test_mantenimiento_vehicle_status_synchronization(self):
        self.client.login(username='admin', password='admin123')
        veh = Vehiculo.objects.create(
            placa='MNT-888',
            modelo='Scania R450',
            capacidad_carga=28000,
            kilometraje_actual=50000,
            estado='Disponible'
        )
        response = self.client.post(reverse('mantenimiento_crear'), {
            'vehiculo': veh.id,
            'tipo_mantenimiento': 'Correctivo',
            'taller_responsable': 'Taller Central',
            'fecha_programada': date.today().isoformat(),
            'descripcion': 'Reparacion caja de cambios',
            'costo': '3500000.00',
            'estado': 'En Proceso'
        })
        self.assertEqual(response.status_code, 302)
        veh.refresh_from_db()
        self.assertEqual(veh.estado, 'Mantenimiento')

    # ──────────────────────────────────────────────
    # TESTS HU-008: MANTENIMIENTO
    # ──────────────────────────────────────────────

    def test_mantenimiento_crud_and_detail(self):
        self.client.login(username='admin', password='admin123')

        # 1. Crear Mantenimiento
        response = self.client.post(reverse('mantenimiento_crear'), {
            'vehiculo': self.vehiculo1.id,
            'tipo_mantenimiento': 'Preventivo',
            'taller_responsable': 'Taller Central Bogota D.C.',
            'fecha_programada': '2026-10-01',
            'descripcion': 'Cambio preventivo de frenos y revision de neumaticos',
            'costo': '1850000.00',
            'estado': 'Programado',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('mantenimiento_lista'))

        # 2. Verificar existencia en base de datos
        mant = Mantenimiento.objects.filter(vehiculo=self.vehiculo1).first()
        self.assertIsNotNone(mant)
        self.assertEqual(mant.tipo_mantenimiento, 'Preventivo')
        self.assertEqual(float(mant.costo), 1850000.00)

        # 3. Consultar lista
        list_response = self.client.get(reverse('mantenimiento_lista'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, f'MNT-{mant.id:04d}')
        self.assertContains(list_response, self.vehiculo1.placa)

        # 4. Consultar detalle
        det_response = self.client.get(reverse('mantenimiento_detalle', kwargs={'id': mant.id}))
        self.assertEqual(det_response.status_code, 200)
        self.assertContains(det_response, f'MNT-{mant.id}')
        self.assertContains(det_response, 'Taller Central Bogota D.C.')

    # ──────────────────────────────────────────────
    # TESTS HU-009 & HU-010: REPORTES
    # ──────────────────────────────────────────────

    def test_reportes_views(self):
        self.client.login(username='admin', password='admin123')

        # Registrar carga de combustible para reporte
        CargaCombustible.objects.create(
            viaje=self.viaje1,
            vehiculo=self.vehiculo1,
            conductor=self.cond_model,
            litros_cargados=120.0,
            costo_total=540000.0,
            ciudad='Bogota',
            fecha_carga=date(2026, 9, 20)
        )

        # 1. Reportes Index
        res_index = self.client.get(reverse('reportes_index'))
        self.assertEqual(res_index.status_code, 200)
        self.assertContains(res_index, 'Centro de Reportes')

        # 2. Reporte Consumo
        res_consumo = self.client.get(reverse('reporte_consumo'))
        self.assertEqual(res_consumo.status_code, 200)
        self.assertContains(res_consumo, self.vehiculo1.placa)

        # 3. Reporte Operacional
        res_op = self.client.get(reverse('reporte_operacional'))
        self.assertEqual(res_op.status_code, 200)
        self.assertContains(res_op, 'Reporte Operacional')
