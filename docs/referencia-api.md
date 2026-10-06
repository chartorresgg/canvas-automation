# API Reference

Documentación de los 9 endpoints REST del backend de Canvas LMS Automation App.

> **Documentación interactiva completa:** http://localhost:8000/docs (Swagger UI)
> Disponible con el servidor corriendo localmente.

---

## Información general

| Parámetro | Valor |
|---|---|
| Base URL (local) | `http://localhost:8000/api/v1` |
| Formato | JSON (requests y responses) |
| Autenticación | Token Canvas configurado en `.env` del servidor |
| Progreso en tiempo real | Server-Sent Events (SSE) |

---

## Endpoints de Despliegue

### `POST /deploy/upload`
**Validación previa del ZIP — sin interactuar con Canvas**

Extrae y normaliza el ZIP localmente. Útil para verificar la estructura
del aula antes de iniciar el despliegue real.

**Request:** `multipart/form-data`

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `zip_file` | File (.zip) | ✅ | ZIP con los materiales del aula |
| `excel_file` | File (.xlsx) | ❌ | Excel del Guion de módulo |

**Response `200 OK`:**
```json
{
  "task_id": "uuid-generado",
  "filename": "ESC535.zip",
  "total_files": 194,
  "total_size_mb": 45.2,
  "folders_renamed": ["1 Archivos → 1. Archivos"],
  "files_renamed": ["U1_Lectura fundamental_1.pdf → U1_Lectura_Fundamental_1.pdf"],
  "warnings": [],
  "message": "ZIP procesado exitosamente. 194 archivos listos."
}
```

---

### `POST /deploy`
**Iniciar el despliegue completo del aula virtual**

Inicia el proceso como BackgroundTask y retorna inmediatamente.
El progreso se monitorea con el endpoint SSE.

**Request:** `multipart/form-data`

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `zip_file` | File (.zip) | ✅ | ZIP con los materiales del aula |
| `excel_file` | File (.xlsx) | ❌ | Excel del Guion de módulo |
| `course_option` | string | ✅ | `"new"` o `"existing"` |
| `course_name` | string | Si `new` | Nombre del curso a crear en Canvas |
| `template_id` | integer | Si `new` | ID de la plantilla Canvas |
| `course_id` | integer | Si `existing` | ID del curso existente en Canvas |
| `modelo_instruccional` | string | ❌ | `"Unidades"` o `"Nuevo sistema"` |
| `nivel_formacion` | string | ❌ | `"Pregrado"` o `"Posgrado"` |

**Response `202 Accepted`:**
```json
{
  "task_id": "291bc60f-d6f0-4cc5-b883-e13af1af763f",
  "stream_url": "/api/v1/deploy/stream/291bc60f-d6f0-4cc5-b883-e13af1af763f",
  "message": "Despliegue iniciado. Conecta al stream SSE para monitorear el progreso."
}
```

**Flujo post-respuesta:**
```
1. Guardar el task_id
2. Conectar inmediatamente a GET /deploy/stream/{task_id}
3. Escuchar los ProgressEvents hasta status=completed o status=failed
```

---

### `GET /deploy/stream/{task_id}`
**Stream SSE del progreso en tiempo real**

Abre una conexión Server-Sent Events. Emite ProgressEvents hasta
que el despliegue termina. El cliente debe conectar con `EventSource`.

**Path params:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `task_id` | string (UUID) | ID retornado por `POST /deploy` |

**Response `200 OK` — `text/event-stream`:**

La conexión emite eventos en formato SSE. Cada evento tiene esta estructura:

```
data: {"step":0,"total_steps":5,"message":"Iniciando proceso","percentage":0.0,"status":"pending","detail":null,"course_id":null,"error":null}

data: {"step":1,"total_steps":5,"message":"Creando curso en Canvas","percentage":20.0,"status":"running","detail":null,"course_id":96142,"error":null}

: heartbeat

data: {"step":3,"total_steps":5,"message":"Subiendo archivos al aula","percentage":45.0,"status":"running","detail":"Archivo 97 de 194","course_id":96142,"error":null}

data: {"step":5,"total_steps":5,"message":"¡Aula virtual desplegada exitosamente!","percentage":100.0,"status":"completed","detail":null,"course_id":96142,"error":null}
```

**Campos del ProgressEvent:**

| Campo | Tipo | Descripción |
|---|---|---|
| `step` | integer (0-5) | Paso actual del proceso |
| `total_steps` | integer | Total de pasos (siempre 5) |
| `message` | string | Descripción legible del paso |
| `percentage` | float (0-100) | Porcentaje de avance |
| `status` | string | `pending`, `running`, `completed`, `failed`, `cancelled` |
| `detail` | string \| null | Información adicional del paso |
| `course_id` | integer \| null | ID del curso Canvas (disponible desde paso 1) |
| `error` | string \| null | Mensaje de error (solo en status=failed) |

