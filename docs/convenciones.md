# Conventions

Estándares de código, nomenclatura y flujo de trabajo del proyecto
Canvas LMS Automation App.

---

## Conventional Commits

Todos los mensajes de commit siguen la especificación
[Conventional Commits](https://www.conventionalcommits.org/).

### Formato

```
tipo(ámbito): descripción breve en minúsculas

[cuerpo opcional — explica el QUÉ y el POR QUÉ]

[footer opcional — referencias a HU o issues]
```

### Tipos utilizados en el proyecto

| Tipo | Cuándo usarlo | Ejemplo |
|---|---|---|
| `feat` | Nueva funcionalidad | `feat(orchestrator): agregar detección de Storyline en Material de trabajo` |
| `fix` | Corrección de bug | `fix(scorm): soportar carpetas con espacio U1_MF 1` |
| `refactor` | Cambio sin nuevo comportamiento | `refactor(guion-reader): cambiar detección de unidad de == a in` |
| `test` | Agregar o modificar tests | `test(guion-reader): agregar caso ESC771 formato Material_Fundamental_U1` |
| `docs` | Cambios en documentación | `docs: agregar README.md del proyecto y .env.example` |
| `ci` | Pipeline de CI | `ci: agregar pipeline GitHub Actions con pytest y TypeScript` |
| `chore` | Mantenimiento y configuración | `chore: eliminar carpeta docs/ — documentación migrada a GitHub Wiki` |

### Ámbitos utilizados en el proyecto

```
orchestrator      → DeploymentOrchestrator
scorm             → InteractiveContentDetector
guion-reader      → GuionExcelReader
normalizer        → FileNormalizer
zip-processor     → ZipProcessor
canvas-http       → CanvasHttpClient
course-repo       → CourseRepository
file-repo         → FileRepository
page-repo         → PageRepository
composers         → cualquier IPageComposer
audit             → AuditRepository y router
benchmark         → BenchmarkRouter
deploy            → DeployRouter
frontend          → cambios en React/TypeScript
ci                → GitHub Actions
```

### Ejemplos reales del proyecto

```bash
feat(scorm): detectar carpetas U1_MF 1 con espacio en detector SCORM
fix(front-composer): usar lambda en re.sub para evitar IndexError con textos Excel
refactor(orchestrator): hacer comparación de prefijos case-insensitive para Windows
test(value-objects): agregar 56 tests para DeploymentConfig y ProgressEvent
docs(wiki): agregar página Architecture con diagramas de capas
ci: corregir sintaxis YAML quoted 'on' para evitar parseo como booleano
chore(deps): agregar aiosqlite a requirements.txt
```

---

## Nomenclatura de ramas

### Formato

```
tipo/HU-XX-descripcion-breve-con-guiones
```

### Ejemplos

```
feature/HU-09-storyline-material-fundamental
feature/HU-16-token-como-contrasena-login
fix/HU-10-guion-reader-formato-esc771
refactor/HU-25-actualizacion-incremental-aula
docs/wiki-conventions-y-troubleshooting
ci/github-actions-pipeline-inicial
```

### Reglas

- Solo letras minúsculas, números y guiones
- Máximo 50 caracteres en la descripción
- Siempre incluir el número de HU cuando aplica
- La rama `main` es la rama de integración permanente — nunca desarrollar directamente en ella

---

## Convenciones Python — Backend

### Nomenclatura

```python
# Módulos y paquetes: snake_case
file_normalizer.py
interactive_content_detector.py

# Clases: PascalCase
class DeploymentOrchestrator:
class CanvasHttpClient:
class SQLiteAuditRepository:

# Funciones y métodos: snake_case
def detect_material_trabajo(self, files_map: dict) -> list[dict]:
async def upload_all(self, course_id: int, path: Path) -> UploadSummary:

# Variables y parámetros: snake_case
files_map: dict[str, int]
upload_summary: UploadSummary
course_id: int

# Constantes: SCREAMING_SNAKE_CASE
MAX_REINTENTOS_POR_ARCHIVO: int = 3
MIGRATION_TIMEOUT_SEG: int = 600

# Variables privadas: prefijo guion bajo
self._http: CanvasHttpClient
self._course_repo: CourseRepository
```

### Type hints — obligatorios en todo el código

```python
# ✅ Correcto
async def create_course(self, name: str) -> CourseInfo:
def detect(self, files_map: dict[str, int]) -> dict[int, list[dict]]:
def _limpiar_texto(texto: str, min_chars: int = 30) -> str:

# ❌ Incorrecto — sin type hints
async def create_course(self, name):
def detect(self, files_map):
```

### Docstrings — en español, formato Google Style

```python
def upload_all(
    self,
    course_id: int,
    content_path: Path,
    on_progress: Callable[[int, int, str], None] | None = None,
) -> UploadSummary:
    """
    Sube recursivamente todos los archivos de una carpeta a Canvas.

    Recorre content_path de forma recursiva, sube cada archivo
    manteniendo la ruta relativa como estructura de carpetas en Canvas.

    Args:
        course_id:    ID del curso Canvas destino.
        content_path: Directorio raíz de los archivos a subir.
        on_progress:  Callback opcional invocado tras cada archivo.

    Returns:
        UploadSummary con el mapa {ruta_relativa: file_id} de exitosos
        y la lista de rutas que fallaron.

    Raises:
        FileUploadError: Si el directorio no existe.
        CanvasAuthError: Sin permisos de subida en el curso.
    """
```

### Reglas de arquitectura — no negociables

```python
# ❌ NUNCA — lógica de negocio en routers
@router.post("/deploy")
async def iniciar_deploy(...):
    archivos = zip.extractall()        # ← esto va en ZipProcessor
    await canvas.create_course(...)    # ← esto va en CourseRepository

# ✅ CORRECTO — el router solo orquesta y delega
@router.post("/deploy")
async def iniciar_deploy(...):
    background_tasks.add_task(_ejecutar_deploy_background, task_id, config)
    return DeployStartResponse(task_id=task_id, ...)

# ❌ NUNCA — importar infraestructura desde dominio
# En domain/services/zip_processor.py:
from app.infrastructure.canvas.http_client import CanvasHttpClient  # ← PROHIBIDO

# ❌ NUNCA — lógica síncrona bloqueante en operaciones I/O
def subir_archivo(path: Path) -> int:
    response = requests.post(url, files=...)  # ← usar httpx async

# ✅ CORRECTO — todo I/O es async/await
async def subir_archivo(path: Path) -> int:
    response = await self._client.post(url, files=...)
```

---

## Convenciones TypeScript — Frontend

### Nomenclatura

```typescript
// Componentes React: PascalCase
function DeployPage(): JSX.Element
function ProgressTracker({ taskId }: Props): JSX.Element
function VerificationPanel({ courseId }: Props): JSX.Element

// Archivos de componentes: PascalCase.tsx
DeployPage.tsx
ProgressTracker.tsx
VerificationPanel.tsx

// Servicios y utilidades: camelCase.ts
api.ts
utils.ts

// Tipos e interfaces: PascalCase
interface ProgressEventData { ... }
interface AuditEntryData { ... }
type CourseOption = "new" | "existing"

// Variables y funciones: camelCase
const taskId = response.task_id
async function startDeploy(params: DeployParams): Promise<DeployStartResponse>

// Constantes de módulo: SCREAMING_SNAKE_CASE
const TIEMPO_MANUAL_MIN = 240
const PLANTILLAS_DISPONIBLES: PlantillaOption[] = [...]
```

### Tipos explícitos — nunca `any`

```typescript
// ✅ Correcto
const [eventos, setEventos] = useState<ProgressEventData[]>([])
const [reporte, setReporte] = useState<VerificationReport | null>(null)

async function verifyDeploy(courseId: number): Promise<VerificationReport> {
  const response = await apiClient.get<VerificationReport>(...)
  return response.data
}

// ❌ Incorrecto
const [eventos, setEventos] = useState<any[]>([])
async function verifyDeploy(courseId: any): Promise<any> { ... }
```

### Llamadas a la API — siempre a través de `api.ts`

```typescript
// ✅ Correcto — centralizado en api.ts
import { startDeploy, verifyDeploy } from "@/services/api"

// ❌ Incorrecto — llamada directa desde el componente
const response = await fetch("http://localhost:8000/api/v1/deploy", {
  method: "POST", ...
})
```

---

## Convenciones de tests — Backend

### Nomenclatura de archivos y funciones

```
test_{componente}.py

test_file_normalizer.py
test_zip_processor.py
test_course_repository.py
test_composers.py
```

```python
# Formato del nombre del test:
# test_[acción]_[condición]_[resultado_esperado]

def test_crear_curso_nombre_valido_retorna_course_info():
def test_subir_archivo_no_existe_lanza_file_upload_error():
def test_detectar_scorm_carpeta_con_espacio_coincide_patron():
```

### Estrategia de mocking

```python
# Siempre mockear CanvasHttpClient para aislar del servidor real
def _mock_http() -> MagicMock:
    mock = MagicMock(spec=CanvasHttpClient)
    mock.get  = AsyncMock()
    mock.post = AsyncMock()
    mock.put  = AsyncMock()
    return mock

# Nunca hacer llamadas HTTP reales en tests unitarios
# Los tests de integración contra Canvas real se hacen manualmente
```

### Estructura de un test

```python
class TestCreateCourse:

    @pytest.mark.asyncio
    async def test_retorna_course_info_con_id_correcto(self) -> None:
        # Arrange — preparar
        http = _mock_http()
        http.post.return_value = {"id": 9876, "name": "Mi Curso", ...}
        repo = CourseRepository(http)

        # Act — ejecutar
        info = await repo.create_course("Mi Curso")

        # Assert — verificar
        assert info.id == 9876
        assert info.name == "Mi Curso"
```

---

## Convenciones de Canvas API

### Slugs de páginas — siempre en minúsculas con guiones

```
✅ unidad-1-material-fundamental
✅ front-del-curso
✅ material-de-trabajo-interactivo-1

❌ Unidad_1_Material_Fundamental
❌ frontDelCurso
```

### Nombres de archivos en el ZIP — patrón institucional

```
Lecturas:           U{n}_Lectura_Fundamental_{seq}.pdf
Material fund.:     U{n}_Material_Fundamental.pdf
Actividad formativa: U{n}_Actividad_Formativa.pdf
Actividad sumativa:  U{n}_Actividad_Sumativa.pdf
Complemento:        U{n}_Complemento.pdf
Material trabajo:   U{n}_Material_de_trabajo.pdf
Carpetas SCORM MF:  U{n}_MF_{num}/ o U{n}_MF {num}/
Carpetas SCORM MT:  U{n}_Material_de_trabajo_{num}/
```

### Comparaciones de rutas — siempre case-insensitive

```python
# ✅ Correcto — resiliente a variaciones de Windows
ruta_lower = ruta.lower().replace("\\", "/")
if ruta_lower.startswith("2. material fundamental/"):

# ❌ Incorrecto — falla si la carpeta tiene F mayúscula
if ruta.startswith("2. Material fundamental/"):
```