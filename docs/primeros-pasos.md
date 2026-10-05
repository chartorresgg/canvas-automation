# Getting Started

Guía de configuración del entorno de desarrollo local para
Canvas LMS Automation App.

> **Tiempo estimado de configuración:** 10-15 minutos

---

## Prerrequisitos

Antes de comenzar, verifica que tienes instalado:

| Herramienta | Versión mínima | Verificar con |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | cualquier | `git --version` |

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/chartorresgg/canvas-aulas-master.git
cd canvas-aulas-master
```

---

## 2. Obtener el Token de Canvas LMS

El sistema necesita un token de administrador de Canvas para interactuar
con la API institucional.

**Pasos para obtenerlo:**

1. Inicia sesión en [poli.instructure.com](https://poli.instructure.com)
2. Haz clic en tu foto de perfil → **Cuenta**
3. Ve a **Configuración**
4. Busca la sección **Token de acceso aprobados**
5. Haz clic en **Nuevo token de acceso**
6. En "Propósito" escribe: `Canvas Automation App`
7. Deja la fecha de vencimiento vacía (sin expiración)
8. Haz clic en **Generar token**
9. **Copia el token ahora** — no podrás verlo de nuevo

> ⚠️ El token tiene permisos de administrador. Nunca lo compartas
> ni lo subas a GitHub.

---

## 3. Configurar el Backend

```bash
# Desde la raíz del repositorio
cd backend

# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# Windows:
venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configurar variables de entorno

```bash
# Copiar la plantilla
cp .env.example .env
```

Abre el archivo `backend/.env` y completa con tu token:

```env
CANVAS_ACCESS_TOKEN=tu_token_real_aqui
CANVAS_BASE_URL=https://poli.instructure.com/api/v1/
CANVAS_ACCOUNT_ID=1
AUDIT_DB_PATH=data/audit_log.db
```

### Verificar la conexión con Canvas

```bash
# Con el venv activado, desde la carpeta backend/
python -c "
import asyncio
from app.infrastructure.canvas.http_client import CanvasHttpClient

async def test():
    async with CanvasHttpClient() as http:
        resp = await http.get('users/self')
        print(f'Conectado como: {resp[\"name\"]}')
        print(f'Email: {resp[\"email\"]}')

asyncio.run(test())
"
```

Si ves tu nombre y email, la configuración es correcta.

### Iniciar el servidor

```bash
uvicorn app.main:app --reload --port 8000
```

El servidor estará disponible en:
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 4. Configurar el Frontend

```bash
# Desde la raíz del repositorio
cd frontend

# Instalar dependencias
npm install

# Iniciar el servidor de desarrollo
npm run dev
```

La aplicación estará disponible en **http://localhost:5173**

---

## 5. Ejecutar los tests

```bash
# Desde la carpeta backend/ con el venv activado
cd backend

# Todos los tests unitarios
pytest tests/unit/ -v

# Con reporte de cobertura
pytest tests/unit/ --cov=app --cov-report=term-missing

# Un módulo específico
pytest tests/unit/test_file_normalizer.py -v
```

**Resultado esperado:** 400+ tests en verde en menos de 60 segundos.

---

## 6. Primer despliegue de prueba

Con ambos servidores corriendo:

1. Abre http://localhost:5173
2. **Paso 1 — Cargar archivos:** arrastra el ZIP del aula
3. **Paso 2 — Plantilla:** selecciona Diseño Instruccional, Nivel y Tipología
4. **Paso 3 — Curso:** elige "Curso nuevo" e ingresa el nombre
5. Haz clic en **"Iniciar despliegue en Canvas"**
6. Observa el progreso en tiempo real en la barra de progreso
7. Al completar, haz clic en **"Abrir en Canvas"** para verificar el resultado

---

## Estructura del ZIP esperada

El sistema espera que el ZIP tenga esta estructura interna:

1. Archivos/
2. Presentación/index.html
3. Material fundamental/U1_Lectura_Fundamental_1.pdf,U1_Lectura_Fundamental_2.pdf, U1_MF_1/← Storyline (opcional) story.html
4. Material de trabajo/U1_Material_de_trabajo.pdf, U1_Material_de_trabajo_1/← Storyline (opcional) story.html
5. Complementos/U1_Complemento.pdf
6. Cierre/index.html

> El sistema normaliza automáticamente variaciones de nombres.
> Ver [Troubleshooting](solucion-de-problemas.md) si hay problemas de detección.

---

## Problemas frecuentes de instalación

| Error | Causa | Solución |
|---|---|---|
| `No module named aiosqlite` | Dependencia no instalada | `pip install aiosqlite` |
| `CANVAS_ACCESS_TOKEN not set` | `.env` no configurado | Verificar paso 3 |
| Puerto 8000 ocupado | Otra instancia corriendo | `taskkill /F /IM uvicorn.exe` (Windows) |
| `python` no reconocido | Python no en PATH | Usar `py` en lugar de `python` en Windows |

> Para problemas más detallados, consulta [Troubleshooting](solucion-de-problemas.md).
