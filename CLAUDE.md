# Canvas LMS Automation — Contexto del Proyecto

## Descripción
Aplicación web para automatizar el montaje de aulas virtuales en Canvas LMS
del Politécnico Grancolombiano. Proyecto de Grado — Ingeniería de Sistemas.

## Stack tecnológico
- Backend: Python 3.10+, FastAPI, Uvicorn ASGI, Pydantic v2, httpx (async)
- Frontend: React 18, TypeScript, Vite 5, Tailwind CSS 3, shadcn/ui
- Integración: Canvas REST API (poli.instructure.com/api/v1/)
- Base de datos: SQLite (audit log únicamente)
- Control de versiones: Git + GitHub

## Arquitectura — Clean Architecture (4 capas)
- Presentación: FastAPI Routers + React SPA
- Aplicación: DeploymentOrchestrator (patrón Facade)
- Dominio: ZipProcessor, FileNormalizer, IPageComposer (patrón Strategy), InteractiveContentDetector
- Infraestructura: CanvasHttpClient, CourseRepository, FileRepository, PageRepository (patrón Repository)

## Canvas API
- Base URL: https://poli.instructure.com/api/v1/
- Account ID: 1
- Auth: Bearer Token en variable de entorno CANVAS_ACCESS_TOKEN
- Timezone: Colombia UTC-5

## Estructura de carpetas clave
- backend/app/domain/          → lógica de negocio pura
- backend/app/application/     → orquestador (facade)
- backend/app/infrastructure/  → repositorios Canvas + composers
- backend/app/presentation/    → FastAPI routers
- frontend/src/features/       → módulos por funcionalidad
- frontend/src/services/       → cliente HTTP y SSE

## Patrones de diseño aplicados
- Facade: DeploymentOrchestrator (orchestrator.py)
- Strategy: IPageComposer + IframeComposer, MaterialFundamentalComposer, FrontPageComposer, ComplementaryPageComposer
- Factory: PageComposerFactory
- Repository: CourseRepository, FileRepository, PageRepository

## Convenciones de código
- Python: snake_case, type hints obligatorios en toda función, docstrings en español
- TypeScript: PascalCase para componentes React, camelCase para funciones y variables
- Commits: Conventional Commits (feat:, fix:, docs:, refactor:, chore:, test:)
- Nunca poner lógica de negocio en los routers de FastAPI
- Nunca hacer llamadas HTTP directamente desde el orquestador (siempre via repositorios)
- Todo I/O debe ser async/await

## Sprints activos
- Sprint 1: Arquitectura base, setup, ZipProcessor, FileNormalizer, health check
- Sprint 2: Integración Canvas API, CourseRepository, FileRepository, deploy endpoint
- Sprint 3: Automatización completa, SSE, progreso en tiempo real
- Sprint 4: Resiliencia, pruebas, reportes