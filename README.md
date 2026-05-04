# Canvas Aulas Master

Prototipo de aplicación web para automatizar el montaje de **Aulas Máster** en Canvas LMS del Politécnico Grancolombiano. Reduce el tiempo de montaje manual de 240 minutos a 25 minutos por aula (optimización del 89,58%).

Desarrollado como Práctica Empresarial — Ingeniería de Sistemas, Politécnico Grancolombiano, periodo 2026-1.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3 · FastAPI · httpx · SQLAlchemy |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS |
| Integración | Canvas LMS REST API v1 |

---

## Requisitos previos

- Python 3.11+
- Node.js 20+
- Acceso a la API de Canvas LMS (token de servicio)

---

## Variables de entorno

Crea un archivo `.env` en la carpeta `backend/` con las siguientes variables:

```env
CANVAS_ACCESS_TOKEN=tu_token_aqui
CANVAS_BASE_URL=https://poli.instructure.com/api/v1/
```

> El token nunca debe hardcodearse en el código fuente.

---

## Instalación y ejecución

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

La API quedará disponible en `http://localhost:8000`. La documentación interactiva en `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

La interfaz quedará disponible en `http://localhost:5173`.

---

## Estructura del proyecto

```
canvas-aulas-master/
├── backend/
│   ├── infrastructure/
│   │   └── canvas/
│   │       └── canvas_client.py   # Único punto de acceso a Canvas API
│   └── requirements.txt
├── frontend/
│   └── src/
│       └── App.tsx
└── docs/
    └── documento_practicaempresarial.md
```

---

## Estructura del ZIP de entrada

El sistema procesa archivos ZIP con la siguiente estructura de carpetas:

```
Archivos/
├── 1. Presentación/          → index.html (cargado en iframe)
├── 2. Material fundamental/  → PDFs + carpetas SCORM (story.html)
├── 3. Material de trabajo/   → PDFs descargables
├── 4. Complementos/          → Lecturas complementarias
└── 5. Cierre/                → index.html (cargado en iframe)
```

---

## Canvas API

| Parámetro | Valor |
|---|---|
| Base URL | `https://poli.instructure.com/api/v1/` |
| Account ID | `1` |
| Timezone | `America/Bogota` (UTC-5) |

---

## Pruebas

```bash
cd backend
pytest
```

---

## Reglas de desarrollo

- Todo acceso a Canvas API va exclusivamente por `infrastructure/canvas/canvas_client.py`.
- Los servicios de dominio no importan FastAPI ni httpx directamente.
- Usar `async/await` en todos los endpoints que llamen a Canvas.
- No hardcodear rutas absolutas del sistema de archivos.

---

## Contexto académico

**Institución:** Politécnico Grancolombiano  
**Facultad:** Ingeniería, Diseño e Innovación  
**Programa:** Ingeniería de Sistemas — Opción de Grado  
**Autor:** Carlos Eduardo Guzmán Torres  
**Tutor:** Javier Fernando Niño Velásquez  
**Asesor:** Wilson Eduardo Soto Forero  
**Periodo:** 2026-1
