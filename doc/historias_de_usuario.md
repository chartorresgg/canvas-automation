# Historias de Usuario — Estructura Completa — Fase 1
# Canvas LMS Automation App — Politécnico Grancolombiano
# Carlos Eduardo Guzmán Torres — cedguzman@poligran.edu.co

---

# SPRINT 1 — Modelado y Prototipo Navegable (19 SP)

---

## HU-01 — Selector de Plantilla Base | 3 SP | ✅ Done

**Como** Analista de Ambientes de Aprendizaje,
**quiero** seleccionar la plantilla Canvas mediante tres filtros en cascada,
**para** que el sistema identifique automáticamente el ID correcto sin necesidad de recordarlo.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | El primer filtro muestra opciones de Diseño Instruccional disponibles | ✅ |
| 2 | Al seleccionar DI, el segundo filtro muestra Niveles de Formación | ✅ |
| 3 | Al seleccionar Nivel, el tercer filtro muestra Tipologías | ✅ |
| 4 | La combinación identifica unívocamente el template_id de Canvas | ✅ |
| 5 | El botón Siguiente se deshabilita hasta completar los tres filtros | ✅ |
| 6 | Muestra las 11 plantillas institucionales con sus IDs reales | ✅ |

### Tareas Técnicas (Jira)
- T-001: Levantar catálogo de 11 plantillas Canvas con IDs reales de producción
- T-002: Implementar `TemplateSelector.tsx` con lógica de filtros en cascada
- T-003: Definir `templates.ts` con estructura de datos de plantillas
- T-004: Implementar validación de estado antes de habilitar avance al paso 2
- T-005: Escribir tests del componente verificando combinaciones de filtros

### Componente
`frontend/src/features/deploy/TemplateSelector.tsx`

---

## HU-02 — Formulario de Metadatos del Curso | 3 SP | ✅ Done

**Como** Analista de Ambientes de Aprendizaje,
**quiero** indicar si el aula es nueva o existente y proporcionar sus datos básicos,
**para** que el sistema configure el despliegue correctamente sin ambigüedades.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Ofrece dos opciones mutuamente excluyentes: Curso Nuevo y Curso Existente | ✅ |
| 2 | Curso Nuevo muestra campo para nombre del aula | ✅ |
| 3 | Curso Existente muestra campo para ID numérico | ✅ |
| 4 | El campo de nombre rechaza texto vacío o menor a 5 caracteres | ✅ |
| 5 | El campo de ID rechaza valores no numéricos | ✅ |
| 6 | Siguiente se deshabilita hasta completar el campo correspondiente | ✅ |

### Tareas Técnicas (Jira)
- T-006: Implementar `MetadataForm.tsx` con radio buttons y campos condicionales
- T-007: Implementar validación reactiva con mensajes de error en línea
- T-008: Conectar estado del formulario con el contexto del wizard

### Componente
`frontend/src/features/deploy/MetadataForm.tsx`

---

## HU-03 — Carga de Archivos mediante Drag & Drop | 5 SP | ✅ Done

**Como** Analista de Ambientes de Aprendizaje,
**quiero** cargar el archivo ZIP arrastrándolo o seleccionándolo desde el explorador,
**para** que el proceso sea intuitivo y no requiera conocimientos técnicos.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Acepta archivos arrastrados desde el explorador de archivos | ✅ |
| 2 | Acepta archivos seleccionados mediante clic | ✅ |
| 3 | Solo acepta extensión .zip | ✅ |
| 4 | Con múltiples archivos, toma solo el primero | ✅ |
| 5 | Muestra nombre y tamaño al cargar exitosamente | ✅ |
| 6 | Permite eliminar el archivo y cargar uno diferente | ✅ |
| 7 | Funciona correctamente en Windows (NTFS case-insensitive) | ✅ |

### Tareas Técnicas (Jira)
- T-009: Implementar `DropZone.tsx` con eventos onDragOver, onDrop, onChange
- T-010: Implementar validación de extensión .zip en el cliente
- T-011: Corregir bug de compatibilidad con Windows en manejo de eventos
- T-012: Implementar estado visual de hover durante drag

