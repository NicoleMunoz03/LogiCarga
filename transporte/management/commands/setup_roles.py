from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from transporte.models import Viaje, Conductor, Vehiculo


class Command(BaseCommand):
    help = 'Inicializa grupos de roles (ADMINISTRADOR, CONDUCTOR) y usuarios de prueba (admin, conductor1).'

    def handle(self, *args, **options):
        # 1. Crear Grupos
        grupo_admin, created_admin = Group.objects.get_or_create(name='ADMINISTRADOR')
        if created_admin:
            self.stdout.write(self.style.SUCCESS('Grupo "ADMINISTRADOR" creado exitosamente.'))
        else:
            self.stdout.write('Grupo "ADMINISTRADOR" ya existía.')

        grupo_conductor, created_cond = Group.objects.get_or_create(name='CONDUCTOR')
        if created_cond:
            self.stdout.write(self.style.SUCCESS('Grupo "CONDUCTOR" creado exitosamente.'))
        else:
            self.stdout.write('Grupo "CONDUCTOR" ya existía.')

        # 2. Crear Usuario Admin
        admin_user, created_uadmin = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Carlos',
                'last_name': 'Guzmán',
                'email': 'admin@logicarga.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        admin_user.groups.add(grupo_admin)
        if created_uadmin:
            self.stdout.write(self.style.SUCCESS('Usuario "admin" creado con clave "admin123".'))
        else:
            self.stdout.write('Usuario "admin" actualizado con clave "admin123" y rol ADMINISTRADOR.')

        # 3. Crear Usuario Conductor
        conductor_user, created_ucond = User.objects.get_or_create(
            username='conductor1',
            defaults={
                'first_name': 'Andrés',
                'last_name': 'Martínez',
                'email': 'conductor1@logicarga.com',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        conductor_user.set_password('conductor123')
        conductor_user.is_staff = False
        conductor_user.is_superuser = False
        conductor_user.save()
        conductor_user.groups.add(grupo_conductor)
        if created_ucond:
            self.stdout.write(self.style.SUCCESS('Usuario "conductor1" creado con clave "conductor123".'))
        else:
            self.stdout.write('Usuario "conductor1" actualizado con clave "conductor123" y rol CONDUCTOR.')

        # 4. Asociar conductor1 a viajes existentes para pruebas inmediatas
        viajes_sin_conductor = Viaje.objects.filter(usuario_conductor__isnull=True)
        if viajes_sin_conductor.exists():
            count = viajes_sin_conductor.update(usuario_conductor=conductor_user)
            self.stdout.write(self.style.SUCCESS(f'Se asociaron {count} viajes existentes al usuario "conductor1".'))
        else:
            # Si no hay viajes, o todos tienen usuario, verificar que conductor1 tenga al menos 1
            if not Viaje.objects.filter(usuario_conductor=conductor_user).exists() and Viaje.objects.exists():
                primer_viaje = Viaje.objects.first()
                primer_viaje.usuario_conductor = conductor_user
                primer_viaje.save()
                self.stdout.write(self.style.SUCCESS(f'Se asignó el viaje #{primer_viaje.id} a "conductor1".'))

        self.stdout.write(self.style.SUCCESS('=== INICIALIZACIÓN COMPLETADA CON ÉXITO ==='))
