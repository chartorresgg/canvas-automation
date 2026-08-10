# Necesidades para la versión 2

**Proyecto:** Canvas LMS Automation App
**Autor del análisis:** Carlos Eduardo Guzmán Torres
**Fecha:** 10 de agosto de 2026
**Versión analizada:** commit sobre `main` — v1.0.0

---

## Resumen ejecutivo

La versión 1 **cumple su objetivo**: automatiza el montaje de Aulas Máster en Canvas LMS y reduce el tiempo de 240 a 25 minutos por aula. La arquitectura es limpia, los patrones están correctamente aplicados y hay 434 pruebas unitarias con 71% de cobertura.

Este documento identifica **23 necesidades** para la versión 2, agrupadas en 11 áreas. El hallazgo central es el siguiente:

> El sistema está construido para **funcionar**, pero todavía no para **ser dependido**. Las brechas más graves no están en la funcionalidad, sino en la persistencia de los datos, el control de acceso y la higiene de recursos.

Tres hallazgos son bloqueantes para uso institucional sostenido:

| # | Hallazgo | Impacto |
|---|---|---|
| **N-07** | El historial de auditoría se borra en cada reinicio del servidor | Pérdida total de trazabilidad |
| **N-01** | Cualquier token de Canvas válido concede acceso completo | Sin control de acceso real |
| **N-11** | Los archivos temporales nunca se eliminan tras un despliegue exitoso | Agotamiento de disco |

---

## Metodología

El análisis se realizó por inspección directa del código fuente sobre la rama `main`, verificando cada afirmación contra el archivo y la línea correspondientes. Todas las referencias de código citadas fueron comprobadas.

**Limitación declarada:** la suite de pruebas no pudo ejecutarse localmente durante este análisis (`pytest` no disponible en el entorno). Las cifras de cobertura provienen del `README.md` y del pipeline de CI.

---

## Estado actual — Fortalezas

Conviene registrar lo que **no** necesita cambiar, para no rehacerlo por inercia:

- **Arquitectura limpia real.** Las cuatro capas se respetan; el dominio no importa FastAPI, httpx ni SQLite.
- **Patrones correctamente aplicados.** Facade, Strategy, Factory y Repository cumplen función estructural, no decorativa.
- **Protección contra Zip Slip implementada.** `zip_processor.py:301-321` rechaza rutas absolutas y con `..` antes de extraer.
- **Reintentos con backoff exponencial** en el cliente HTTP de Canvas (`http_client.py:57`).
- **Cancelación activa de despliegues** vía `asyncio.Task.cancel()`.
- **Progreso en tiempo real por SSE**, ya funcionando.
- **`IAuditRepository` desacoplada**, lista para cambiar de motor de persistencia sin tocar el resto del sistema.
- **CI/CD operativo** con GitHub Actions y despliegue automático.

---

# Necesidades identificadas

## A. Seguridad

### N-01 · No existe control de autorización real
**Severidad: Crítica · Esfuerzo: Medio**

El login valida el token llamando a `GET users/self` (`auth.py:64`). Ese endpoint responde correctamente para **cualquier** token de Canvas válido, incluido el de un estudiante.

El mensaje de error incluso afirma un requisito que no se verifica:

```python
# auth.py:72-75
"Verifica que el token sea correcto y tenga permisos
 de administrador en Canvas."
```

**No se comprueba ningún rol.** Cualquier persona con una cuenta en `poli.instructure.com` puede autenticarse y acceder a toda la aplicación, incluido el historial completo de despliegues de todos los analistas.

**Propuesta:** tras validar el token, consultar los roles del usuario en la cuenta institucional (`GET accounts/1/admins` o equivalente) y rechazar el login si no pertenece al grupo autorizado. Mantener una lista de roles permitidos configurable por variable de entorno.

---

### N-02 · Sin límite de tamaño de carga en el servidor
**Severidad: Alta · Esfuerzo: Bajo**

La validación de 500 MB existe **únicamente en el frontend** (`DropZone.tsx:38`). El backend acepta `UploadFile` sin restricción alguna.

Cualquier petición construida fuera de la interfaz —con `curl`, Postman o un script— puede enviar un archivo de tamaño arbitrario y agotar el disco o la memoria del contenedor.

**Propuesta:** validar `Content-Length` en el router antes de leer el cuerpo, y rechazar con `413 Payload Too Large`. El límite debe vivir en una constante compartida, no duplicado entre capas.