**Bug resuelto:** Drag & Drop no funcionaba en Windows por diferencias en el
objeto DataTransfer. Corregido en `fix(frontend): corregir Drag&Drop en Windows`.

### Componente
`frontend/src/features/deploy/DropZone.tsx`

---

## HU-04 — Validación y Normalización Local del ZIP | 8 SP | ✅ Done

**Como** Sistema,
**quiero** extraer y normalizar el ZIP antes de interactuar con Canvas,
**para** garantizar que los nombres de carpetas y PDFs cumplan el estándar
institucional independientemente de cómo los haya nombrado el analista.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Extrae el ZIP en un directorio temporal | ✅ |
| 2 | Renombra carpetas sin punto al estándar institucional | ✅ |
| 3 | Los PDFs sin secuencia reciben el sufijo _1 | ✅ |
| 4 | Retorna total de archivos, tamaño y lista de cambios aplicados | ✅ |
| 5 | Los archivos no modificados no aparecen en la lista de cambios | ✅ |
| 6 | Maneja ZIPs con subcarpetas anidadas correctamente | ✅ |

### Tareas Técnicas (Jira)
- T-013: Implementar `ZipProcessor` (dominio) con extracción y limpieza
- T-014: Implementar `FileNormalizer` (dominio) con regex de normalización
- T-015: Definir `DeploymentConfig` y `ProgressEvent` como value objects
- T-016: Implementar endpoint `POST /api/v1/deploy/upload`
- T-017: Escribir 127 tests unitarios (ZipProcessor: 38, FileNormalizer: 33, ValueObjects: 56)

### Componentes
- `backend/app/domain/services/zip_processor.py`
- `backend/app/domain/services/file_normalizer.py`
- `backend/app/domain/value_objects/`

---

# SPRINT 2 — Integración con API Canvas (21 SP)

---

## HU-05 — Creación Automatizada de Curso en Canvas | 5 SP | ✅ Done

**Como** Sistema,
**quiero** crear el curso en Canvas y copiar la plantilla seleccionada,
**para** que el analista reciba el aula lista sin acceder directamente al LMS.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Con course_option=new, crea el curso con el nombre proporcionado | ✅ |
| 2 | Inicia la migración de contenido desde la plantilla | ✅ |
| 3 | Espera mediante polling hasta que la migración complete | ✅ |
| 4 | El polling tiene timeout máximo de 600 segundos | ✅ |
| 5 | Con course_option=existing, obtiene el curso por ID sin crear uno nuevo | ✅ |
| 6 | Si el curso existente no se encuentra, emite evento de error | ✅ |

### Tareas Técnicas (Jira)
- T-018: Implementar `CanvasHttpClient` con autenticación Bearer y manejo de errores
- T-019: Investigar protocolo de migración Canvas (content_migrations, polling)
- T-020: Implementar `CourseRepository.create_course()` y `copy_template()`
- T-021: Implementar `CourseRepository.poll_migration()` con asyncio.sleep(5)
- T-022: Escribir 25 tests unitarios para CourseRepository

### Componentes
- `backend/app/infrastructure/canvas/http_client.py`
- `backend/app/infrastructure/canvas/course_repository.py`

---

## HU-06 — Subida Masiva de Archivos a Canvas | 8 SP | ✅ Done

**Como** Sistema,
**quiero** subir todos los archivos del ZIP al sistema de archivos del curso en Canvas,
**para** que los Composers puedan referenciarlos por su file_id en las páginas HTML.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Sube cada archivo mediante el protocolo de tres fases de Canvas | ✅ |
| 2 | Emite un evento de progreso por cada archivo completado | ✅ |
| 3 | Reintenta hasta 3 veces con pausa de 2s en caso de error | ✅ |
| 4 | Los archivos que fallan 3 intentos se registran como fallidos | ✅ |
| 5 | El proceso continúa aunque fallen archivos individuales | ✅ |
| 6 | Retorna el mapa {ruta: file_id} de archivos exitosos | ✅ |

