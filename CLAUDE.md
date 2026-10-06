# Canvas LMS Automation — Contexto del Proyecto

## Descripción
Aplicación web institucional para automatizar el montaje de Aulas Máster en
Canvas LMS del Politécnico Grancolombiano. Reduce el tiempo de montaje de 240 a
25 minutos por aula. Desarrollada como Práctica Empresarial — Ingeniería de
Sistemas, período 2026-1.

## Estado actual
La Fase 1 está cerrada y en operación. La **Fase 2** está en preparación: no
amplía funcionalidad, prepara el aplicativo para ser operado y auditado por la
institución. Sus tres frentes:

1. Endurecimiento de seguridad de la API (autorización, control de tasa, límites
   de carga, saneamiento de entradas).
2. Migración de Vercel y Render a infraestructura institucional en AWS, con
   persistencia gestionada.
3. Autenticación SSO sobre Active Directory, en reemplazo del token personal de
   Canvas como credencial de ingreso.

El análisis detallado de necesidades se mantiene fuera de este repositorio
público.

## Stack tecnológico
Versiones reales, resueltas desde `requirements.txt` y `package-lock.json`
(8 de septiembre de 2026). Verificar antes de citarlas en documentación.

- Backend: Python 3.11, FastAPI 0.136.1, Uvicorn 0.34.0, Pydantic 2.13.3,
  httpx 0.28.1 (async), aiosqlite 0.22.1, openpyxl 3.1.5, anyio 4.13.0
- Frontend: React 19.2.5, TypeScript 6.0.3, Vite 8.0.10, Tailwind CSS 3.4.19,
  shadcn/ui sobre Radix UI, Axios 1.16.0
- Integración: Canvas LMS REST API v1
- Base de datos: SQLite (solo audit log; migra a PostgreSQL en la Fase 2)
- CI: GitHub Actions — gitleaks, pytest, `tsc --noEmit`

## Arquitectura — Clean Architecture (4 capas)
Las dependencias fluyen de exterior hacia el dominio. El dominio no importa
FastAPI, httpx ni SQLite en ningún archivo, y esa regla se mantiene.

- **Presentación** — Routers FastAPI (`auth`, `deploy`, `audit`, `benchmark`,
  `health`), `SessionManager`, `TaskManager`, y la SPA de React
- **Aplicación** — `DeploymentOrchestrator` (Facade), en `orchestrator.py`
- **Dominio** — `ZipProcessor`, `FileNormalizer`, `GuionExcelReader`,
  `InteractiveContentDetector`, interfaces `IPageComposer` e `IAuditRepository`
- **Infraestructura** — `CanvasHttpClient`, los tres repositorios de Canvas,
  cinco composers con su factory, `SQLiteAuditRepository`

## Canvas API
- Base URL: https://poli.instructure.com/api/v1/
- Account ID: 1
- Auth: Bearer Token. En producción lo aporta el analista al iniciar sesión y
  vive en `SessionManager` (memoria). `CANVAS_ACCESS_TOKEN` solo se usa en
  desarrollo local.
- Timezone: Colombia UTC-5 (`America/Bogota`)

## Estructura de carpetas clave
- `backend/app/domain/`          → lógica de negocio pura
- `backend/app/application/`     → orquestador (facade)
- `backend/app/infrastructure/`  → repositorios Canvas + composers + persistencia
- `backend/app/presentation/`    → routers FastAPI, sesiones, tareas
- `backend/app/main.py`          → fábrica de la aplicación FastAPI
- `backend/tests/unit/`          → 434 pruebas; `tests/integration/` está vacío
- `frontend/src/features/`       → módulos por funcionalidad
- `frontend/src/services/`       → cliente HTTP y SSE
- `docs/`                        → análisis y documentación de proyecto

## Patrones de diseño aplicados
- **Facade**: `DeploymentOrchestrator` (`application/orchestrator.py`)
- **Strategy**: `IPageComposer` + `IframeComposer`, `MaterialFundamentalComposer`,
  `MaterialDeTrabajoComposer`, `FrontPageComposer`, `ComplementaryPageComposer`
- **Factory**: `PageComposerFactory`
- **Repository**: `CourseRepository`, `FileRepository`, `PageRepository`,
  `SQLiteAuditRepository`

## Convenciones de código
- Python: snake_case, type hints obligatorios en toda función, docstrings en
  español
- TypeScript: PascalCase para componentes React, camelCase para funciones y
  variables
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`,
  `chore:`, `test:`)
- Nunca poner lógica de negocio en los routers de FastAPI
- Nunca hacer llamadas HTTP directamente desde el orquestador — siempre vía
  repositorios
- Todo acceso a Canvas pasa exclusivamente por
  `infrastructure/canvas/http_client.py`
- Todo I/O debe ser `async`/`await`. Parte del código de la Fase 1 no lo
  cumple; no replicar ese patrón. Al tocar código bloqueante, envolverlo en
  `anyio.to_thread.run_sync`.

## Reglas de seguridad
Estas reglas rigen todo código nuevo. La Fase 1 no las cumple en su totalidad y
alinearla es precisamente el objeto de la Fase 2 — no tomar el código existente
como referencia de lo correcto en estos puntos.

1. **Todo endpoint nace exigiendo sesión válida.** Una ruta pública se declara de
   forma explícita y se justifica en el código; nunca queda pública por omisión.
2. **Autenticar no es autorizar.** Verificar además el rol antes de exponer datos
   de otros usuarios o funciones administrativas.
3. **Validar en el servidor lo que valida el navegador.** Tamaños, extensiones y
   formatos. Una validación que solo existe en el frontend no existe.
4. **Nunca construir una ruta de disco concatenando un nombre de archivo
   recibido del cliente.** Generar un nombre seguro y confirmar con
   `Path.resolve()` que el destino queda dentro del directorio de trabajo.
5. **Limpiar los recursos en `finally`,** nunca solo en el camino de error.
   `ZipProcessor.cleanup()` ya existe y está probado.
6. **Ningún secreto en el repositorio, en logs ni en mensajes de error.** El
   token de Canvas no se registra jamás, ni completo ni parcial.
7. **Antes de extraer un archivo comprimido,** validar tamaño descomprimido total
   y ratio de compresión, además de la protección contra Zip Slip que ya existe.
8. **Todo despliegue debe quedar atribuido a un usuario** en el registro de
   auditoría.

## Comandos
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
python -m pytest tests/unit/ -v --tb=short

# Frontend
cd frontend && npm install
npm run dev
npx tsc --noEmit

# Escaneo de secretos sobre el historial completo
gitleaks detect --source . --config .gitleaks.toml --log-opts="--all" -v
```

## Notas para asistentes de código
- El canal de progreso usa SSE, no WebSockets ni polling.
- `pytest-cov` no está en `requirements.txt`; instalarlo aparte si se pide
  cobertura.
- No renombrar el servicio `canvas-aulas-api` de Render: cambia la URL pública y
  rompe `VITE_API_URL` en Vercel.
- El repositorio es público. No documentar en archivos versionados el detalle
  explotable de vulnerabilidades abiertas en producción.
