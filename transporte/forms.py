import re
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Vehiculo, Conductor, Viaje, CargaCombustible, Mantenimiento, Incidente, Viatico


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['placa', 'modelo', 'capacidad_carga', 'kilometraje_actual', 'estado']
        widgets = {
            'placa': forms.TextInput(attrs={
                'name': 'placa',
                'id': 'plate',
                'placeholder': 'Ej. TRK-8921',
                'class': 'block w-full h-10 pl-9 pr-9 rounded-lg border border-outline-variant bg-surface-container-lowest text-primary font-tabular-data text-tabular-data uppercase tracking-wider focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/15 transition-all',
            }),
            'modelo': forms.TextInput(attrs={
                'name': 'modelo',
                'id': 'model',
                'placeholder': 'Ej. Volvo FH 540 / Scania R450',
                'class': 'block w-full h-10 pl-9 pr-3 rounded-lg border border-outline-variant bg-surface-container-lowest text-primary font-body-md text-body-md focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/15 transition-all',
            }),
            'capacidad_carga': forms.NumberInput(attrs={
                'name': 'capacidad_carga',
                'id': 'payload',
                'placeholder': '32000',
                'min': '100',
                'step': '50',
                'class': 'block w-full h-10 pl-9 pr-14 rounded-lg border border-outline-variant bg-surface-container-lowest text-primary font-tabular-data text-tabular-data focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/15 transition-all',
            }),
            'kilometraje_actual': forms.NumberInput(attrs={
                'name': 'kilometraje_actual',
                'id': 'odometer',
                'placeholder': '0',
                'min': '0',
                'step': '1',
                'class': 'block w-full h-10 pl-9 pr-14 rounded-lg border border-outline-variant bg-surface-container-lowest text-primary font-tabular-data text-tabular-data focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/15 transition-all',
            }),
            'estado': forms.RadioSelect(attrs={'name': 'estado'}),
        }

    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '').strip().upper()
        if not placa:
            raise ValidationError("La placa es obligatoria.")
        if len(placa) < 4 or len(placa) > 15:
            raise ValidationError("La placa debe tener entre 4 y 15 caracteres.")
        if not re.match(r'^[A-Z0-9\-\s]+$', placa):
            raise ValidationError("La placa solo puede contener letras mayúsculas, números y guiones.")
        
        # Validar unicidad
        qs = Vehiculo.objects.filter(placa=placa)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f"Ya existe un vehículo registrado con la placa {placa}.")
        return placa

    def clean_modelo(self):
        modelo = self.cleaned_data.get('modelo', '').strip()
        if len(modelo) < 2:
            raise ValidationError("El modelo debe tener al menos 2 caracteres.")
        return modelo

    def clean_capacidad_carga(self):
        capacidad = self.cleaned_data.get('capacidad_carga')
        if capacidad is not None and capacidad <= 0:
            raise ValidationError("La capacidad de carga debe ser mayor a 0 kg.")
        return capacidad

    def clean_kilometraje_actual(self):
        km = self.cleaned_data.get('kilometraje_actual')
        if km is not None and km < 0:
            raise ValidationError("El kilometraje actual no puede ser negativo.")
        return km

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        if self.instance and self.instance.pk and estado == 'Disponible':
            if self.instance.viajes.filter(estado='En curso').exists():
                raise ValidationError("No se puede marcar como 'Disponible' un vehículo que actualmente tiene un viaje en curso.")
        return cleaned_data