### Tareas Técnicas (Jira)
- T-023: Investigar y documentar el protocolo de subida en 3 fases de Canvas
- T-024: Implementar `FileRepository.upload_all()` con iteración recursiva
- T-025: Implementar `_subir_con_reintentos()` con asyncio.sleep(2)
- T-026: Implementar callback `on_progress` por archivo completado
- T-027: Escribir 29 tests unitarios para FileRepository
- T-028: Validar con 194 archivos en Canvas real (curso ESC535, ID 96010)

**Decisión técnica:** El protocolo Canvas requiere 3 requests HTTP por archivo
(solicitar token → subir a S3 → confirmar en Canvas). Un POST multipart
convencional no funciona con la API de Canvas.

### Componente
`backend/app/infrastructure/canvas/file_repository.py`

---

## HU-07 — Vinculación de PDFs a Actividades | 5 SP | ✅ Done

**Como** Sistema,
**quiero** vincular los PDFs subidos a sus Actividades y Foros en Canvas,
**para** que el aula muestre los documentos con vista previa sin configuración manual.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Identifica el PDF de cada Actividad por nomenclatura institucional | ✅ |
| 2 | Actualiza la descripción de la Actividad con HTML de vista previa Canvas | ✅ |
| 3 | El atributo data-canvas-previewable="true" está presente en el HTML | ✅ |
| 4 | Los PDFs sin Actividad correspondiente quedan registrados | ✅ |
| 5 | Procesa Actividades y Foros en la misma operación | ✅ |

### Tareas Técnicas (Jira)
- T-029: Implementar `PageRepository.link_pdfs_bulk()` con asyncio.gather
- T-030: Implementar lógica de matching por nomenclatura institucional
- T-031: Construir HTML con data-canvas-previewable="true"
- T-032: Escribir 33 tests unitarios para PageRepository

### Componente
`backend/app/infrastructure/canvas/page_repository.py`

---

## HU-08 — Panel Visual de Progreso en Tiempo Real | 3 SP | ✅ Done

**Como** Analista de Ambientes de Aprendizaje,
**quiero** ver el progreso del despliegue en tiempo real sin recargar la página,
**para** saber en qué paso se encuentra el proceso y cuánto ha avanzado.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | La barra de progreso avanza de 0% a 100% durante el despliegue | ✅ |
| 2 | Los 5 pasos muestran su estado: pendiente/activo/completado/error | ✅ |
| 3 | Un log muestra cada mensaje SSE recibido | ✅ |
| 4 | La conexión SSE se mantiene activa durante todo el despliegue | ✅ |
| 5 | Al completar, aparece el enlace al curso en Canvas | ✅ |

### Tareas Técnicas (Jira)
- T-033: Implementar `TaskManager` con asyncio.Queue por task_id
- T-034: Implementar endpoint SSE `GET /api/v1/deploy/stream/{task_id}`
- T-035: Implementar heartbeat cada 10s para mantener la conexión
- T-036: Implementar `ProgressTracker.tsx` con indicadores de color por estado
- T-037: Conectar EventSource nativo del navegador al stream SSE

### Componentes
- `backend/app/presentation/task_manager.py`
- `frontend/src/features/deploy/ProgressTracker.tsx`

---

# SPRINT 3 — Automatización y Monitoreo (23 SP)

---

## HU-09 — Inyección de Paquetes Articulate Storyline | 8 SP | ✅ Done

**Como** Sistema,
**quiero** detectar automáticamente los paquetes SCORM y crear páginas iframe en Canvas,
**para** que el contenido interactivo sea accesible sin configuración manual.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Detecta story.html (preferido) o index.html como entrada SCORM | ✅ |
| 2 | Soporta 6 patrones de nomenclatura de carpetas institucionales | ✅ |
| 3 | La detección es case-insensitive | ✅ |
| 4 | Carpetas con espacio (U1_MF 1) son detectadas correctamente | ✅ |
| 5 | Crea página wiki en Canvas con iframe por cada paquete | ✅ |
| 6 | El botón de acceso aparece en la página de Material Fundamental | ✅ |

