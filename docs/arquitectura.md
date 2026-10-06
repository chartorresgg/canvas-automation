# Architecture

Documentación de la arquitectura técnica del sistema Canvas LMS Automation App.

---

## Visión general

El sistema implementa una arquitectura **cliente-servidor** desacoplada:

```
┌─────────────────────┐         HTTP / REST          ┌─────────────────────┐
│   Frontend          │ ◄──────────────────────────► │   Backend           │
│   React 18 + Vite   │         SSE (stream)          │   FastAPI + Python  │
│   localhost:5173    │                               │   localhost:8000    │
└─────────────────────┘                               └──────────┬──────────┘
                                                                 │
                                                          Canvas REST API
                                                     poli.instructure.com/api/v1/
```

El frontend nunca llama directamente a Canvas. Todo pasa por el backend,
que gestiona autenticación, reintentos, paginación y protocolo de subida
de archivos en 3 fases.

---

## Clean Architecture — 4 capas

El backend sigue estrictamente el patrón **Clean Architecture** de Robert C. Martin.
La regla fundamental: **las dependencias solo apuntan hacia adentro**.

```
┌─────────────────────────────────────────────────────────────┐
│  PRESENTACIÓN                                               │
│  FastAPI Routers · Schemas · TaskManager · Dependencies     │
├─────────────────────────────────────────────────────────────┤
│  APLICACIÓN                                                 │
│  DeploymentOrchestrator (Facade)                            │
├─────────────────────────────────────────────────────────────┤
│  INFRAESTRUCTURA                                            │
│  CanvasHttpClient · 3 Repositorios · 5 Composers           │
├─────────────────────────────────────────────────────────────┤
│  DOMINIO  ← núcleo, sin dependencias externas               │
│  Servicios · Interfaces · Value Objects                     │
└─────────────────────────────────────────────────────────────┘
```

### Capa de Dominio — `backend/app/domain/`

Contiene la lógica de negocio pura. No importa nada de FastAPI, Canvas ni bases de datos.

| Módulo | Clase | Responsabilidad |
|---|---|---|
| `services/` | `ZipProcessor` | Extracción y normalización de ZIPs |
| `services/` | `FileNormalizer` | Renombramiento de carpetas y PDFs al estándar institucional |
| `services/` | `GuionExcelReader` | Lectura del Excel de Guion — URLs Vimeo, SoundCloud, párrafos |
| `services/` | `InteractiveContentDetector` | Detección de paquetes Storyline en el FileMap |
| `interfaces/` | `IPageComposer` | Contrato Strategy para generación de HTML |
| `interfaces/` | `IAuditRepository` | Contrato Repository para persistencia de auditoría |
| `value_objects/` | `DeploymentConfig` | Configuración inmutable de un despliegue |
| `value_objects/` | `ProgressEvent` | Evento de progreso para SSE |
| `value_objects/` | `AuditEntry` | Registro inmutable de un despliegue ejecutado |

### Capa de Aplicación — `backend/app/application/`

Un único componente: el orquestador. Coordina el flujo completo delegando
en los colaboradores. No conoce los detalles de Canvas ni de HTTP.

| Clase | Patrón | Responsabilidad |
|---|---|---|
| `DeploymentOrchestrator` | Facade | Coordina los 5 pasos del despliegue emitiendo ProgressEvents |

### Capa de Infraestructura — `backend/app/infrastructure/`

Implementaciones concretas que hablan con el mundo exterior.

**Canvas API (`infrastructure/canvas/`):**

| Clase | Responsabilidad |
|---|---|
| `CanvasHttpClient` | HTTP async con reintentos, backoff exponencial y paginación |
| `CourseRepository` | Crear curso, copiar plantilla, polling de migración |
| `FileRepository` | Subida masiva con protocolo de 3 fases, reintentos ×3 |
| `PageRepository` | Actualizar páginas wiki, vincular PDFs a actividades |

**Composers (`infrastructure/composers/`):**

| Clase | Página Canvas que genera |
|---|---|
| `IframeComposer` | Presentación y Cierre (iframe al HTML del ZIP) |
| `MaterialFundamentalComposer` | Unidad N — Material Fundamental |
| `ComplementaryPageComposer` | Unidad N — Complementario |
| `FrontPageComposer` | Front del curso (con datos del Excel) |
| `MaterialDeTrabajoComposer` | Material de Trabajo (PDFs + Storylines) |
| `PageComposerFactory` | Fábrica que instancia el Composer correcto |

**Persistencia (`infrastructure/persistence/`):**

| Clase | Responsabilidad |
|---|---|
| `SQLiteAuditRepository` | Registro histórico de despliegues en SQLite |

