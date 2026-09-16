# LogiCarga Transportes S.A. 🚛📦

Sistema integral de gestión logística y despacho de carga pesada desarrollado en **Django 6** y diseñado con estándares corporativos, roles basados en permisos (RBAC), telemetría de flota, control de combustible y órdenes técnicas de mantenimiento.

---

## 🌟 Características Principales

- **Dashboard Ejecutivo**: Monitoreo de flota en tiempo real, viajes en curso, alertas preventivas y balance operativo.
- **Gestión de Vehículos**: Control de tractocamiones, dobletroques y camiones rígidos (placas, modelos, capacidad de carga, odómetro y estado).
- **Gestión de Conductores**: Fichas de conductores con validación estricta de licencias, teléfonos y documentos de identidad.
- **Módulo de Despacho y Viajes**: Programación de rutas, estimación de tiempos de llegada, asignación de carga y actualización automática de estados del vehículo.
- **Control de Combustible**: Registro de abastecimiento (Diesel ACPM), galonaje/litros, costos facturados y cálculo de rendimientos.
- **Taller y Mantenimientos**: Órdenes técnicas preventivas, predictivas y correctivas con desglose de costos y vinculación al estado del automotor.
- **Centro de Reportes**: Analítica consolidada de consumo de combustible, efectividad de despachos y reportes operacionales exportables a CSV/PDF.
- **Roles y Permisos (RBAC)**:
  - **ADMINISTRADOR**: Acceso total a todos los módulos y reportes ejecutivos.
  - **CONDUCTOR**: Acceso restringido a sus viajes asignados (*Mis Viajes*) y registro seguro de combustible.

---

## 🔐 Credenciales del Sistema

| Rol | Usuario | Contraseña |
| :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` |
| **Conductor** | `conductor1` | `conductor123` |
| **Conductor** | `conductor2` | `conductor123` |

---

## 🚀 Despliegue en Render

El repositorio ya cuenta con `render.yaml`, `build.sh`, `Procfile` y `requirements.txt` listos para desplegar:

### Opción 1: Despliegue con Blueprint (Recomendado)
1. Inicia sesión en [Render](https://render.com/).
2. Haz clic en **New +** y selecciona **Blueprint**.
3. Conecta este repositorio: `https://github.com/NicoleMunoz03/LogiCarga.git`.
4. Render detectará automáticamente el archivo `render.yaml` y desplegará el servicio web.

### Opción 2: Despliegue Manual (Web Service)
1. En Render, crea un nuevo **Web Service**.
2. Conecta el repositorio de GitHub.
3. Configura:
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application`
4. Variables de entorno:
   - `PYTHON_VERSION`: `3.12.0`
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(Generar clave segura)*
   - `ALLOWED_HOSTS`: `.onrender.com,localhost,127.0.0.1`
   - `CSRF_TRUSTED_ORIGINS`: `https://*.onrender.com`

---

## 💻 Instalación y Ejecución Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/NicoleMunoz03/LogiCarga.git
cd LogiCarga

# 2. Crear y activar entorno virtual
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Migrar base de datos y cargar datos iniciales
python manage.py migrate
python manage.py setup_roles
python seed_data.py

# 5. Ejecutar servidor de desarrollo
python manage.py runserver
```

---

## 🧪 Pruebas Automatizadas

Para ejecutar la suite de pruebas unitarias y de validación:
```bash
python manage.py test
```
