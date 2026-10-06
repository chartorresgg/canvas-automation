# Troubleshooting

Guía de diagnóstico y solución de problemas frecuentes en
Canvas LMS Automation App.

> Todos los problemas documentados aquí ocurrieron durante el
> desarrollo real del proyecto y tienen solución verificada.

---

## Problemas de instalación y arranque

### `No module named 'aiosqlite'`

**Síntoma:**
```
ModuleNotFoundError: No module named 'aiosqlite'
```

**Causa:** La dependencia `aiosqlite` no está instalada en el entorno virtual.

**Solución:**
```powershell
# Con el venv activado
pip install aiosqlite
# O forzado en sistemas con restricciones:
pip install aiosqlite --break-system-packages
```

---

### `python` no reconocido en Windows

**Síntoma:**
```
python : El término 'python' no se reconoce como nombre de un cmdlet
```

**Causa:** En Windows, Python puede estar disponible como `py` en lugar de `python`.

**Solución:**
```powershell
# Usar py en lugar de python
py -m pytest tests/unit/ -v
py -m uvicorn app.main:app --reload --port 8000

# O verificar que Python está en el PATH:
py --version
```

---

### Puerto 8000 ya está en uso

**Síntoma:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)
```

**Causa:** Otra instancia de Uvicorn u otra aplicación usa el puerto 8000.

**Solución en Windows:**
```powershell
# Encontrar el proceso que usa el puerto
netstat -ano | findstr :8000

# Matar el proceso (reemplazar PID con el número encontrado)
taskkill /PID 12345 /F

# O usar un puerto diferente
uvicorn app.main:app --reload --port 8001
```

---

### CORS error desde el frontend

**Síntoma:** En el navegador aparece:
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:5173'
has been blocked by CORS policy
```

**Causa:** El backend no tiene configurado el origen del frontend en CORS.

**Solución:** Verificar `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ← debe incluir el origen del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Problemas con el Token de Canvas

### Token inválido o sin permisos

**Síntoma:**
```json
{"status": 401, "message": "Invalid access token."}
```
O:
```json
{"status": 403, "message": "Insufficient scopes on access token."}
```

**Causa:** El token es incorrecto, fue regenerado o no tiene permisos de administrador.

**Diagnóstico:**
```powershell
# Verificar que el token funciona desde la terminal
python -c "
import asyncio
from app.infrastructure.canvas.http_client import CanvasHttpClient

async def test():
    async with CanvasHttpClient() as http:
        resp = await http.get('users/self')
        print('Token válido. Usuario:', resp['name'])

asyncio.run(test())
"
```

**Solución:**
1. Ir a Canvas → Cuenta → Configuración → Token de acceso aprobados
2. Eliminar el token actual
3. Crear un nuevo token con propósito `Canvas Automation App`
4. Actualizar `backend/.env` con el nuevo valor
5. Reiniciar Uvicorn

---

### El `.env` no se carga

**Síntoma:**
```
KeyError: 'CANVAS_ACCESS_TOKEN'
```
O el token aparece como `None`.

**Causa:** El archivo `.env` no existe o está en la carpeta incorrecta.

**Verificación:**
```powershell
# El .env debe estar en backend/ (no en la raíz del proyecto)
ls backend\.env

# Verificar su contenido
type backend\.env
```

**Solución:**
```powershell
cd backend
cp .env.example .env
# Editar .env con el token real
```

---

## Problemas con el ZIP

### Carpetas SCORM no reconocidas

**Síntoma en los logs:**
```
WARNING - Carpeta SCORM no reconocida: 'U1_MF 1' — omitiendo
WARNING - Carpeta SCORM no reconocida: 'U2_Contenido' — omitiendo
```

**Causa:** El nombre de la carpeta no coincide con ningún patrón reconocido.

**Patrones soportados para Material Fundamental:**
```
U{n}_MF_{num}          → U1_MF_1, U3_MF_2
U{n}_MF {num}          → U1_MF 1, U2_MF 2  (con espacio)
U{n}_MF{num}           → U1_MF1, U3_MF3
MF_U{n}_{num}          → MF_U1_2, MF_U3_1
MF_U{n}               → MF_U1, MF_U4
U{n}_Material_fundamental    → U1_Material_fundamental
U{n}_Material fundamental    → U1_Material fundamental
```

**Patrones soportados para Material de Trabajo:**
```
Cualquier subcarpeta que contenga story.html o index.html
No requiere convención de nombre específica
```

**Solución:** Renombrar la carpeta al patrón más simple: `U{n}_MF_{num}`.

---

### PDFs sin botones en páginas de Material Fundamental

**Síntoma:** El despliegue completa sin errores pero las páginas de Material
Fundamental aparecen solo con el banner y sin botones de lecturas o actividades.

**Causa más frecuente:** Diferencia de casing en Windows.
En Windows, si la carpeta se llama `2. Material Fundamental` (F mayúscula),
Python la reporta con esa capitalización aunque el normalizer intentó
renombrarla a `2. Material fundamental` (f minúscula).

**Diagnóstico:**
```powershell
# Verificar los logs del servidor en modo debug
uvicorn app.main:app --reload --port 8000 --log-level debug
# Buscar líneas: "Ctx U1 → lecturas=X, mat_fund=X"
# Si todos los contadores son 0, es el problema de casing
```

**Solución:** Ya corregida en la versión actual del orquestador.
La comparación de rutas usa `.lower()` en ambos lados.
Si persiste, verificar que el archivo `orchestrator.py` tiene
la función `_construir_ctx_material_fundamental` con la versión
actualizada que usa `prefijo_lower`.

---

### `IndexError: no such group` en paso 4

**Síntoma:**
```
[04] Error en paso 4: IndexError
'InteractiveContentDetector' object has no attribute 'detect_material_trabajo'
```
O:
```
[04] Error en paso 4: IndexError: no such group
```

**Causa 1 — Método no encontrado:** Python cargó una versión cacheada del
`InteractiveContentDetector` anterior que no tiene el método `detect_material_trabajo`.

**Solución:**
```powershell
# 1. Detener Uvicorn (Ctrl+C)
# 2. Limpiar caché de Python
Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
# 3. Reiniciar
uvicorn app.main:app --reload --port 8000
```

**Causa 2 — Regex con un solo grupo:** La función `_parsear_carpeta` en
`InteractiveContentDetector` llama `m.group(2)` sobre un patrón que solo
tiene 1 grupo capturador.

**Solución:** Verificar que `_parsear_carpeta` tiene el bloque `try/except`:
```python
try:
    numero_raw = m.group(2)