class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = ['nombre_completo', 'numero_licencia', 'telefono', 'correo']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'name': 'nombre_completo',
                'placeholder': 'Nombre completo del conductor',
                'class': 'w-full h-10 pl-10 pr-10 rounded-lg bg-white border border-outline-variant font-body-md text-body-md text-primary focus:ring-2 focus:ring-secondary/20 focus:border-secondary outline-none shadow-sm',
            }),
            'numero_licencia': forms.TextInput(attrs={
                'name': 'numero_licencia',
                'placeholder': 'Ej. LIC-9482014-C3',
                'class': 'w-full h-10 pl-10 pr-24 rounded-lg bg-white border border-outline-variant font-tabular-data text-tabular-data text-primary focus:ring-2 focus:ring-secondary/20 focus:border-secondary outline-none shadow-sm uppercase',
            }),
            'telefono': forms.TextInput(attrs={
                'name': 'telefono',
                'placeholder': '+57 300 000 0000',
                'class': 'w-full h-10 pl-10 pr-10 rounded-lg bg-white border border-outline-variant font-tabular-data text-tabular-data text-primary focus:ring-2 focus:ring-secondary/20 focus:border-secondary outline-none shadow-sm',
            }),
            'correo': forms.EmailInput(attrs={
                'name': 'correo',
                'placeholder': 'conductor@logicarga.com',
                'class': 'w-full h-10 pl-10 pr-10 rounded-lg bg-white border border-outline-variant font-body-md text-body-md text-primary focus:ring-2 focus:ring-secondary/20 focus:border-secondary outline-none shadow-sm',
            }),
        }

    def clean_nombre_completo(self):
        nombre = self.cleaned_data.get('nombre_completo', '').strip()
        if len(nombre) < 3:
            raise ValidationError("El nombre completo debe tener al menos 3 caracteres.")
        return nombre

    def clean_numero_licencia(self):
        licencia = self.cleaned_data.get('numero_licencia', '').strip().upper()
        if not licencia:
            raise ValidationError("El número de licencia es obligatorio.")
        if len(licencia) < 4:
            raise ValidationError("El número de licencia debe tener al menos 4 caracteres.")
        
        qs = Conductor.objects.filter(numero_licencia=licencia)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f"Ya existe un conductor con el número de licencia {licencia}.")
        return licencia

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if not telefono:
            raise ValidationError("El teléfono de contacto es obligatorio.")
        if not re.match(r'^[0-9\+\-\s\(\)]+$', telefono) or len(telefono) < 7:
            raise ValidationError("Ingrese un número de teléfono válido (mínimo 7 dígitos).")
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '').strip().lower()
        if not correo:
            raise ValidationError("El correo electrónico es obligatorio.")
        return correo