### Tareas Técnicas (Jira)
- T-038: Implementar `InteractiveContentDetector` con 6 patrones regex
- T-039: Implementar `_parsear_carpeta()` con try/except para grupos opcionales
- T-040: Añadir patrón para carpetas con espacio (`U(\d+)_MF\s(\d+)`)
- T-041: Implementar `IframeComposer` generando HTML de iframe Canvas
- T-042: Integrar detección SCORM en el paso 4 del orquestador
- T-043: Escribir tests cubriendo los 6 patrones y casos de borde

**Bugs resueltos:**
- IndexError en group(2) para patrones de un solo grupo → try/except
- Carpetas U1_MF 1 (con espacio) no detectadas → nuevo patrón regex

### Componentes
- `backend/app/domain/services/interactive_content_detector.py`
- `backend/app/infrastructure/composers/iframe_composer.py`

---

## HU-10 — Procesamiento del Guion Excel | 5 SP | ✅ Done

**Como** Sistema,
**quiero** parsear el Excel del Guion y extraer URLs de video, párrafos y podcasts,
**para** actualizar el front del curso y las páginas de Material Fundamental automáticamente.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Soporta formato ESC535 (Unidad N como marcador) | ✅ |
| 2 | Soporta formato ESC339 (Título de la unidad N como marcador) | ✅ |
| 3 | Soporta formato ESC771 (nombre alternativo de material multimedia) | ✅ |
| 4 | Extrae URLs de Vimeo, SoundCloud y Material Fundamental | ✅ |
| 5 | Es resiliente a variaciones de capitalización | ✅ |
| 6 | Sin Excel, el despliegue continúa sin el paso de Guion | ✅ |

### Tareas Técnicas (Jira)
- T-044: Implementar `GuionExcelReader` con detección de 3 formatos
- T-045: Corregir detección de unidad con operador `in` en lugar de `==`
- T-046: Corregir detección ESC771 con `"material_fundamental" in col2_l`
- T-047: Implementar `FrontPageComposer` con lambda en re.sub
- T-048: Escribir 26 tests unitarios cubriendo los 3 formatos institucionales

**Bugs resueltos:**
- `re.sub()` IndexError con texto Excel que contiene caracteres especiales → lambda
- ESC339 no detectaba párrafos → `in` en lugar de `==`
- ESC771 no detectaba Material Fundamental → condición generalizada

### Componentes
- `backend/app/domain/services/guion_excel_reader.py`
- `backend/app/infrastructure/composers/front_page_composer.py`

---

## HU-11 — Cancelación del Despliegue en Curso | 5 SP | ✅ Done

**Como** Analista de Ambientes de Aprendizaje,
**quiero** poder cancelar un despliegue en curso,
**para** recuperar el control si ocurre un error o necesito detener el proceso.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | El botón de cancelación aparece durante el despliegue activo | ✅ |
| 2 | Aparece un diálogo de confirmación antes de ejecutar | ✅ |
| 3 | El proceso se detiene en la siguiente operación await | ✅ |
| 4 | El stream SSE emite evento con status=cancelled | ✅ |
| 5 | Los archivos ya subidos permanecen en Canvas | ✅ |
| 6 | La cancelación queda registrada en el AuditLog | ✅ |

### Tareas Técnicas (Jira)
- T-049: Implementar `TaskManager.registrar_asyncio_task()` con referencia al Task
- T-050: Implementar endpoint `POST /api/v1/deploy/cancel/{task_id}`
- T-051: Implementar `except asyncio.CancelledError` en el orquestador
- T-052: Agregar diálogo de confirmación en el frontend

---

## HU-14 — Verificación de Integridad Post-Despliegue | 5 SP | ✅ Done

