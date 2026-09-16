from django.db import models
from django.contrib.auth.models import User


class Vehiculo(models.Model):
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('En viaje', 'En viaje'),
        ('Mantenimiento', 'Mantenimiento'),
    ]

    placa = models.CharField(max_length=20, unique=True)
    modelo = models.CharField(max_length=100)
    capacidad_carga = models.DecimalField(max_digits=10, decimal_places=2, help_text='Capacidad en kg')
    kilometraje_actual = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Disponible')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.placa} – {self.modelo}'


class Conductor(models.Model):
    nombre_completo = models.CharField(max_length=150)
    numero_licencia = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=30)
    correo = models.EmailField(max_length=254)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conductor'
        verbose_name_plural = 'Conductores'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.nombre_completo} ({self.numero_licencia})'


class Viaje(models.Model):
    ESTADO_CHOICES = [
        ('Programado', 'Programado'),
        ('En curso', 'En curso'),
        ('Finalizado', 'Finalizado'),
    ]

    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name='viajes')
    conductor = models.ForeignKey(Conductor, on_delete=models.PROTECT, related_name='viajes')
    usuario_conductor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='viajes_asignados',
        verbose_name='Usuario Conductor'
    )
    ciudad_origen = models.CharField(max_length=150)
    ciudad_destino = models.CharField(max_length=150)
    fecha_hora_salida = models.DateTimeField()
    fecha_hora_llegada = models.DateTimeField(null=True, blank=True)
    tipo_carga = models.CharField(max_length=100)
    kilometraje_inicial = models.PositiveIntegerField(default=0)
    kilometraje_final = models.PositiveIntegerField(null=True, blank=True)
    combustible_inicial = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text='Litros al inicio')
    combustible_final = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text='Litros al finalizar')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Programado')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Viaje'
        verbose_name_plural = 'Viajes'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Viaje {self.id} – {self.ciudad_origen} → {self.ciudad_destino}'


class CargaCombustible(models.Model):
    viaje = models.ForeignKey(Viaje, on_delete=models.PROTECT, related_name='cargas_combustible')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name='cargas_combustible')
    conductor = models.ForeignKey(Conductor, on_delete=models.PROTECT, related_name='cargas_combustible')
    litros_cargados = models.DecimalField(max_digits=8, decimal_places=2)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2)
    ciudad = models.CharField(max_length=150)
    fecha_carga = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Carga de Combustible'
        verbose_name_plural = 'Cargas de Combustible'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Carga {self.id} – {self.litros_cargados}L en {self.ciudad}'


class Mantenimiento(models.Model):
    TIPO_CHOICES = [
        ('Preventivo', 'Preventivo'),
        ('Correctivo', 'Correctivo'),
        ('Predictivo', 'Predictivo'),
    ]
    ESTADO_CHOICES = [
        ('Programado', 'Programado'),
        ('En Proceso', 'En Proceso'),
        ('Finalizado', 'Finalizado'),
    ]

    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name='mantenimientos')
    tipo_mantenimiento = models.CharField(max_length=20, choices=TIPO_CHOICES)
    taller_responsable = models.CharField(max_length=200)
    fecha_programada = models.DateField()
    fecha_realizada = models.DateField(null=True, blank=True)
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=14, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Programado')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'MNT-{self.id} – {self.vehiculo.placa} ({self.tipo_mantenimiento})'