class ViajeForm(forms.ModelForm):
    class Meta:
        model = Viaje
        fields = [
            'vehiculo', 'conductor', 'usuario_conductor', 'ciudad_origen', 'ciudad_destino',
            'fecha_hora_salida', 'fecha_hora_llegada', 'tipo_carga',
            'kilometraje_inicial', 'kilometraje_final',
            'combustible_inicial', 'combustible_final', 'estado',
        ]
        widgets = {
            'vehiculo': forms.Select(attrs={
                'id': 'vehiculo-select',
                'name': 'vehiculo',
                'class': 'w-full h-12 pl-4 pr-10 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md text-body-md focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all appearance-none cursor-pointer',
            }),
            'conductor': forms.Select(attrs={
                'id': 'conductor-select',
                'name': 'conductor',
                'class': 'w-full h-12 pl-4 pr-10 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md text-body-md focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all appearance-none cursor-pointer',
            }),
            'usuario_conductor': forms.Select(attrs={
                'id': 'usuario-conductor-select',
                'name': 'usuario_conductor',
                'class': 'w-full h-12 pl-4 pr-10 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md text-body-md focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all appearance-none cursor-pointer',
            }),
            'ciudad_origen': forms.TextInput(attrs={
                'id': 'origen-input',
                'name': 'ciudad_origen',
                'placeholder': 'Ingrese ciudad de origen',
                'class': 'w-full h-11 pl-10 pr-4 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md text-body-md focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline',
            }),
            'ciudad_destino': forms.TextInput(attrs={
                'id': 'destino-input',
                'name': 'ciudad_destino',
                'placeholder': 'Ingrese ciudad de destino',
                'class': 'w-full h-11 pl-10 pr-4 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md text-body-md focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline',
            }),
            'fecha_hora_salida': forms.DateTimeInput(attrs={
                'id': 'fecha-salida',
                'name': 'fecha_hora_salida',
                'type': 'datetime-local',
                'class': 'w-full h-11 px-3 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-tabular-data text-tabular-data focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all',
            }, format='%Y-%m-%dT%H:%M'),
            'fecha_hora_llegada': forms.DateTimeInput(attrs={
                'id': 'fecha-llegada',
                'name': 'fecha_hora_llegada',
                'type': 'datetime-local',
                'class': 'w-full h-11 px-3 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-tabular-data text-tabular-data focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all',
            }, format='%Y-%m-%dT%H:%M'),
            'tipo_carga': forms.TextInput(attrs={
                'id': 'tipo-carga',
                'name': 'tipo_carga',
                'placeholder': 'Ej. Carga General Seca',
                'class': 'w-full h-11 pl-3 pr-10 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md text-body-md focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all',
            }),
            'kilometraje_inicial': forms.NumberInput(attrs={
                'id': 'km-inicial',
                'name': 'kilometraje_inicial',
                'placeholder': '0',
                'min': '0',
                'class': 'w-full h-12 pl-4 pr-14 rounded-lg bg-surface-container-lowest border border-outline-variant text-primary font-tabular-data font-bold focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all',
            }),
            'kilometraje_final': forms.NumberInput(attrs={
                'id': 'km-final',
                'name': 'kilometraje_final',
                'placeholder': '0',
                'min': '0',
                'class': 'w-full h-12 pl-4 pr-14 rounded-lg bg-surface-container-lowest border border-outline-variant text-primary font-tabular-data font-bold focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all',
            }),
            'combustible_inicial': forms.NumberInput(attrs={
                'name': 'combustible_inicial',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'class': 'w-full h-11 px-3 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-tabular-data text-tabular-data focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all',
            }),
            'combustible_final': forms.NumberInput(attrs={
                'name': 'combustible_final',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'class': 'w-full h-11 px-3 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-tabular-data text-tabular-data focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all',
            }),
            'estado': forms.Select(attrs={
                'name': 'estado',
                'class': 'w-full h-11 pl-3 pr-10 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md text-body-md focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all appearance-none cursor-pointer',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_hora_salida'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
        self.fields['fecha_hora_llegada'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
        self.fields['fecha_hora_llegada'].required = False
        self.fields['kilometraje_final'].required = False
        self.fields['combustible_inicial'].required = False
        self.fields['combustible_final'].required = False
        self.fields['usuario_conductor'].required = False

    def clean_ciudad_origen(self):
        origen = self.cleaned_data.get('ciudad_origen', '').strip()
        if len(origen) < 2:
            raise ValidationError("La ciudad de origen es obligatoria y debe tener al menos 2 caracteres.")
        return origen

    def clean_ciudad_destino(self):
        destino = self.cleaned_data.get('ciudad_destino', '').strip()
        if len(destino) < 2:
            raise ValidationError("La ciudad de destino es obligatoria y debe tener al menos 2 caracteres.")
        return destino

    def clean_tipo_carga(self):
        tipo = self.cleaned_data.get('tipo_carga', '').strip()
        if len(tipo) < 2:
            raise ValidationError("El tipo de carga es obligatorio.")
        return tipo

    def clean(self):
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        conductor = cleaned_data.get('conductor')
        origen = cleaned_data.get('ciudad_origen', '').strip()
        destino = cleaned_data.get('ciudad_destino', '').strip()
        fecha_salida = cleaned_data.get('fecha_hora_salida')
        fecha_llegada = cleaned_data.get('fecha_hora_llegada')
        km_inicial = cleaned_data.get('kilometraje_inicial')
        km_final = cleaned_data.get('kilometraje_final')
        comb_inicial = cleaned_data.get('combustible_inicial')
        comb_final = cleaned_data.get('combustible_final')
        estado = cleaned_data.get('estado')

        # 1. Origen y destino no pueden ser iguales
        if origen and destino and origen.lower() == destino.lower():
            raise ValidationError({'ciudad_destino': "La ciudad de destino no puede ser idéntica a la ciudad de origen."})

        # 2. Fechas de salida y llegada coherentes
        if fecha_salida and fecha_llegada:
            if fecha_llegada <= fecha_salida:
                raise ValidationError({'fecha_hora_llegada': "La fecha y hora de llegada debe ser posterior a la fecha y hora de salida."})

        # 3. Restricciones de Vehículo
        if vehiculo:
            if vehiculo.estado == 'Mantenimiento':
                raise ValidationError({'vehiculo': f"El vehículo {vehiculo.placa} se encuentra en mantenimiento y no puede ser asignado a un viaje."})
            
            if estado == 'En curso':
                viajes_activos = Vehiculo.objects.filter(id=vehiculo.id, viajes__estado='En curso')
                if self.instance and self.instance.pk:
                    viajes_activos = viajes_activos.exclude(viajes__id=self.instance.pk)
                if viajes_activos.exists():
                    raise ValidationError({'vehiculo': f"El vehículo {vehiculo.placa} ya se encuentra actualmente en un viaje en curso."})

        # 4. Restricciones de Conductor
        if conductor and estado == 'En curso':
            cond_activos = Conductor.objects.filter(id=conductor.id, viajes__estado='En curso')
            if self.instance and self.instance.pk:
                cond_activos = cond_activos.exclude(viajes__id=self.instance.pk)
            if cond_activos.exists():
                raise ValidationError({'conductor': f"El conductor {conductor.nombre_completo} ya tiene asignado un viaje en curso activo."})

        # 5. Restricciones de Kilometraje
        if km_inicial is not None and km_inicial < 0:
            raise ValidationError({'kilometraje_inicial': "El kilometraje inicial no puede ser negativo."})

        if km_final is not None:
            if km_final < 0:
                raise ValidationError({'kilometraje_final': "El kilometraje final no puede ser negativo."})
            if km_inicial is not None and km_final < km_inicial:
                raise ValidationError({'kilometraje_final': "El kilometraje final no puede ser menor al kilometraje inicial del viaje."})

        # 6. Restricciones de Combustible
        if comb_inicial is not None and comb_inicial < 0:
            raise ValidationError({'combustible_inicial': "El combustible inicial no puede ser negativo."})
        if comb_final is not None and comb_final < 0:
            raise ValidationError({'combustible_final': "El combustible final no puede ser negativo."})

        # 7. Restricciones al Finalizar Viaje
        if estado == 'Finalizado':
            if km_final is None:
                raise ValidationError({'kilometraje_final': "Debe registrar el kilometraje final para poder marcar el viaje como Finalizado."})
            if not fecha_llegada:
                raise ValidationError({'fecha_hora_llegada': "Debe registrar la fecha y hora de llegada para finalizar el viaje."})

        return cleaned_data


class CargaCombustibleForm(forms.ModelForm):
    class Meta:
        model = CargaCombustible
        fields = ['viaje', 'vehiculo', 'conductor', 'litros_cargados', 'costo_total', 'ciudad', 'fecha_carga', 'foto_evidencia']
        widgets = {
            'viaje': forms.Select(attrs={
                'name': 'viaje',
                'class': 'w-full h-11 pl-11 pr-10 rounded-lg border border-outline-variant bg-white font-body-md text-body-md text-primary font-medium focus:ring-2 focus:ring-secondary focus:border-secondary transition-colors appearance-none cursor-pointer',
            }),
            'vehiculo': forms.Select(attrs={
                'name': 'vehiculo',
                'class': 'w-full h-11 pl-11 pr-10 rounded-lg border border-outline-variant bg-white font-body-md text-body-md text-primary font-medium focus:ring-2 focus:ring-secondary focus:border-secondary transition-colors appearance-none cursor-pointer',
            }),
            'conductor': forms.Select(attrs={
                'name': 'conductor',
                'class': 'w-full h-11 pl-11 pr-10 rounded-lg border border-outline-variant bg-white font-body-md text-body-md text-primary font-medium focus:ring-2 focus:ring-secondary focus:border-secondary transition-colors appearance-none cursor-pointer',
            }),
            'litros_cargados': forms.NumberInput(attrs={
                'name': 'litros_cargados',
                'placeholder': '0.00',
                'min': '0.01',
                'step': '0.01',
                'class': 'w-full h-11 pl-4 pr-14 rounded-lg border border-outline-variant bg-white font-bold text-primary focus:ring-2 focus:ring-secondary focus:border-secondary transition-colors',
            }),
            'costo_total': forms.NumberInput(attrs={
                'name': 'costo_total',
                'placeholder': '0.00',
                'min': '0.01',
                'step': '0.01',
                'class': 'w-full h-11 pl-9 pr-14 rounded-lg border border-outline-variant bg-white font-bold text-primary focus:ring-2 focus:ring-secondary focus:border-secondary transition-colors',
            }),
            'ciudad': forms.TextInput(attrs={
                'name': 'ciudad',
                'placeholder': 'Ciudad de la estación de carga',
                'class': 'w-full h-11 pl-10 pr-4 rounded-lg border border-outline-variant bg-white font-body-md text-body-md text-primary focus:ring-2 focus:ring-secondary focus:border-secondary transition-colors',
            }),
            'fecha_carga': forms.DateInput(attrs={
                'name': 'fecha_carga',
                'type': 'date',
                'class': 'w-full h-11 px-3 rounded-lg border border-outline-variant bg-white font-tabular-data text-tabular-data text-primary focus:ring-2 focus:ring-secondary focus:border-secondary transition-colors',
            }, format='%Y-%m-%d'),
            'foto_evidencia': forms.FileInput(attrs={
                'id': 'foto_evidencia',
                'class': 'block w-full text-body-sm text-on-surface file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-label-sm file:font-semibold file:bg-primary file:text-on-primary hover:file:bg-primary-container file:cursor-pointer cursor-pointer border border-outline-variant rounded-lg p-1 bg-white',
                'accept': 'image/*',
            }),
        }

    def clean_litros_cargados(self):
        litros = self.cleaned_data.get('litros_cargados')
        if litros is None or litros <= 0:
            raise ValidationError("Los litros cargados deben ser una cantidad estrictamente mayor a 0.")
        return litros

    def clean_costo_total(self):
        costo = self.cleaned_data.get('costo_total')
        if costo is None or costo <= 0:
            raise ValidationError("El costo total debe ser una cantidad estrictamente mayor a 0.")
        return costo

    def clean_fecha_carga(self):
        fecha = self.cleaned_data.get('fecha_carga')
        if fecha and fecha > date.today():
            raise ValidationError("La fecha de carga no puede ser una fecha futura.")
        return fecha

    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad', '').strip()
        if len(ciudad) < 2:
            raise ValidationError("La ciudad de carga es obligatoria.")
        return ciudad

    def clean(self):
        cleaned_data = super().clean()
        viaje = cleaned_data.get('viaje')
        vehiculo = cleaned_data.get('vehiculo')
        conductor = cleaned_data.get('conductor')

        if viaje:
            # Autoalinear o verificar coherencia con el viaje
            if not vehiculo:
                cleaned_data['vehiculo'] = viaje.vehiculo
            elif vehiculo != viaje.vehiculo:
                raise ValidationError({'vehiculo': f"El vehículo seleccionado ({vehiculo.placa}) no corresponde al vehículo asignado en el viaje ({viaje.vehiculo.placa})."})

            if not conductor:
                cleaned_data['conductor'] = viaje.conductor
            elif conductor != viaje.conductor:
                raise ValidationError({'conductor': f"El conductor seleccionado ({conductor.nombre_completo}) no corresponde al conductor asignado en el viaje ({viaje.conductor.nombre_completo})."})

        return cleaned_data


class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = [
            'vehiculo', 'tipo_mantenimiento', 'taller_responsable',
            'fecha_programada', 'fecha_realizada', 'descripcion',
            'costo', 'estado',
        ]
        widgets = {
            'vehiculo': forms.Select(attrs={
                'name': 'vehiculo',
                'id': 'vehiculo',
                'class': 'w-full py-2.5 pl-3 pr-10 rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md text-on-surface focus:border-primary-container focus:ring-1 focus:ring-primary-container appearance-none cursor-pointer',
            }),
            'tipo_mantenimiento': forms.Select(attrs={
                'name': 'tipo_mantenimiento',
                'id': 'tipo_mantenimiento',
                'class': 'w-full py-2.5 pl-3 pr-10 rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md text-on-surface focus:border-primary-container focus:ring-1 focus:ring-primary-container appearance-none cursor-pointer',
            }),
            'taller_responsable': forms.TextInput(attrs={
                'name': 'taller_responsable',
                'id': 'taller',
                'placeholder': 'Ej. Taller Central LogiCarga - Bogotá D.C.',
                'class': 'w-full pl-10 pr-3 py-2.5 rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md text-on-surface focus:border-primary-container',
            }),
            'fecha_programada': forms.DateInput(attrs={
                'name': 'fecha_programada',
                'id': 'fecha_programada',
                'type': 'date',
                'class': 'w-full pl-10 pr-3 py-2.5 rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md text-on-surface focus:border-primary-container focus:ring-1 focus:ring-primary-container',
            }, format='%Y-%m-%d'),
            'fecha_realizada': forms.DateInput(attrs={
                'name': 'fecha_realizada',
                'id': 'fecha_realizada',
                'type': 'date',
                'class': 'w-full pl-10 pr-3 py-2.5 rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md text-on-surface focus:border-primary-container focus:ring-1 focus:ring-primary-container',
            }, format='%Y-%m-%d'),
            'descripcion': forms.Textarea(attrs={
                'name': 'descripcion',
                'id': 'descripcion',
                'placeholder': 'Detalle las tareas a realizar, repuestos a sustituir y especificaciones técnicas...',
                'rows': 3,
                'class': 'w-full rounded-lg border border-outline-variant bg-surface-container-lowest p-3.5 font-body-md text-body-md text-on-surface focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 transition-all placeholder:text-outline',
            }),
            'costo': forms.NumberInput(attrs={
                'name': 'costo',
                'id': 'costo',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'class': 'w-full pl-8 pr-12 py-2.5 rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md font-semibold text-on-surface focus:border-primary-container focus:ring-1 focus:ring-primary-container font-tabular-data',
            }),
            'estado': forms.Select(attrs={
                'name': 'estado',
                'id': 'estado',
                'class': 'w-full py-2.5 pl-3 pr-10 rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md text-on-surface focus:border-primary-container focus:ring-1 focus:ring-primary-container appearance-none cursor-pointer',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_programada'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_realizada'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_realizada'].required = False

    def clean_costo(self):
        costo = self.cleaned_data.get('costo')
        if costo is not None and costo < 0:
            raise ValidationError("El costo de mantenimiento no puede ser negativo.")
        return costo

    def clean_taller_responsable(self):
        taller = self.cleaned_data.get('taller_responsable', '').strip()
        if len(taller) < 3:
            raise ValidationError("El taller responsable debe tener al menos 3 caracteres.")
        return taller

    def clean_descripcion(self):
        desc = self.cleaned_data.get('descripcion', '').strip()
        if len(desc) < 5:
            raise ValidationError("La descripción del mantenimiento debe ser más detallada (mínimo 5 caracteres).")
        return desc

    def clean_fecha_realizada(self):
        fecha = self.cleaned_data.get('fecha_realizada')
        if fecha and fecha > date.today():
            raise ValidationError("La fecha de realización del mantenimiento no puede ser futura.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_realizada = cleaned_data.get('fecha_realizada')

        if estado == 'Finalizado' and not fecha_realizada:
            raise ValidationError({'fecha_realizada': "Debe registrar la fecha en la que se realizó el mantenimiento para marcarlo como Finalizado."})

        return cleaned_data


INPUT_CLASS = (
    'block w-full h-10 px-3 rounded-lg border border-outline-variant '
    'bg-surface-container-lowest text-on-surface font-body-md text-body-md '
    'focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/15 transition-all'
)

SELECT_CLASS = (
    'block w-full h-10 px-3 rounded-lg border border-outline-variant '
    'bg-surface-container-lowest text-on-surface font-body-md text-body-md '
    'focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/15 transition-all cursor-pointer'
)

TEXTAREA_CLASS = (
    'block w-full px-3 py-2.5 rounded-lg border border-outline-variant '
    'bg-surface-container-lowest text-on-surface font-body-md text-body-md '
    'focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/15 transition-all resize-none'
)


class IncidenteForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = ['viaje', 'tipo_incidente', 'lugar', 'fecha_incidente', 'descripcion', 'foto_evidencia']
        widgets = {
            'viaje': forms.Select(attrs={
                'id': 'inc_viaje',
                'class': SELECT_CLASS,
            }),
            'tipo_incidente': forms.Select(attrs={
                'id': 'inc_tipo',
                'class': SELECT_CLASS,
            }),
            'lugar': forms.TextInput(attrs={
                'id': 'inc_lugar',
                'placeholder': 'Ej. Sector La Línea, Cajamarca',
                'class': INPUT_CLASS,
            }),
            'fecha_incidente': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    'id': 'inc_fecha',
                    'type': 'datetime-local',
                    'class': INPUT_CLASS,
                }
            ),
            'descripcion': forms.Textarea(attrs={
                'id': 'inc_descripcion',
                'rows': 4,
                'placeholder': 'Describa con detalle lo ocurrido, las condiciones y las medidas tomadas...',
                'class': TEXTAREA_CLASS,
            }),
            'foto_evidencia': forms.FileInput(attrs={
                'id': 'inc_foto',
                'class': 'block w-full text-body-sm text-on-surface file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-label-sm file:font-semibold file:bg-primary file:text-on-primary hover:file:bg-primary-container file:cursor-pointer cursor-pointer border border-outline-variant rounded-lg p-1 bg-surface-container-lowest',
                'accept': 'image/*',
            }),
        }
        labels = {
            'viaje': 'Viaje Asociado',
            'tipo_incidente': 'Tipo de Incidente',
            'lugar': 'Lugar del Incidente',
            'fecha_incidente': 'Fecha y Hora',
            'descripcion': 'Descripción Detallada',
            'foto_evidencia': 'Foto de Evidencia (Opcional)',
        }

    def clean_lugar(self):
        lugar = self.cleaned_data.get('lugar', '').strip()
        if len(lugar) < 3:
            raise ValidationError('El lugar debe tener al menos 3 caracteres.')
        return lugar

    def clean_descripcion(self):
        desc = self.cleaned_data.get('descripcion', '').strip()
        if len(desc) < 10:
            raise ValidationError('La descripción debe tener al menos 10 caracteres.')
        return desc


class ViaticoForm(forms.ModelForm):
    class Meta:
        model = Viatico
        fields = ['viaje', 'tipo_gasto', 'monto', 'descripcion', 'fecha_gasto', 'comprobante_foto']
        widgets = {
            'viaje': forms.Select(attrs={
                'id': 'vtc_viaje',
                'class': SELECT_CLASS,
            }),
            'tipo_gasto': forms.Select(attrs={
                'id': 'vtc_tipo',
                'class': SELECT_CLASS,
            }),
            'monto': forms.NumberInput(attrs={
                'id': 'vtc_monto',
                'placeholder': '0',
                'min': '1',
                'step': '100',
                'class': INPUT_CLASS,
            }),
            'descripcion': forms.TextInput(attrs={
                'id': 'vtc_descripcion',
                'placeholder': 'Ej. Peaje en la salida de Bogotá, factura adjunta',
                'class': INPUT_CLASS,
            }),
            'fecha_gasto': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'id': 'vtc_fecha',
                    'type': 'date',
                    'class': INPUT_CLASS,
                }
            ),
            'comprobante_foto': forms.FileInput(attrs={
                'id': 'vtc_comprobante',
                'class': 'block w-full text-body-sm text-on-surface file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-label-sm file:font-semibold file:bg-primary file:text-on-primary hover:file:bg-primary-container file:cursor-pointer cursor-pointer border border-outline-variant rounded-lg p-1 bg-surface-container-lowest',
                'accept': 'image/*',
            }),
        }
        labels = {
            'viaje': 'Viaje Asociado',
            'tipo_gasto': 'Tipo de Gasto',
            'monto': 'Valor (COP)',
            'descripcion': 'Descripción / Observaciones',
            'fecha_gasto': 'Fecha del Gasto',
            'comprobante_foto': 'Comprobante / Factura (Opcional)',
        }

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto <= 0:
            raise ValidationError('El monto debe ser mayor a $0 COP.')
        return monto