**Como** Analista de Ambientes de Aprendizaje,
**quiero** ver un reporte de integridad del aula después del despliegue,
**para** confirmar que todas las páginas institucionales quedaron correctamente creadas.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Verifica existencia de las 12 páginas institucionales por slug | ✅ |
| 2 | Verifica que las Actividades tienen PDFs vinculados | ✅ |
| 3 | Verifica que el front del curso tiene contenido real (>300 caracteres) | ✅ |
| 4 | El resultado se clasifica como success, warning o error | ✅ |
| 5 | Las 3 consultas a Canvas se ejecutan en paralelo con asyncio.gather | ✅ |

### Tareas Técnicas (Jira)
- T-053: Implementar endpoint `GET /api/v1/deploy/verify/{course_id}`
- T-054: Implementar 3 consultas paralelas con asyncio.gather
- T-055: Implementar lógica de clasificación success/warning/error
- T-056: Implementar `VerificationPanel.tsx` con semáforo de colores

### Componentes
- `backend/app/presentation/routers/deploy.py` (verify)
- `frontend/src/features/deploy/VerificationPanel.tsx`

---

# SPRINT 4 — Validación, Pruebas y Resiliencia (18 SP)

---

## HU-12 — Gestión Automática de Errores de Red | 5 SP | ✅ Done

**Como** Sistema,
**quiero** reintentar automáticamente las subidas que fallen por errores transitorios,
**para** garantizar despliegues completos sin intervención manual del analista.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Cada archivo tiene hasta 3 intentos de subida | ✅ |
| 2 | Entre intentos hay pausa de 2 segundos | ✅ |
| 3 | Si los 3 fallan, el archivo se registra como fallido | ✅ |
| 4 | El despliegue continúa con el siguiente archivo | ✅ |
| 5 | El resumen distingue archivos exitosos de fallidos | ✅ |

### Tareas Técnicas (Jira)
- T-057: Implementar `MAX_REINTENTOS_POR_ARCHIVO = 3` en FileRepository
- T-058: Implementar `asyncio.sleep(2)` entre reintentos
- T-059: Implementar `UploadSummary` con listas separadas de exitosos/fallidos

---

## HU-13 — Benchmark de Procesamiento Local | 5 SP | ✅ Done

**Como** Desarrollador,
**quiero** medir el tiempo de cada etapa del procesamiento sin interactuar con Canvas,
**para** documentar el rendimiento y compararlo con el proceso manual.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Ejecuta extracción, normalización y detección SCORM | ✅ |
| 2 | Mide el tiempo de cada etapa en milisegundos | ✅ |
| 3 | Retorna nombre, duración y estado de cada etapa | ✅ |
| 4 | No realiza ninguna llamada a Canvas | ✅ |
| 5 | Ejecutable desde Postman con cualquier ZIP real | ✅ |

### Tareas Técnicas (Jira)
- T-060: Implementar endpoint `POST /api/v1/benchmark`
- T-061: Implementar medición con `time.perf_counter()`
- T-062: Implementar `BenchmarkPage.tsx` con visualización de etapas

---

## HU-15 — Historial y Exportación de Auditoría | 3 SP | ✅ Done

**Como** Analista de Ambientes de Aprendizaje,
**quiero** consultar el historial de despliegues y exportarlo en Excel,
**para** generar reportes operativos institucionales.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Todo despliegue queda registrado automáticamente al finalizar | ✅ |
| 2 | Registra: task_id, curso, archivos, duración, estado, fechas | ✅ |
| 3 | Se registra aunque el despliegue falle o sea cancelado | ✅ |
| 4 | El endpoint soporta paginación y filtro por estado | ✅ |
| 5 | El Excel exportado tiene historial detallado y hoja de resumen | ✅ |
| 6 | El Excel usa colores por estado (verde/rojo/naranja) | ✅ |