---

### N-03 · Sin protección contra ZIP bomb
**Severidad: Alta · Esfuerzo: Bajo**

`_validar_seguridad_zip` protege contra Zip Slip, pero no contra **descompresión desproporcionada**. En `zip_processor.py:197` se acumula `info.file_size` (tamaño descomprimido declarado), pero ese total **no se compara contra ningún límite antes de extraer**.

Un archivo de 1 MB puede declarar 10 GB de contenido descomprimido. La extracción procede sin objeción.

**Propuesta:** antes de `extractall()`, validar dos condiciones:
1. Tamaño descomprimido total por debajo de un máximo configurable
2. Ratio de compresión (descomprimido ÷ comprimido) por debajo de un umbral razonable

---

### N-04 · Validación de rutas incompleta en Windows
**Severidad: Baja · Esfuerzo: Trivial**

```python
# zip_processor.py:317
if nombre.startswith("/") or ".." in nombre.split("/"):
```

La comprobación divide únicamente por `/`. Un ZIP generado en Windows puede usar `\` como separador, y una ruta como `..\..\evil.txt` no quedaría dividida correctamente.

**Propuesta:** normalizar el separador antes de comparar y validar adicionalmente con `Path.resolve()` que el destino final quede dentro del directorio de extracción.

---

### N-05 · Sin limitación de intentos en el login
**Severidad: Media · Esfuerzo: Bajo**

El endpoint `/auth/login` no tiene control de frecuencia. Permite intentos ilimitados de validación de tokens contra la API de Canvas, lo que habilita tanto fuerza bruta como uso del servicio como proxy de validación masiva de tokens ajenos.

**Propuesta:** limitación por IP con ventana deslizante.

---

### N-06 · CORS permite todos los métodos y cabeceras
**Severidad: Baja · Esfuerzo: Trivial**

```python
# main.py:28-29
allow_methods=["*"],
allow_headers=["*"],
```

Los orígenes sí están correctamente restringidos, lo cual es lo importante. Aun así, conviene declarar explícitamente los métodos y cabeceras que la aplicación realmente usa.

---

## B. Persistencia

### N-07 · El historial de auditoría se pierde en cada reinicio
**Severidad: Crítica · Esfuerzo: Medio**

```yaml
# render.yaml:19
AUDIT_DB_PATH: /tmp/audit_log.db
```

El sistema de archivos de Render es **efímero**. Cada redeploy, cada reinicio y cada despertar tras el sleep de 15 minutos del plan Free **elimina la base de datos completa**.

Esto vacía de propósito un módulo entero que ya está construido y probado: `AuditPage.tsx`, los endpoints `/audit` y `/audit/export`, y `SQLiteAuditRepository`. Todo funciona correctamente sobre datos que desaparecen solos.

Para un sistema institucional que debe poder responder *"¿quién desplegó qué aula y cuándo?"*, es la brecha más grave del inventario.

**Propuesta:** implementar `PostgresAuditRepository` sobre la instancia PostgreSQL gratuita de Render. El trabajo de diseño **ya está hecho** — `dependencies.py:90-99` documenta el procedimiento:

```python
# Para migrar a PostgreSQL:
#     1. Crear PostgresAuditRepository(IAuditRepository)
#     2. Retornar esa instancia aquí
#     3. Sin más cambios en el sistema
```

---

### N-08 · Las sesiones no sobreviven a un reinicio ni tienen caducidad
**Severidad: Alta · Esfuerzo: Medio**

`SessionManager` guarda los tokens en un diccionario en memoria (`session_manager.py:47`) sin ningún mecanismo de expiración. Esto produce dos problemas de signo opuesto:

- **Seguridad:** una sesión vive indefinidamente mientras el proceso siga activo. No hay TTL ni renovación.
- **Usabilidad:** en Render Free el servicio duerme a los 15 minutos de inactividad, de modo que en la práctica **los analistas pierden la sesión constantemente** y sin explicación visible.

Además, al ser un singleton por proceso, el diseño no admite escalar a múltiples instancias.

**Propuesta:** añadir TTL explícito con renovación por actividad, y una tarea de limpieza periódica de sesiones expiradas. Si en el futuro se escala horizontalmente, migrar a un almacén compartido.

---

## C. Autenticación y sesión (Login)

### N-09 · Recargar la página cierra la sesión
**Severidad: Alta · Esfuerzo: Bajo**

`TokenContext.tsx:31` mantiene el `sessionId` en `useState`. No se persiste en ningún lado, de modo que **pulsar F5 devuelve al analista a la pantalla de login** en mitad de su trabajo.

Lo más revelador es que el backend **ya tiene resuelto el otro extremo del problema**:

```python
# auth.py:131-132
"El frontend llama a este endpoint al cargar la app para saber
 si el analista ya tiene una sesión válida o debe hacer login."
