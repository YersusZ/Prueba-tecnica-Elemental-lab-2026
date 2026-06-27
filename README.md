# Prueba Técnica — Elemental Lab 2026
## API REST de Agendamiento de Citas

Sistema de agendamiento interno con reglas de negocio para manejo de citas, clientes VIP y validación de disponibilidad.

---

## Tecnologías

- Python 3.14
- Django 6.0
- Django REST Framework
- drf-spectacular (documentación OpenAPI)
- SQLite

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/Prueba_tecnica_Elemental_lab_2026.git
cd Prueba_tecnica_Elemental_lab_2026/Prueba_tecnica

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Correr el servidor
python manage.py runserver
```

---

## Endpoints

### Clientes

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/customers/` | Listar todos los clientes |
| POST | `/api/customers/` | Crear un cliente |
| GET | `/api/customers/<id>/` | Obtener un cliente |
| PUT | `/api/customers/<id>/` | Actualizar un cliente |
| DELETE | `/api/customers/<id>/` | Eliminar un cliente |

#### Crear cliente — Body

```json
{
  "name": "Juan Pérez",
  "category": "VIP"
}
```

> `category` acepta: `"VIP"` o `"Regular"`

---

### Citas

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/appointments/` | Listar todas las citas |
| POST | `/api/appointments/` | Crear una cita |
| GET | `/api/appointments/availability/<date>/` | Ver bloques ocupados para una fecha |

#### Crear cita — Body

```json
{
  "customer": 1,
  "date": "2026-07-10",
  "start_time": "10:00:00",
  "duration_minutes": 60
}
```

#### Respuesta exitosa (201)

```json
{
  "id": 1,
  "customer": 1,
  "date": "2026-07-10",
  "start_time": "09:45:00",
  "duration_minutes": 90
}
```

> Para clientes VIP, el sistema ajusta automáticamente `start_time` -15 min y `duration_minutes` +30 min para incluir el buffer de 15 minutos antes y después.

#### Ver disponibilidad

```
GET /api/appointments/availability/2026-07-10/
```

Retorna los bloques de tiempo ya ocupados o bloqueados para esa fecha, incluyendo los buffers VIP.

---

## Reglas de Negocio

### Regla del Almuerzo
No se permiten citas que toquen el rango de **13:00 a 14:00**.

```
✅ 11:00 - 12:30  →  permitido
❌ 12:30 - 13:15  →  rechazado (toca el almuerzo)
❌ 13:30 - 14:30  →  rechazado (dentro del almuerzo)
✅ 14:00 - 15:00  →  permitido
```

### Buffer de Cliente VIP
Si el cliente es VIP, el sistema bloquea automáticamente **15 minutos antes y 15 minutos después** de su cita. Ninguna otra cita puede solaparse con ese tiempo de colchón.

```
Cliente VIP agenda 10:00 por 60 min
→ Se guarda en DB: start_time=09:45, duration_minutes=90
→ Bloquea: 09:45 a 11:15
```

### Bloqueo de Martes
Los martes después de las **16:00** el sistema está en mantenimiento. No se permiten citas que empiecen o terminen después de esa hora.

```
❌ Martes 15:30 por 60 min  →  rechazado (termina a las 16:30)
✅ Martes 14:00 por 60 min  →  permitido (termina a las 15:00)
```

### Anti-Solapamiento
No se pueden crear dos citas en el mismo día que se solapen en tiempo, incluyendo los buffers VIP ya guardados en la base de datos.

---

## Documentación Interactiva

Con el servidor corriendo, accede a:

| URL | Descripción |
|-----|-------------|
| `/api/schema/swagger-ui/` | Swagger UI |
| `/api/schema/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI schema (JSON) |

---

## Estructura del Proyecto

```
Prueba_tecnica/
├── Prueba_tecnica/
│   ├── models.py        # Modelos Customer y Appointment
│   ├── serializers.py   # Validaciones de negocio
│   ├── views.py         # ViewSets y lógica VIP
│   ├── urls.py          # Rutas de la API
│   └── settings.py      # Configuración Django
├── manage.py
├── db.sqlite3
└── README.md
```

---

## Modelos

### Customer

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | AutoField | Clave primaria |
| `name` | CharField | Nombre del cliente |
| `category` | CharField | `VIP` o `Regular` |

### Appointment

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | AutoField | Clave primaria |
| `customer` | ForeignKey | Relación con Customer |
| `date` | DateField | Fecha de la cita |
| `start_time` | TimeField | Hora de inicio (ajustada si es VIP) |
| `duration_minutes` | IntegerField | Duración en minutos (ajustada si es VIP) |

---

## Errores comunes

| Código | Causa |
|--------|-------|
| 400 | Campos faltantes, solapamiento, regla de almuerzo o martes |
| 404 | Cliente no encontrado |
| 500 | Error interno — revisar logs del servidor |