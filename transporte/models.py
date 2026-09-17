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

    @property
    def intervalo_mantenimiento(self):
        return 30000

    @property
    def proximo_mantenimiento_km(self):
        if self.kilometraje_actual == 0:
            return 30000
        return ((self.kilometraje_actual // 30000) + 1) * 30000

    @property
    def km_para_proximo_mantenimiento(self):
        return max(0, self.proximo_mantenimiento_km - self.kilometraje_actual)

    @property
    def km_ciclo_actual(self):
        return self.kilometraje_actual % 30000

    @property
    def porcentaje_ciclo_mantenimiento(self):
        return min(100, round((self.km_ciclo_actual / 30000) * 100, 1))

    @property
    def requiere_mantenimiento_preventivo(self):
        return self.km_para_proximo_mantenimiento <= 3000



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
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
    ]

    viaje = models.ForeignKey(Viaje, on_delete=models.PROTECT, related_name='cargas_combustible')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name='cargas_combustible')
    conductor = models.ForeignKey(Conductor, on_delete=models.PROTECT, related_name='cargas_combustible')
    litros_cargados = models.DecimalField(max_digits=8, decimal_places=2)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2)
    ciudad = models.CharField(max_length=150)
    fecha_carga = models.DateField()
    foto_evidencia = models.ImageField(upload_to='combustible/', null=True, blank=True, verbose_name='Foto / Comprobante')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    observacion_admin = models.TextField(blank=True, verbose_name='Observación de Administración')
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Carga de Combustible'
        verbose_name_plural = 'Cargas de Combustible'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Carga {self.id} – {self.litros_cargados}L en {self.ciudad} ({self.estado})'


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


class Incidente(models.Model):
    TIPO_CHOICES = [
        ('Falla Mecánica', 'Falla Mecánica'),
        ('Retraso en Vía', 'Retraso en Vía'),
        ('Pinchazo Neumático', 'Pinchazo Neumático'),
        ('Desvío por Derrumbe', 'Desvío por Derrumbe'),
        ('Derrame de Lubricante', 'Derrame de Lubricante'),
        ('Accidente de Tránsito', 'Accidente de Tránsito'),
        ('Robo o Hurto', 'Robo o Hurto'),
        ('Otro', 'Otro'),
    ]
    ESTADO_CHOICES = [
        ('Reportado', 'Reportado'),
        ('En Revisión', 'En Revisión'),
        ('Resuelto', 'Resuelto'),
        ('Rechazado', 'Rechazado'),
    ]

    viaje = models.ForeignKey(Viaje, on_delete=models.PROTECT, related_name='incidentes')
    tipo_incidente = models.CharField(max_length=50, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    lugar = models.CharField(max_length=200)
    fecha_incidente = models.DateTimeField()
    foto_evidencia = models.ImageField(upload_to='incidentes/', null=True, blank=True, verbose_name='Foto de Evidencia')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Reportado')
    respuesta_admin = models.TextField(blank=True, verbose_name='Respuesta / Dictamen Administrativo')
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Incidente'
        verbose_name_plural = 'Incidentes'
        ordering = ['-fecha_incidente']

    def __str__(self):
        return f'INC-{self.id} – {self.tipo_incidente} ({self.viaje})'


class Viatico(models.Model):
    TIPO_GASTO_CHOICES = [
        ('Peajes', 'Peajes'),
        ('Hospedaje', 'Hospedaje'),
        ('Alimentación', 'Alimentación'),
        ('Parqueadero', 'Parqueadero'),
        ('Lavado de unidad', 'Lavado de unidad'),
        ('Desvare menor', 'Desvare menor'),
        ('Otro', 'Otro'),
    ]
    ESTADO_CHOICES = [
        ('En validación', 'En validación'),
        ('Aprobado', 'Aprobado'),
        ('Reembolsado', 'Reembolsado'),
        ('Rechazado', 'Rechazado'),
    ]

    viaje = models.ForeignKey(Viaje, on_delete=models.PROTECT, related_name='viaticos')
    conductor = models.ForeignKey(Conductor, on_delete=models.PROTECT, related_name='viaticos')
    tipo_gasto = models.CharField(max_length=50, choices=TIPO_GASTO_CHOICES)
    monto = models.DecimalField(max_digits=14, decimal_places=2, help_text='Valor en COP')
    descripcion = models.CharField(max_length=300, blank=True)
    fecha_gasto = models.DateField()
    comprobante_foto = models.ImageField(upload_to='viaticos/', null=True, blank=True, verbose_name='Comprobante / Factura')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='En validación')
    observacion_admin = models.TextField(blank=True, verbose_name='Observación de Auditoría')
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Viático'
        verbose_name_plural = 'Viáticos'
        ordering = ['-fecha_gasto']

    def __str__(self):
        return f'VTC-{self.id} – {self.tipo_gasto} ${self.monto} COP'