```

El endpoint `GET /auth/validate` existe, está documentado y probado — **pero el frontend nunca lo llama**, porque no conserva ningún `sessionId` que validar. Es funcionalidad construida y desconectada.

**Propuesta:** persistir el `sessionId` en `sessionStorage` (se limpia al cerrar la pestaña, mejor que `localStorage` para este caso) y llamar a `/auth/validate` al montar la aplicación. Conecta lo que ya está construido en ambos lados.

**Nota de seguridad:** lo que se guardaría es el `sessionId`, no el token de Canvas. El token permanece exclusivamente en la memoria del servidor, como está hoy — ese diseño es correcto y debe mantenerse.

---

### N-10 · Sin cierre de sesión por inactividad
**Severidad: Media · Esfuerzo: Bajo**

No existe expiración por inactividad en el cliente. Combinado con N-08, una sesión abierta en un equipo compartido del área de Ambientes de Aprendizaje permanece utilizable indefinidamente.

**Propuesta:** temporizador de inactividad en el frontend con aviso previo al cierre.

---

## D. Higiene de recursos

### N-11 · Los archivos temporales nunca se eliminan tras un despliegue exitoso
**Severidad: Crítica · Esfuerzo: Bajo**

En `deploy.py`, `shutil.rmtree` aparece **únicamente dentro de bloques `except`** (líneas 113, 144, 327 y 330). En el camino de éxito, el directorio de la tarea —con el ZIP original **y todo su contenido extraído**— permanece en disco de forma permanente.

A aproximadamente 300 MB por aula, tres despliegues exitosos dejan cerca de **1,8 GB** acumulados.

Existe un detalle importante de diagnóstico: **el defecto N-07 es lo que impide que este sea catastrófico hoy.** Como Render borra el disco en cada reinicio, la basura se limpia sola por accidente. Los dos defectos se enmascaran mutuamente.

> **Consecuencia de planeación:** N-07 y N-11 deben resolverse en la misma entrega. Corregir la persistencia sin corregir la limpieza convertiría un problema latente en uno activo.

**Propuesta:** invocar `ZipProcessor.cleanup()` —que ya existe y está probado (`zip_processor.py:279-294`)— en un bloque `finally`, garantizando la limpieza tanto en éxito como en fallo.

---

### N-12 · Fuga de memoria en el registro de tareas
**Severidad: Media · Esfuerzo: Trivial**

`TaskManager.limpiar_completadas()` está implementado en `task_manager.py:124`, pero **no se invoca desde ningún punto del sistema**. Cada despliegue deja su `TaskEntry` y su `asyncio.Queue` residentes de forma indefinida en un proceso con 512 MB de memoria disponible.

**Propuesta:** llamar a la limpieza tras marcar cada tarea como completada, o mediante una tarea periódica de mantenimiento.

---

## E. Rendimiento y archivos grandes

### N-13 · El ZIP se transfiere dos veces
**Severidad: Alta · Esfuerzo: Medio**

El asistente sube el archivo completo en dos ocasiones distintas:

| Paso | Función | Endpoint |
|---|---|---|
| 1 | `uploadZip()` — `api.ts:101` | `POST /deploy/upload` |
| 3 | `startDeploy()` — `api.ts:135` | `POST /deploy` |

El `task_id` que devuelve el primer endpoint (`deploy.py:334`) **nunca se reutiliza**. El segundo endpoint recibe el archivo íntegro otra vez y repite la extracción y normalización completas.

En términos prácticos: desplegar un aula de 300 MB transfiere **600 MB** y descomprime dos veces.

**Propuesta:** reutilizar el `task_id` del primer paso y eliminar el segundo envío del archivo. Reduce a la mitad tanto el tiempo de transferencia como el trabajo del servidor.

---

### N-14 · El procesamiento bloquea el bucle de eventos
**Severidad: Alta · Esfuerzo: Medio**

`upload_zip` está declarada `async def`, pero todo su contenido es síncrono y bloqueante (`deploy.py:313-324`): `shutil.copyfileobj`, `processor.extract()` y `processor.normalize()`.

Durante los 30 a 90 segundos que toma descomprimir un ZIP de 300 MB en el hardware compartido de Render, **el servidor no responde a ninguna otra petición** — ni al health check, ni a otro analista, ni al stream SSE en curso.

Esto incumple una regla de arquitectura declarada en el propio `README.md`, línea 211:

> *"Todo I/O usa `async/await` — sin operaciones síncronas bloqueantes."*

**La documentación describe un sistema que el código no implementa.** Corregirlo cierra además una inconsistencia observable en la sustentación.

**Propuesta:** envolver las operaciones bloqueantes en `anyio.to_thread.run_sync()`. La dependencia `anyio` ya está en `requirements.txt`.

---

### N-15 · El procesamiento ocurre dentro del ciclo de petición
**Severidad: Media · Esfuerzo: Alto**

El tiempo total de la petición es la suma de la transferencia más el procesamiento en el servidor. El tiempo de transferencia es irreducible —los bytes deben viajar—, pero el de procesamiento **no tiene por qué estar dentro de la petición**.

Este es el origen de fondo de los errores de tiempo de espera reportados por los analistas con contenidos superiores a 300 MB.

**Propuesta:** aplicar al endpoint de carga el mismo patrón que ya usa `/deploy`: responder `202 Accepted` de inmediato con un `task_id` y reportar el avance del procesamiento por SSE. La infraestructura ya existe (`_generar_stream_sse`, `deploy.py:450`) — se trata de reutilizarla, no de construirla.

> **Estado:** en la sesión del 10 de agosto de 2026 se aplicó una mitigación parcial — tiempo de espera diferenciado de 15 minutos para cargas y barra de progreso real basada en `onUploadProgress`. Resuelve el síntoma inmediato; la causa de fondo permanece.

---

## F. Validación de contenidos frente a Canvas

### N-16 · La verificación comprueba existencia, no correspondencia
**Severidad: Alta · Esfuerzo: Alto**

El endpoint `GET /deploy/verify/{course_id}` (`deploy.py:530`) ya realiza tres comprobaciones útiles:

1. Qué páginas institucionales existen en el curso
2. Cuántas actividades tienen PDFs vinculados
3. Si el front del curso tiene contenido real (umbral de 300 caracteres)

La limitación es de naturaleza conceptual: **verifica que algo existe en Canvas, no que corresponda a lo que se cargó.**

Hoy no es posible responder preguntas como:

- ¿Los 47 archivos del ZIP son exactamente los 47 archivos que quedaron en Canvas?
- ¿Cuál archivo específico falta?
- ¿El PDF vinculado en la actividad 3 es el que venía en la carpeta `3. Material de trabajo`?
- ¿Algún archivo se subió con nombre alterado por la normalización sin que el analista lo advierta?

Un despliegue con el 60% de los archivos subidos y todas las páginas creadas se reporta hoy como correcto.

**Propuesta:** construir una verificación por **diferencia real**:

1. Al procesar el ZIP, generar un manifiesto: ruta relativa, nombre normalizado, tamaño y hash de cada archivo
2. Tras el despliegue, consultar el inventario efectivo del curso en Canvas
3. Contrastar ambos conjuntos y reportar tres categorías: **presentes**, **faltantes** y **inesperados**
4. Mostrar el resultado como un informe descargable, adjunto al registro de auditoría

Esta es probablemente la necesidad con **mayor valor institucional** de todo el inventario: convierte la verificación de un indicador aproximado en una garantía comprobable.

---

### N-17 · La lista de páginas esperadas está fijada en el código
**Severidad: Media · Esfuerzo: Bajo**

Los slugs institucionales están escritos directamente en `deploy.py:495-515`, con cuatro unidades fijas:

```python
("unidad-1-material-fundamental", "Material Fundamental U1"),
("unidad-2-material-fundamental", "Material Fundamental U2"),
...
```

Un aula con tres o cinco unidades produce un informe de verificación engañoso: reportará faltantes que no debían existir, o dejará de comprobar páginas que sí.

**Propuesta:** derivar la lista esperada del modelo instruccional y del contenido real del ZIP, no de una constante fija.

---

## G. Usuario administrador y roles

### N-18 · No existe distinción entre tipos de usuario
**Severidad: Alta · Esfuerzo: Alto**

Todos los usuarios autenticados tienen exactamente las mismas capacidades. En particular:

- El endpoint `/audit` **no filtra por usuario** (`audit.py:33`): cualquier analista consulta el historial completo de todos sus compañeros
- No hay forma de revocar el acceso de una persona sin intervenir en Canvas
- No existe visibilidad operativa: cuántos despliegues hay en curso, cuáles fallaron, quién está usando el sistema
- No hay administración de plantillas ni de parámetros desde la interfaz

**Propuesta para v2 — dos roles:**

| Rol | Capacidades |
|---|---|
| **Analista** | Desplegar aulas · Ver únicamente su propio historial · Verificar sus despliegues |
| **Administrador** | Todo lo anterior · Historial completo de todos los usuarios · Panel operativo · Gestión de plantillas · Revocación de sesiones activas |

La asignación de rol debe derivarse de los permisos reales del usuario en Canvas (ligado a N-01), no de una lista mantenida a mano.

---

### N-19 · Sin panel de operación
**Severidad: Media · Esfuerzo: Medio**

No existe una vista que responda, en un momento dado: cuántos despliegues están en curso, cuál es la tasa de éxito reciente, qué errores se repiten, cuánto espacio en disco se está usando.

**Propuesta:** vista de administrador con métricas agregadas, alimentada por el registro de auditoría una vez sea persistente (N-07).

---

## H. Experiencia de usuario

### N-20 · La aplicación no tiene rutas navegables
**Severidad: Media · Esfuerzo: Medio**

La navegación se resuelve con `useState` en `App.tsx:12`, sin enrutador. Consecuencias directas:

- La URL nunca cambia: **no se puede compartir un enlace** a una vista concreta
- Los botones **atrás y adelante del navegador no funcionan**
- Recargar devuelve siempre a la vista inicial — y, por N-09, al login
- No se puede marcar el historial como favorito

**Propuesta:** incorporar React Router con rutas reales (`/deploy`, `/historial`, `/benchmark`, `/admin`) y protección de rutas según sesión y rol.

---

### N-21 · Un despliegue interrumpido debe rehacerse por completo
**Severidad: Alta · Esfuerzo: Alto**

Existen reintentos a nivel de archivo individual (`MAX_REINTENTOS_POR_ARCHIVO = 3`, `file_repository.py:51`), pero no a nivel de despliegue. Si el proceso falla cuando ya subió el 80% del contenido, el analista debe reiniciar desde cero: volver a cargar el ZIP, volver a esperar la transferencia completa y volver a subir los archivos que ya estaban en Canvas.

Con aulas de 300 MB, eso puede significar perder más de veinte minutos de trabajo.

**Propuesta:** persistir el estado de avance por archivo y permitir reanudar desde el último punto confirmado. Depende de N-07 (persistencia real).

---

### N-22 · Comunicación insuficiente de errores y espera
**Severidad: Media · Esfuerzo: Bajo**

Se corrigió parcialmente en la carga de archivos, pero el patrón persiste en otras partes del sistema. En particular, el arranque en frío de Render —entre 30 y 60 segundos según el `README.md`— **no se comunica en la interfaz**: el analista percibe una aplicación congelada, sin señal de que el servidor está despertando.

**Propuesta:** estado explícito de "conectando con el servidor" al iniciar, con explicación de la demora esperada. Revisar todos los mensajes de error para que indiquen qué hacer, no solo qué falló.

---

## I. Rediseño de interfaz y branding

### N-23 · Identidad visual sin definir
**Severidad: Media · Esfuerzo: Medio**

El sistema se identifica hoy de tres formas distintas según dónde se mire:

| Ubicación | Texto |
|---|---|
| `index.html:7` | Automatización de Aulas Máster |
| `LoginPage.tsx` | Automatización de Aulas Máster |
| `DeployPage.tsx:139` | Canvas LMS Automation |
| `main.py:10` | Canvas LMS Automation API |
| `README.md:1` | Canvas LMS Automation App |

El logotipo es una letra «C» sobre un cuadrado azul (`LoginPage.tsx:68-70`) — un marcador de posición, no una identidad.

**Consideración estratégica:** el nombre actual **ata el producto a Canvas**. Si la institución migrara de LMS, o si la herramienta se extendiera a otra plataforma, el nombre quedaría desactualizado. Un nombre propio evita ese techo.

*(Se evaluó «Zaia» como candidato en agosto de 2026: dos sílabas, pronunciación inequívoca en español, inicial poco frecuente que favorece el recuerdo, y sin atadura a la plataforma. Decisión aplazada.)*

**Propuesta:**
1. Fijar un nombre y usarlo de forma consistente en las cinco ubicaciones
2. Emparejarlo siempre con un descriptor fijo — *Nombre · Automatización de Aulas Máster*
3. Sustituir el logotipo provisional
4. Definir paleta, tipografía y espaciado como sistema documentado

> **Advertencia técnica:** el cambio de nombre debe limitarse a las cadenas visibles y la documentación. **No renombrar** el repositorio ni el servicio `canvas-aulas-api` en Render: esto último modifica la URL `.onrender.com` y rompe la variable `VITE_API_URL` configurada en Vercel.

---

## J. Calidad y pruebas

### Sin pruebas de integración
**Severidad: Alta · Esfuerzo: Medio**

El directorio `tests/integration/` existe pero contiene únicamente `__init__.py`. Las 434 pruebas son unitarias, con Canvas simulado mediante mocks.

El riesgo concreto: si Canvas modifica el formato de alguna respuesta, **ninguna prueba lo detecta**. Los mocks seguirán devolviendo la forma antigua y la suite pasará en verde mientras producción falla.

**Propuesta:** pruebas de integración con `respx` —compatible con httpx, ya presente en el stack— que ejerciten el flujo completo contra respuestas grabadas de Canvas.

### Dependencias de desarrollo en producción
**Severidad: Baja · Esfuerzo: Trivial**

`requirements.txt` incluye `pytest` y `coverage`, que Render instala en cada compilación. El paso de instalación de dependencias ya es el más lento del despliegue.

**Propuesta:** separar `requirements-dev.txt`.

---

## K. Documentación

### El README describe versiones que no corresponden
**Severidad: Baja · Esfuerzo: Trivial**

| Componente | README | `package.json` real |
|---|---|---|
| React | 18 | 19.2.5 |
| Vite | 5 | 8.0.10 |
| TypeScript | 5 | 6.0.2 |

Súmese la regla de arquitectura sobre `async/await` que el código incumple (N-14). En una sustentación, una documentación que no corresponde al código resta credibilidad al conjunto.

### `orchestrator.py` concentra demasiada responsabilidad
**Severidad: Baja · Esfuerzo: Medio**

706 líneas y 12 métodos. Todavía manejable, pero es el archivo con mayor tendencia a crecer y ya empieza a acumular responsabilidades heterogéneas.

**Propuesta:** vigilar su evolución; extraer la composición de páginas a un colaborador propio si supera las 800 líneas.

---

# Matriz de priorización

| ID | Necesidad | Severidad | Esfuerzo | Prioridad |
|---|---|---|---|---|
| N-07 | Persistencia del historial | Crítica | Medio | **1** |
| N-11 | Limpieza de temporales | Crítica | Bajo | **1** |
| N-01 | Control de autorización | Crítica | Medio | **2** |
| N-13 | Doble transferencia del ZIP | Alta | Medio | **2** |
| N-09 | Sesión persistente al recargar | Alta | Bajo | **3** |
| N-14 | Bloqueo del bucle de eventos | Alta | Medio | **3** |
| N-02 | Límite de carga en servidor | Alta | Bajo | **3** |
| N-03 | Protección ZIP bomb | Alta | Bajo | **3** |
| N-12 | Fuga de memoria en tareas | Media | Trivial | **3** |
| N-08 | Caducidad de sesiones | Alta | Medio | **4** |
| N-16 | Validación por diferencia real | Alta | Alto | **4** |
| N-18 | Roles y administrador | Alta | Alto | **4** |
| N-21 | Reanudación de despliegues | Alta | Alto | **5** |
| N-20 | Rutas navegables | Media | Medio | **5** |
| N-23 | Identidad visual | Media | Medio | **5** |
| N-17 | Páginas esperadas dinámicas | Media | Bajo | **5** |
| N-19 | Panel de operación | Media | Medio | **6** |
| N-22 | Comunicación de estado | Media | Bajo | **6** |
| N-10 | Cierre por inactividad | Media | Bajo | **6** |
| N-05 | Límite de intentos de login | Media | Bajo | **6** |
| N-04 | Rutas ZIP en Windows | Baja | Trivial | **7** |
| N-06 | CORS explícito | Baja | Trivial | **7** |

---

# Propuesta de alcance para la versión 2

## Entrega 1 — Fundamentos *(bloqueante)*

**N-07 · N-11 · N-12 · N-02 · N-03**

Persistencia real en PostgreSQL, limpieza de recursos y endurecimiento de las cargas. Estas necesidades deben ir juntas: como se explica en N-11, corregir la persistencia sin corregir la limpieza convierte un problema latente en uno activo.

*Resultado:* el sistema deja de perder datos y de acumular basura.

## Entrega 2 — Acceso y control

**N-01 · N-09 · N-08 · N-10 · N-05**

Autorización real por rol de Canvas, sesión que sobrevive a una recarga, caducidad y limitación de intentos. N-09 es de esfuerzo bajo y alto impacto percibido: conecta el endpoint `/auth/validate` que ya existe sin usarse.

*Resultado:* el acceso deja de ser abierto y la sesión deja de perderse sola.

## Entrega 3 — Rendimiento de cargas

**N-13 · N-14 · N-15**

Elimina la doble transferencia, libera el bucle de eventos y saca el procesamiento del ciclo de petición.

*Resultado:* se resuelve la causa de los errores de tiempo de espera reportados por los analistas, no solo el síntoma.

## Entrega 4 — Garantía de contenido

**N-16 · N-17**

Verificación por diferencia real entre el ZIP cargado y lo efectivamente presente en Canvas.

*Resultado:* la afirmación «el aula quedó montada correctamente» pasa de ser un indicador aproximado a una garantía comprobable.

## Entrega 5 — Producto e identidad

**N-18 · N-19 · N-20 · N-21 · N-23 · N-22**

Roles, panel administrativo, enrutamiento, reanudación e identidad visual.

---

## Recomendación

Si la versión 2 tuviera alcance limitado, la recomendación es ejecutar **las entregas 1, 2 y 3**, y trasladar las entregas 4 y 5 a una versión posterior.

El razonamiento: las entregas 1 y 2 corrigen problemas de **correctitud** —el sistema hoy pierde datos y no controla quién entra—, y ninguna funcionalidad nueva compensa eso. La entrega 3 resuelve el único problema que los usuarios **ya están reportando**.

Las entregas 4 y 5 aportan valor considerable, pero mejoran un sistema que primero debe ser confiable.

Adicionalmente, las entregas 1 y 2 construyen una narrativa técnica sólida para la sustentación: la detección de que dos defectos de recursos se enmascaraban mutuamente, y la de que un control de acceso documentado no estaba implementado, demuestran criterio de ingeniería con más fuerza que agregar una funcionalidad más.

---

## Anexo — Índice de referencias verificadas

| Referencia | Necesidad |
|---|---|
| `render.yaml:19` | N-07 |
| `backend/app/presentation/routers/auth.py:64,72-75,121-144` | N-01, N-09 |
| `backend/app/presentation/session_manager.py:47` | N-08 |
| `backend/app/presentation/task_manager.py:124` | N-12 |
| `backend/app/presentation/routers/deploy.py:113,144,327,330` | N-11 |
| `backend/app/presentation/routers/deploy.py:313-324` | N-14 |
| `backend/app/presentation/routers/deploy.py:334,495-515,530` | N-13, N-16, N-17 |
| `backend/app/presentation/dependencies.py:90-99` | N-07 |
| `backend/app/domain/services/zip_processor.py:197,279-294,301-321` | N-03, N-04, N-11 |
| `backend/app/infrastructure/canvas/file_repository.py:51` | N-21 |
| `backend/app/presentation/routers/audit.py:33` | N-18 |
| `backend/app/main.py:10,28-29` | N-06, N-23 |
| `frontend/src/App.tsx:12` | N-20 |
| `frontend/src/context/TokenContext.tsx:31` | N-09 |
| `frontend/src/services/api.ts:101,135` | N-13 |
| `frontend/src/features/deploy/components/DropZone.tsx:38` | N-02 |
| `frontend/src/features/deploy/DeployPage.tsx:139` | N-23 |
| `backend/tests/integration/` | Pruebas de integración |
| `README.md:211` | N-14 |