**Pasos del proceso:**

| Step | Mensaje | Porcentaje |
|---|---|---|
| 0 | Iniciando proceso | 0% |
| 1 | Creando/verificando curso en Canvas | 20% |
| 2 | Procesando archivo ZIP | 35% |
| 3 | Subiendo archivos al aula | 35%→65% |
| 4 | Actualizando páginas del curso | 85% |
| 5 | ¡Aula virtual desplegada exitosamente! | 100% |

**Heartbeat:**
Cada 10 segundos se emite `: heartbeat` para mantener la conexión
activa durante pasos largos (migración de plantilla, subida masiva).

**Response `404`:** Si el `task_id` no existe o ya expiró.

---

### `POST /deploy/cancel/{task_id}`
**Cancelar un despliegue en curso**

Inyecta `CancelledError` en el asyncio.Task del orquestador.
El proceso se detiene en la siguiente operación async y emite
un ProgressEvent con `status=cancelled`.

**Path params:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `task_id` | string (UUID) | ID de la tarea a cancelar |

**Response `200 OK`:**
```json
{
  "task_id": "291bc60f-d6f0-4cc5-b883-e13af1af763f",
  "message": "Cancelación solicitada. El proceso se detendrá en breve."
}
```

**Response `404`:** Tarea no encontrada.
**Response `409`:** La tarea ya terminó o ya fue cancelada.

> Los archivos subidos a Canvas antes de la cancelación permanecen en el curso.

---

### `GET /deploy/verify/{course_id}`
**Verificar la integridad del aula desplegada**

Realiza 3 consultas paralelas a Canvas y retorna un reporte
de integridad con semáforo de resultado.

**Path params:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `course_id` | integer | ID del curso Canvas a verificar |

**Response `200 OK`:**
```json
{
  "course_id": 96142,
  "course_name": "Procedimientos Judiciales",
  "course_url": "https://poli.instructure.com/courses/96142",
  "resultado": "success",
  "resumen": {
    "paginas_ok": 12,
    "paginas_total": 12,
    "porcentaje_paginas": 100.0,
    "front_con_contenido": true,
    "actividades_con_pdf": 4,
    "actividades_total": 4
  },
  "paginas": [
    {"slug": "front-del-curso",               "titulo": "Front del curso",          "existe": true},
    {"slug": "inicio-presentacion",           "titulo": "Presentación",             "existe": true},
    {"slug": "unidad-1-material-fundamental", "titulo": "Material Fundamental U1",  "existe": true}
  ]
}
```

**Valores de `resultado`:**

| Valor | Condición |
|---|---|
| `success` | Todas las páginas existen y el front tiene contenido |
| `warning` | Faltan 1-3 páginas institucionales |
| `error` | Faltan más de 3 páginas institucionales |

**Páginas institucionales verificadas (12 en total):**
```
front-del-curso · inicio-presentacion · cierre-retroalimentacion
material-de-trabajo · unidad-{1-4}-material-fundamental
unidad-{1-4}-complementario
```

---

## Endpoints de Auditoría

### `GET /audit`
**Historial paginado de despliegues**

**Query params:**

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `limite` | integer | 50 | Máximo de registros a retornar (1-200) |
| `offset` | integer | 0 | Desplazamiento para paginación |
| `estado` | string | null | Filtrar: `completed`, `failed`, `cancelled` |

**Response `200 OK`:**
```json
{
  "total": 24,
  "limite": 50,
  "offset": 0,
  "entradas": [
    {
      "task_id": "291bc60f...",
      "course_id": 96142,
      "course_name": "Procedimientos Judiciales",
      "zip_filename": "ESC535.zip",
      "archivos_subidos": 194,
      "duracion_display": "4m 32s",
      "estado": "completed",
      "estado_display": "✅ Exitoso",
      "iniciado_en": "2026-05-10T14:23:00Z",
      "modelo_instruccional": "Unidades",
      "nivel_formacion": "Pregrado"
    }
  ]
}
```

---

### `GET /audit/export`
**Exportar historial completo como Excel**

Genera y descarga un archivo `.xlsx` con dos hojas:
- **Historial de despliegues** — detalle de cada despliegue con colores por estado
- **Resumen** — estadísticas agregadas (total, tasa de éxito, duración promedio)

