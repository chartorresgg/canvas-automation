# Canvas LMS Automation App

Aplicación web institucional para automatizar el montaje de **Aulas Máster** en Canvas LMS del Politécnico Grancolombiano. Reduce el tiempo de montaje de 240 minutos a 25 minutos por aula — optimización del **89.58%**.

Desarrollado como Práctica Empresarial — Ingeniería de Sistemas, Politécnico Grancolombiano, período 2026-1.

---

## 🌐 URLs de producción

| Servicio | URL |
|---|---|
| Frontend (React + Vercel) | https://canvas-automation.vercel.app |
| Backend (FastAPI + Render) | https://canvas-aulas-api.onrender.com |
| Documentación Swagger UI | https://canvas-aulas-api.onrender.com/docs |
| Health check | https://canvas-aulas-api.onrender.com/api/v1/health |

> **Nota Render Free Tier:** El primer request puede tardar 30-60 segundos (cold start). Los siguientes son inmediatos.

---

## Stack tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Backend — Lenguaje | Python | 3.11 |
| Backend — Framework | FastAPI | 0.136.1 |
| Backend — Servidor | Uvicorn (ASGI) | 0.34.0 |
| Backend — Validación | Pydantic | 2.13.3 |
| Backend — HTTP client | httpx | 0.28.1 |
| Backend — Persistencia | SQLite + aiosqlite | 0.22.1 |
| Backend — Excel | openpyxl | 3.1.5 |
| Frontend — Librería | React | 19.2.5 |
| Frontend — Lenguaje | TypeScript | 6.0.3 |
| Frontend — Build | Vite | 8.0.10 |
| Frontend — Estilos | Tailwind CSS | 3.4.19 |
| Frontend — Componentes | shadcn/ui sobre Radix UI | — |
| Frontend — HTTP | Axios | 1.16.0 |
| Integración | Canvas LMS REST API | v1 |
| CI/CD | GitHub Actions | gitleaks · pytest · tsc |
| Deploy backend | Render Web Service | Free Tier |
| Deploy frontend | Vercel CDN | Hobby |

> Versiones resueltas desde `backend/requirements.txt` y `frontend/package-lock.json`
> el 8 de septiembre de 2026. Al actualizar dependencias, actualizar también esta tabla.

---

## Requisitos previos (desarrollo local)

- Python 3.11 (versión con la que corre el CI y el despliegue)
- Node.js 20+
- Token de acceso a la API de Canvas LMS (generado desde el perfil del usuario en poli.instructure.com)

> En producción, cada analista ingresa su propio token a través de la interfaz web. No se requiere configuración local de variables de entorno para los usuarios finales.

---

## Variables de entorno

### Backend — archivo `backend/.env`

```env
CANVAS_BASE_URL=https://poli.instructure.com/api/v1/
CANVAS_ACCOUNT_ID=1
AUDIT_DB_PATH=~/.canvas-automation/audit_log.db
FRONTEND_URL=https://canvas-automation.vercel.app
```

> `AUDIT_DB_PATH` es opcional. Si se omite, la base de auditoría se crea en
> `~/.canvas-automation/audit_log.db`, **fuera del repositorio**: contiene
> registros reales de despliegues (IDs y nombres de cursos institucionales)
> que nunca deben versionarse.

> El token de Canvas **no** se almacena en variables de entorno del servidor.
> Cada analista ingresa su token al iniciar sesión. El sistema lo guarda
> en memoria RAM (SessionManager) y nunca lo persiste en disco.

### Frontend — archivo `frontend/.env.local`

```env
VITE_API_URL=http://localhost:8000
```

> En producción, `VITE_API_URL` apunta a la URL de Render (configurada en Vercel Dashboard).

---

## Instalación y ejecución local

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API disponible en: `http://localhost:8000`  
Swagger UI en: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Interfaz disponible en: `http://localhost:5173`

---

## Estructura del proyecto

