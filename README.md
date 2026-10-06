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
| Backend — Framework | FastAPI | Latest |
| Backend — Servidor | Uvicorn (ASGI) | Latest |
| Backend — Validación | Pydantic | v2 |
| Backend — HTTP client | httpx | Latest |
| Backend — Persistencia | SQLite + aiosqlite | Latest |
| Backend — Excel | openpyxl | Latest |
| Frontend — Librería | React | 18 |
| Frontend — Lenguaje | TypeScript | 5 |
| Frontend — Build | Vite | 5 |
| Frontend — Estilos | Tailwind CSS | 3 |
| Frontend — HTTP | Axios | Latest |
| Integración | Canvas LMS REST API | v1 |
| CI/CD | GitHub Actions | — |
| Deploy backend | Render Web Service | Free Tier |
| Deploy frontend | Vercel CDN | Hobby |

---

## Requisitos previos (desarrollo local)

- Python 3.11+
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
│   │   │   └── deployment_orchestrator.py
│   │   ├── infrastructure/            # Capa 3 — Adaptadores técnicos
│   │   │   ├── canvas/               # CanvasHttpClient + 3 Repositories
│   │   │   ├── composers/            # 5 Composers (Strategy) + Factory
│   │   │   └── persistence/          # SQLiteAuditRepository
│   │   └── presentation/             # Capa 4 — Controladores HTTP
│   │       ├── routers/              # deploy, auth, audit, benchmark, health
│   │       ├── session_manager.py
│   │       ├── task_manager.py
│   │       ├── schemas.py
│   │       └── dependencies.py
│   ├── tests/unit/                    # 434 tests automatizados
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── features/
│       │   ├── deploy/               # Wizard de despliegue (3 pasos)
│       │   ├── audit/                # Historial de despliegues
│       │   └── benchmark/            # Medición de rendimiento
│       ├── components/ui/
│       └── services/api.ts           # Axios + interceptor X-Session-ID
├── .github/workflows/ci.yml          # GitHub Actions: pytest + TypeScript
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
pytest tests/unit/ -v --tb=short

# Con reporte de cobertura
pytest tests/unit/ --cov=app --cov-report=term-missing
```

**Estado actual:**
- ✅ 434 tests passing · 3 skipped
- 📊 71% cobertura · 2.352 líneas ejecutables
- ⏱ 16.35s ejecución · 31s pipeline CI/CD completo

---

## Reglas de arquitectura

- Las dependencias fluyen de exterior → Dominio. El Dominio **nunca** importa FastAPI, httpx ni SQLite.
- Todo acceso a Canvas API va exclusivamente por `infrastructure/canvas/canvas_client.py`.
- Todo I/O usa `async/await` — sin operaciones síncronas bloqueantes.
- El token de Canvas **nunca** se persiste en disco ni aparece en logs.
- No se hardcodean rutas absolutas del sistema de archivos.

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