### Capa de Presentación — `backend/app/presentation/`

| Módulo | Responsabilidad |
|---|---|
| `routers/deploy.py` | Endpoints de despliegue (upload, deploy, stream, cancel, verify) |
| `routers/audit.py` | Endpoints de historial y exportación Excel |
| `routers/benchmark.py` | Endpoint de benchmark de procesamiento local |
| `routers/health.py` | Health check del servidor |
| `task_manager.py` | Registro de queues SSE y referencias asyncio.Task |
| `schemas.py` | Schemas Pydantic de request/response |
| `dependencies.py` | Inyección de dependencias (repositorios, orquestador) |

---

## Patrones de diseño aplicados

### Facade — `DeploymentOrchestrator`

Expone una única operación `deploy()` que internamente coordina
7 colaboradores distintos. El router FastAPI no conoce ninguno de ellos.

```python
# El router solo ve esto:
async for event in orchestrator.deploy(config):
    queue.put_nowait(event)

# Internamente el orquestador coordina:
# CourseRepository → FileRepository → InteractiveContentDetector
# → PageRepository → Composers → AuditRepository
```

### Strategy — `IPageComposer`

Permite generar HTML de distintos tipos de página sin que el orquestador
conozca los detalles de cada formato.

```
IPageComposer (interfaz)
    ├── IframeComposer
    ├── MaterialFundamentalComposer
    ├── ComplementaryPageComposer
    ├── FrontPageComposer
    └── MaterialDeTrabajoComposer
```

### Factory — `PageComposerFactory`

Centraliza la creación de Composers. El orquestador pide un tipo y
recibe la instancia correcta sin conocer las clases concretas.

```python
composer = factory.create(PageType.MATERIAL_FUNDAMENTAL)
html = composer.compose(course_id, ctx)
```

### Repository — `CourseRepository`, `FileRepository`, `PageRepository`

Abstraen las llamadas a Canvas API detrás de una interfaz de dominio.
El orquestador habla de "cursos", "archivos" y "páginas", no de
endpoints HTTP ni de protocolos de autenticación.

---

## Flujo completo de un despliegue

```
Analista sube ZIP + Excel
         │
         ▼
POST /api/v1/deploy ──► BackgroundTask
         │                    │
         ▼                    ▼
202 Accepted            DeploymentOrchestrator.deploy()
+ task_id                     │
         │               Paso 1: Crear/verificar curso Canvas
         ▼               Paso 2: Extraer y normalizar ZIP
GET /api/v1/deploy/      Paso 3: Subir 100-900 archivos a Canvas
    stream/{task_id}     Paso 4: Detectar SCORM
         │                       Crear páginas HTML
         │                       Vincular PDFs a actividades
         ▼               Paso 5: Completado
ProgressEvents SSE  ◄────────────────────────────────────
(tiempo real)
         │
         ▼
Frontend muestra barra de progreso
Al completar: VerificationPanel consulta integridad del curso
```

---

## Comunicación en tiempo real — SSE

El sistema usa **Server-Sent Events** para transmitir el progreso
sin que el cliente tenga que hacer polling.

```
Backend (asyncio.Queue)          Frontend (EventSource)
         │                                │
         │  data: {"step":1,"pct":20}     │
         │ ──────────────────────────► │
         │  data: {"step":3,"pct":45}     │
         │ ──────────────────────────► │
         │  : heartbeat                   │  ← cada 10s para mantener conexión
         │ ──────────────────────────► │
         │  data: {"status":"completed"}  │
         │ ──────────────────────────► │
         │  [conexión cerrada]            │
```

---

## Reglas de dependencias — qué puede importar qué

```
Dominio:          NO puede importar de Aplicación, Infraestructura ni Presentación
Aplicación:       Puede importar de Dominio únicamente
Infraestructura:  Puede importar de Dominio únicamente
Presentación:     Puede importar de Aplicación, Dominio e Infraestructura
```

Estas reglas se verifican en cada code review. Ningún módulo de dominio
importa `fastapi`, `httpx`, `aiosqlite` ni ninguna librería externa.

---

## Preparación para escala — decisiones de arquitectura

| Decisión | Implementación actual | Migración futura |
|---|---|---|
| Auditoría | SQLite local (`data/audit_log.db`) | `PostgresAuditRepository` implementando `IAuditRepository` — cambiar 1 línea en `dependencies.py` |
| Token Canvas | Variable de entorno `.env` | Campo de contraseña en `LoginPage` — `SessionManager` en backend |
| Despliegue | Local (puerto 8000) | Railway (backend) + Vercel (frontend) — sin cambios en el código |
| Auth | Token único de administrador | OAuth Canvas con Developer Key institucional |