```
canvas-automation/
├── backend/
│   ├── app/
│   │   ├── domain/                    # Capa 1 — Lógica de negocio pura
│   │   │   ├── interfaces/            # IPageComposer, IAuditRepository
│   │   │   ├── services/              # ZipProcessor, FileNormalizer,
│   │   │   │                          # GuionExcelReader, InteractiveContentDetector
│   │   │   └── value_objects/         # DeploymentConfig, ProgressEvent, AuditEntry
│   │   ├── application/               # Capa 2 — Casos de uso
│   │   │   └── orchestrator.py        # DeploymentOrchestrator (Facade)
│   │   ├── infrastructure/            # Capa 3 — Adaptadores técnicos
│   │   │   ├── canvas/               # http_client.py + 3 Repositories
│   │   │   ├── composers/            # 5 Composers (Strategy) + Factory
│   │   │   └── persistence/          # SQLiteAuditRepository
│   │   ├── presentation/             # Capa 4 — Controladores HTTP
│   │   │   ├── routers/              # deploy, auth, audit, benchmark, health
│   │   │   ├── session_manager.py
│   │   │   ├── task_manager.py
│   │   │   ├── schemas.py
│   │   │   └── dependencies.py
│   │   └── main.py                    # Fábrica de la app FastAPI
│   ├── tests/unit/                    # 434 pruebas automatizadas
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── features/
│       │   ├── deploy/               # Wizard de despliegue (3 pasos)
│       │   ├── audit/                # Historial de despliegues
│       │   └── benchmark/            # Medición de rendimiento
│       ├── components/ui/
│       └── services/api.ts           # Axios + interceptor X-Session-ID
├── docs/                             # Sitio de documentación (MkDocs)
├── .github/workflows/ci.yml          # gitleaks + pytest + TypeScript
├── .gitleaks.toml                    # Reglas de escaneo de secretos
├── render.yaml                        # Config despliegue Render
└── README.md
```

---

## Estructura del ZIP de entrada

```
Archivos/
├── 1. Presentación/          → index.html (iframe)
├── 2. Material fundamental/  → PDFs + carpetas SCORM (story.html)
├── 3. Material de trabajo/   → PDFs descargables
├── 4. Complementos/          → Lecturas complementarias
└── 5. Cierre/                → index.html (iframe)
```

> `FileNormalizer` estandariza nombres automáticamente: "2 Material fundamental" → "2. Material fundamental"

---

## Canvas API

| Parámetro | Valor |
|---|---|
| Base URL | `https://poli.instructure.com/api/v1/` |
| Account ID | `1` |
| Timezone | `America/Bogota` (UTC-5) |

---

## Endpoints (resumen)

| Grupo | Método | Endpoint | Descripción |
|---|---|---|---|
| Auth | POST | `/api/v1/auth/login` | Iniciar sesión con token Canvas |
| Auth | POST | `/api/v1/auth/logout` | Cerrar sesión |
| Auth | GET | `/api/v1/auth/validate` | Verificar sesión activa |
| Health | GET | `/api/v1/health` | Estado del servidor |
| Deploy | POST | `/api/v1/deploy/upload` | Subir archivo ZIP |
| Deploy | POST | `/api/v1/deploy` | Iniciar despliegue (async) |
| Deploy | GET | `/api/v1/deploy/stream/{task_id}` | Stream SSE de progreso |
| Deploy | POST | `/api/v1/deploy/cancel/{task_id}` | Cancelar despliegue |
| Deploy | GET | `/api/v1/deploy/verify/{course_id}` | Verificar integridad |
| Audit | GET | `/api/v1/audit` | Historial de despliegues |
| Audit | GET | `/api/v1/audit/export` | Exportar historial Excel |
| Benchmark | POST | `/api/v1/benchmark` | Medir tiempos locales |

---

## Pruebas

```bash
cd backend
python -m pytest tests/unit/ -v --tb=short
```

Para el reporte de cobertura hace falta instalar `pytest-cov`, que no viene en
`requirements.txt`:

```bash
pip install pytest-cov
python -m pytest tests/unit/ --cov=app --cov-report=term-missing
```

**Estado actual:**

| Indicador | Valor | Verificado |
|---|---|---|
| Pruebas unitarias | 434 pasando · 3 omitidas | 8-sep-2026 |
| Tiempo de ejecución | 16,2 s | 8-sep-2026 |
| Cobertura | 71 % sobre 2.352 líneas ejecutables | última medición conocida |
| Pruebas de integración | Ninguna — `tests/integration/` está vacío | 8-sep-2026 |

> La cobertura no la mide el pipeline de CI. Al no estar `pytest-cov` en las
> dependencias, la cifra proviene de una medición manual anterior y puede haber
> variado.

> Las 434 pruebas son unitarias y simulan Canvas con mocks. Si Canvas cambiara
> el formato de una respuesta, la suite seguiría en verde. Cerrar esa brecha con
> `respx` es un requisito de la Fase 2 (RC-03).

---

## Reglas de arquitectura