except IndexError:
    numero_raw = None
```

---

### `IndexError` en `FrontPageComposer` (textos del Excel)

**Síntoma:**
```
[04] Error en paso 4: IndexError: no such group
```
El error ocurre durante la actualización del front del curso.

**Causa:** El texto extraído del Excel contiene caracteres como `\1` o `\g<N>`
que Python interpreta como referencias a grupos de captura en `re.sub()`.

**Solución:** Verificar que `FrontPageComposer._reemplazar_modulo` usa
lambda en lugar de string de reemplazo:
```python
# ✅ Correcto — texto nunca se interpreta como referencia
return re.sub(
    pattern,
    lambda m: m.group(1) + nuevo_texto + m.group(3),
    html,
    flags=re.IGNORECASE,
)

# ❌ Incorrecto — falla si nuevo_texto contiene \1 o \g<N>
return re.sub(pattern, rf'\g<1>{nuevo_texto}\g<3>', html)
```

---

## Problemas con el Excel del Guion

### Videos y podcasts no se cargan en las páginas

**Síntoma:** El despliegue completa correctamente pero las páginas de
Material Fundamental no tienen los botones de video, podcast o Vimeo.

**Causa más frecuente:** El Excel subido es el archivo de rúbricas u otro
archivo diferente al Guion de módulo.

**Diagnóstico:** El Guion de módulo correcto tiene una hoja llamada
exactamente `Guion de módulo`. Verificar en Excel antes de subir.

**Causa alternativa:** El Excel usa el formato `Material_Fundamental_U1`
en lugar de `U1_material_fundamental_1`.

**Solución:** Verificar que `guion_excel_reader.py` usa la detección flexible:
```python
# ✅ Correcto — detecta ambos formatos
if "material_fundamental" in col2_l and "lectura" not in col2_l:
```

---

### Párrafos de introducción no aparecen en el front del curso

**Síntoma:** El front del curso se actualiza pero los párrafos de
introducción de las unidades quedan vacíos.

**Causa:** El Excel usa `"Título de la unidad N"` en col[0] en lugar de
`"Unidad N"`. El parser anterior usaba igualdad exacta.

**Solución:** Verificar que `guion_excel_reader.py` usa `in` para detectar la unidad:
```python
# ✅ Correcto — detecta "Unidad 1" y "Título de la unidad 1"
if f"unidad {u}" in col0_l:

# ❌ Incorrecto — solo detecta "Unidad 1" exacto
if col0_l == f"unidad {u}":
```

---

## Problemas con GitHub Actions CI

### `No event triggers defined in 'on'`

**Síntoma en GitHub Actions:**
```
No event triggers defined in `on`
This workflow graph cannot be shown
```

**Causa:** La palabra `on` en YAML 1.1 se interpreta como el booleano `true`.

**Solución:** Poner `on` entre comillas en el workflow:
```yaml
# ✅ Correcto
"on":
  push:
    branches: [main]

# ❌ Incorrecto
on:
  push:
    branches: [main]
```

---

### `exit code 4` en pytest dentro de CI

**Síntoma:** El job de backend falla con exit code 4.

**Causa:** pytest no encontró tests en la ruta especificada.
El exit code 4 significa "no collection" — ruta incorrecta.

**Solución:** Usar `python -m pytest` en lugar de `pytest` en el workflow:
```yaml
# ✅ Correcto
run: python -m pytest tests/unit/ -v --tb=short

# ❌ Puede fallar si pytest no está en PATH
run: pytest tests/unit/ -v --tb=short
```

---

## Referencia rápida de comandos

```powershell
# Limpiar caché de Python (Windows)
Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force

# Verificar token Canvas
python -c "import asyncio; from app.infrastructure.canvas.http_client import CanvasHttpClient; asyncio.run(CanvasHttpClient().__aenter__())"

# Correr solo un test específico
python -m pytest tests/unit/test_file_normalizer.py::TestNormalizarPDFs -v

# Ver logs en modo debug
uvicorn app.main:app --reload --port 8000 --log-level debug

# Verificar que el método existe en la clase
python -c "from app.domain.services.interactive_content_detector import InteractiveContentDetector; print([m for m in dir(InteractiveContentDetector()) if not m.startswith('_')])"

# Matar proceso en puerto 8000
netstat -ano | findstr :8000
taskkill /PID [numero] /F
```