**Response `200 OK`:**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="reporte_despliegues_20260510_1423.xlsx"
```

No requiere parámetros. Exporta todos los registros históricos.

---

## Endpoint de Benchmark

### `POST /benchmark`
**Medir tiempos de procesamiento local**

Ejecuta el pipeline completo de procesamiento sin llamar a Canvas.
Mide el tiempo de cada etapa para documentación de rendimiento.

**Request:** `multipart/form-data`

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `zip_file` | File (.zip) | ✅ | ZIP a procesar |
| `excel_file` | File (.xlsx) | ❌ | Excel del Guion |

**Response `200 OK`:**
```json
{
  "zip_filename": "ESC535.zip",
  "total_archivos": 194,
  "total_size_mb": 45.2,
  "scorm_detectados": 2,
  "total_procesamiento_display": "1.8 s",
  "etapas": [
    {
      "nombre": "Extracción ZIP",
      "duracion_ms": 1234.5,
      "duracion_display": "1.23 s",
      "detalle": "194 archivos extraídos (45.2 MB)",
      "exitosa": true
    },
    {
      "nombre": "Normalización",
      "duracion_ms": 89.3,
      "duracion_display": "89 ms",
      "detalle": "3 carpeta(s) renombrada(s), 2 PDF(s) renombrado(s)",
      "exitosa": true
    },
    {
      "nombre": "Detección SCORM",
      "duracion_ms": 12.1,
      "duracion_display": "12 ms",
      "detalle": "2 paquetes Storyline detectados → U3: 2 paquete(s)",
      "exitosa": true
    },
    {
      "nombre": "Lectura Guion Excel",
      "duracion_ms": 45.7,
      "duracion_display": "46 ms",
      "detalle": "4 unidades | video_inicial=✓ | videos_intro=4 | podcasts=1",
      "exitosa": true
    }
  ]
}
```

---

## Endpoint de Salud

### `GET /health`
**Verificar que el servidor está operativo**

**Response `200 OK`:**
```json
{
  "status": "ok",
  "service": "Canvas LMS Automation API",
  "version": "1.0.0"
}
```

Usado por herramientas de monitoreo y por el pipeline de CI
para verificar que el servidor arrancó correctamente.

---

## Referencia de IDs de plantillas Canvas

| Diseño Instruccional | Nivel | Tipología | ID Canvas |
|---|---|---|---|
| Unidades | Posgrado | Teórico | 69243 |
| Unidades | Posgrado | Teórico-Práctico | 69239 |
| Unidades | Pregrado | Teórico | 63449 |
| Unidades | Pregrado | Teórico-Práctico | 63801 |
| Unidades | Transversal | Práctica 16 sem | 69238 |
| Unidades | Transversal | Práctica 8 sem | 63888 |
| Nuevo sistema | Pregrado | Teórico | 96005 |
| Nuevo sistema | Pregrado | Teórico-Práctico | 96005 |
| Nuevo sistema | Pregrado | Práctica | 96006 |
| Nuevo sistema | Posgrado | Fundamentación | 96007 |
| Nuevo sistema | Posgrado | Profundización | 96008 |

---

## Slugs institucionales de páginas Canvas

Páginas que el sistema crea o actualiza automáticamente en cada curso:

```
front-del-curso
inicio-presentacion
cierre-retroalimentacion
material-de-trabajo
unidad-1-material-fundamental    unidad-1-complementario
unidad-2-material-fundamental    unidad-2-complementario
unidad-3-material-fundamental    unidad-3-complementario
unidad-4-material-fundamental    unidad-4-complementario
unidad-{n}-material-interactivo-{num}         ← Storyline MF
material-de-trabajo-interactivo-{num}         ← Storyline MT
unidad-{n}-material-de-trabajo-interactivo-{num}  ← Storyline MT con unidad
```


## Herramientas de prueba

### Swagger UI — Documentación interactiva

La API expone documentación interactiva autogenerada por FastAPI en:

```
https://canvas-aulas-api.onrender.com/docs
```

Desde Swagger UI puedes explorar todos los endpoints, ver sus parámetros
y ejecutar requests directamente en el navegador sin herramientas adicionales.

### Colección de Postman

Para pruebas automatizadas con validaciones y flujo completo, importa la
colección oficial del proyecto:

* **[📥 Descargar colección Postman](https://charlie-1572114.postman.co/workspace/Charlie's-Workspace~4ddae0bd-d394-42e3-86e5-beba8b68a2e1/collection/43848137-fcae5987-0cb9-4386-b10b-d21b477a380b?action=share&creator=43848137)**
* **[🌐 Ver colección pública](https://documenter.getpostman.com/view/43848137/2sBXqRiwQ2)**

La colección incluye:
- Variables de entorno configuradas (`base_url`, `session_id`)
- Login automático que guarda el `session_id` para todos los requests
- Tests de validación por endpoint
- Ejemplos de respuesta documentados

**Flujo de prueba recomendado:**
1. Ejecutar **01 — Autenticación → Login** primero
2. El `session_id` se guarda automáticamente
3. Ejecutar los endpoints en el orden de las carpetas