- Las dependencias fluyen de exterior → Dominio. El Dominio **nunca** importa FastAPI, httpx ni SQLite.
- Todo acceso a Canvas API va exclusivamente por `infrastructure/canvas/http_client.py`.
- Todo I/O **debe** usar `async/await`, sin operaciones síncronas bloqueantes.
  El trabajo bloqueante inevitable se envuelve en `anyio.to_thread.run_sync`.
- El token de Canvas **nunca** se persiste en disco ni aparece en logs.
- No se hardcodean rutas absolutas del sistema de archivos.
- Todo endpoint nuevo nace exigiendo sesión válida. Las rutas públicas se
  declaran de forma explícita y se justifican; no se heredan por omisión.

---

## Progreso del proyecto

| Sprint | Objetivo | SP planificados | SP completados |
|---|---|---|---|
| Sprint 1 | Modelado y Prototipo Navegable | 19 | 19 ✅ |
| Sprint 2 | Integración con API Canvas | 21 | 21 ✅ |
| Sprint 3 | Automatización y Monitoreo | 18 | 18 ✅ |
| Sprint 4 | Resiliencia y Reportes | 18 | 13 ✅ |
| Sprint 5 | Despliegue en Nube y CI/CD | 8 | 13 ✅ |
| **Total** | | **89** | **79 SP únicos** |

La Fase 1 está cerrada y en operación. La **Fase 2** —en preparación— no amplía
funcionalidad: prepara el aplicativo para ser operado y auditado por la
institución. Sus tres frentes son el endurecimiento de seguridad de la API, la
migración de Vercel y Render a infraestructura institucional en AWS, y la
autenticación mediante SSO sobre Active Directory en reemplazo del token
personal de Canvas.

---

## Estado de seguridad

Controles vigentes:

- **Escaneo de secretos en cada push y pull request** — gitleaks sobre el
  historial completo, con una regla propia para el formato de token de Canvas
  (`.gitleaks.toml`) que la herramienta no reconoce de fábrica.
- **El token de Canvas no se persiste.** Vive en la memoria del proceso durante
  la sesión y nunca toca el disco ni los logs.
- **Identificador de sesión no enumerable** — 32 bytes de `secrets.token_urlsafe`.
- **Protección contra Zip Slip** al extraer el contenido cargado.
- **Orígenes CORS restringidos** por lista explícita, sin comodín.
- **Datos de auditoría fuera del árbol del repositorio** por defecto.

La Fase 2 completa el endurecimiento de la API —autorización por rol, control de
tasa, validación de cargas en el servidor y saneamiento de entradas—, el manejo
de sesiones, la persistencia gestionada del registro de auditoría con atribución
por usuario, y la autenticación SSO sobre Active Directory.

> **Este aplicativo aún no debe considerarse apto para operación institucional
> sostenida.** Los requisitos que habilitan esa condición están levantados en el
> documento de evaluación técnica de la Fase 2.
>
> ¿Encontraste un problema de seguridad? Repórtalo de forma privada al autor o
> al área de Ambientes de Aprendizaje, no como issue público.

---

## Contexto académico

| Campo | Valor |
|---|---|
| Institución | Politécnico Grancolombiano |
| Facultad | Ingeniería, Diseño e Innovación |
| Programa | Ingeniería de Sistemas — Práctica Empresarial |
| Autor | Carlos Eduardo Guzmán Torres |
| Tutor académico | Javier Fernando Niño Velásquez |
| Asesor técnico | Wilson Eduardo Soto Forero |
| Área institucional | Ambientes de Aprendizaje |
| Período | 2026-1 |

---

## Documentación

📚 **Sitio de documentación:** https://chartorresgg.github.io/canvas-automation/

- 🚀 [Primeros pasos](https://chartorresgg.github.io/canvas-automation/primeros-pasos/)
- 📖 [Arquitectura](https://chartorresgg.github.io/canvas-automation/arquitectura/)
- 📊 [Diagramas UML](https://chartorresgg.github.io/canvas-automation/diagramas-uml/)
- 📡 [Referencia de API](https://chartorresgg.github.io/canvas-automation/referencia-api/)
- 🔧 [Convenciones](https://chartorresgg.github.io/canvas-automation/convenciones/)
- 🐛 [Solución de problemas](https://chartorresgg.github.io/canvas-automation/solucion-de-problemas/)

En el repositorio:

- 🤖 [`CLAUDE.md`](CLAUDE.md) y [`.cursorrules`](.cursorrules) — contexto de
  arquitectura y reglas que deben seguir los asistentes de código.