### Tareas Técnicas (Jira)
- T-063: Definir interfaz `IAuditRepository` en capa de dominio
- T-064: Implementar `SQLiteAuditRepository` con aiosqlite
- T-065: Integrar registro en bloque `finally` del orquestador
- T-066: Implementar `GET /api/v1/audit` con paginación
- T-067: Implementar `GET /api/v1/audit/export` con openpyxl
- T-068: Implementar `AuditPage.tsx` con tabla y botón de exportación

---

## HU-16 — Token de Canvas como Contraseña | 5 SP | ✅ Done

**Como** Analista de Ambientes de Aprendizaje,
**quiero** ingresar mi token Canvas en una pantalla de login,
**para** que el sistema use mis credenciales sin almacenar el token en el servidor.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | La app muestra login al abrir sin sesión activa | ✅ |
| 2 | El campo de token es de tipo password | ✅ |
| 3 | Hay opción de mostrar/ocultar el token | ✅ |
| 4 | El sistema valida el token contra Canvas antes de crear sesión | ✅ |
| 5 | Token inválido muestra mensaje de error específico | ✅ |
| 6 | El token nunca se persiste en disco ni en el servidor | ✅ |
| 7 | Cada analista usa su propio token con sus permisos | ✅ |
| 8 | Hay botón de logout que elimina la sesión activa | ✅ |

### Tareas Técnicas (Jira)
- T-069: Implementar `SessionManager` en memoria con secrets.token_urlsafe
- T-070: Implementar `POST /api/v1/auth/login` validando con Canvas
- T-071: Implementar `POST /api/v1/auth/logout` y `GET /api/v1/auth/validate`
- T-072: Implementar `TokenContext` React con estado en memoria
- T-073: Implementar `LoginPage.tsx` con campo password y toggle
- T-074: Agregar interceptor Axios para enviar X-Session-ID
- T-075: Actualizar todos los endpoints protegidos para leer el header

---

## HU-17 — Despliegue en la Nube (Render + Vercel) | 8 SP | ✅ Done

**Como** Analista de Ambientes de Aprendizaje,
**quiero** acceder al sistema desde cualquier navegador sin instalar software,
**para** usar la herramienta de forma autónoma desde cualquier máquina institucional.

### Criterios de Aceptación
| # | Criterio | ✅ |
|---|---|---|
| 1 | Frontend accesible en URL pública de Vercel | ✅ |
| 2 | Backend accesible en URL pública de Render | ✅ |
| 3 | Login funciona desde cualquier navegador sin configuración | ✅ |
| 4 | Despliegue end-to-end funciona desde la nube | ✅ |
| 5 | CORS permite únicamente el origen de Vercel | ✅ |
| 6 | Push a main redespliega automáticamente en ambas plataformas | ✅ |

### Tareas Técnicas (Jira)
- T-076: Crear `render.yaml` con configuración de build y start
- T-077: Actualizar CORS con variable de entorno `FRONTEND_URL`
- T-078: Actualizar `api.ts` para usar `VITE_API_URL` desde env vars
- T-079: Limpiar `requirements.txt` con solo dependencias del proyecto
- T-080: Configurar variables de entorno en dashboards de Render y Vercel
- T-081: Verificar despliegue end-to-end desde producción

### URLs de producción
- Frontend: https://canvas-automation.vercel.app
- Backend: https://canvas-aulas-api.onrender.com
- Swagger: https://canvas-aulas-api.onrender.com/docs

---

## Resumen de la Fase 1

| Sprint | HU | Story Points | Tests añadidos |
|---|---|---|---|
| Sprint 1 | HU-01 a HU-04 | 19 SP | 127 |
| Sprint 2 | HU-05 a HU-08 | 21 SP | 115 |
| Sprint 3 | HU-09 a HU-14 | 23 SP | 111 |
| Sprint 4 | HU-12, HU-13, HU-15 a HU-17 | 18 SP | 81 |
| **Total** | **17 HU** | **81 SP** | **434** |

---

Elaboración propia. Práctica Empresarial — Politécnico Grancolombiano, 2026.
