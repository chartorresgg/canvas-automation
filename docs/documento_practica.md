Desarrollo de un prototipo de aplicación web para la automatización del montaje de Aulas Máster mediante la API de Canvas LMS en el Politécnico Grancolombiano

Carlos Eduardo Guzmán Torres

Institución Universitaria Politécnico Grancolombiano

Facultad de Ingeniería, Diseño e Innovación

Ingeniería de Sistemas – Opción de Grado

Tutor: Javier Fernando Niño Velásquez

Asesor: Wilson Eduardo Soto Forero

Bogotá D.C., 02 de mayo de 2026

Dedicatoria

A mi mamá, Judith, por ser mi mayor inspiración, mi motor de vida y la razón principal detrás de cada uno de mis logros. Todo este esfuerzo y dedicación llevan tu nombre.

A mis dos hermanas, Karen y Marcela, por su apoyo incondicional y por acompañarme durante todos estos años de carrera. Este triunfo también es de ustedes.

Agradecimientos

Deseo expresar mi más sincero agradecimiento a todas las personas que hicieron posible el desarrollo de este proyecto y a la culminación de mis estudios de pregrado.

A mi asesor de Práctica Empresarial, el ingeniero Wilson Soto Forero por su orientación técnica, su rigor académico y sus valiosos consejos que elevaron la calidad de este proyecto.

A la Líder de Ambientes de Aprendizaje, Andrea Alfonso Ayala, por su confianza en mi trabajo y por su disposición constante en validar y retroalimentar este proyecto.

Al docente de la asignatura de Opción de Grado, Javier Niño Velásquez, por sus enseñanzas fundamentales, exigiendo siempre una excelencia investigativa y metodológica que requiere un proyecto de grado.

Finalmente, a la institución y a todos los docentes que hicieron parte de mi formación como Ingeniero de Sistemas, por brindarme los conocimientos fundamentales para afrontar los retos tecnológicos del mundo real.

Resumen

El presente proyecto de Práctica Empresarial desarrolla un prototipo de aplicación web diseñado para automatizar el montaje y configuración de Aulas Máster en la plataforma Canvas LMS del Politécnico Grancolombiano. Operativamente, el equipo de Ambientes de Aprendizaje invierte un promedio de 240 minutos de trabajo manual por asignatura, limitando la capacidad de respuesta frente a la escala del modelo virtual. Para resolver esta problemática, se aplicó un enfoque de investigación cuantitativa de alcance preexperimental, utilizando el marco de trabajo ágil Scrum como mecanismo de la aplicación tecnológica. A nivel técnico, se refactorizó un código legado orientado a consola para construir una arquitectura cliente-servidor, mediante FastAPI para la lógica de procesamiento masivo y comunicación asíncrona con la API de Canvas, y React.js para la interfaz gráfica. Como resultado proyectado de esta intervención empírica, la herramienta permite descentralizar el proceso operativo, asegurando un entorno de ejecución local autónomo que reduce el tiempo de montaje a un máximo de 25 minutos por aula, lo que representa una optimización operativa del 89,58% y una mitigación directa del error humano.

**Palabras clave:** Automatización, Canvas LMS, FastAPI, Scrum, React.js.

Abstract

This Business Internship project develops a web application prototype designed to automate the assembly and configuration of Master Courses within the Canvas LMS platform at Politécnico Grancolombiano. Operationally, the Learning Environments team invests an average of 240 minutes of manual labor per subject, limiting the response capacity to the scale of the virtual model. To solve this problem, a quantitative pre-experimental research approach was applied, using the Scrum agile framework as the mechanism for building the technological intervention. Technically, a legacy console-oriented script was refactored to build a client-server architecture, using FastAPI for mass processing logic and asynchronous communication with the Canvas API, and React.js for the graphical user interface. As a projected result of this empirical intervention, the tool allows the operational process to be decentralized, ensuring an autonomous local execution environment that reduces the assembly time to a maximum of 25 minutes per course, representing an operational optimization of 89.58% and a direct mitigation of human error.

**Keywords:** Automation, Canvas LMS, FastAPI, Scrum, React.js.

Tabla de contenidos

[1\. Introducción 8](#_Toc228731360)

[1.1 Descripción de la empresa 8](#_Toc228731361)

[1.2 Datos generales de la Práctica Empresarial 10](#_Toc228731362)

[1.3 Formulación del problema 11](#_Toc228731363)

[1.4 Pregunta de Investigación 12](#_Toc228731364)

[1.5 Justificación 12](#_Toc228731365)

[1.6 Objetivos 17](#_Toc228731366)

[1.7 Alcance y límites del proyecto 18](#_Toc228731367)

[2\. Marco teórico 20](#_Toc228731368)

[2.1 Fundamentos de Ingeniería de Software 21](#_Toc228731369)

[2.2 Plataformas de Gestión del Aprendizaje 29](#_Toc228731370)

[2.3 Interfaces de Programación de Aplicaciones 35](#_Toc228731371)

[2.4 Gestión de Proyectos de Software 39](#_Toc228731372)

[3\. Método 45](#_Toc228731373)

[3.1 Tipo de estudio e hipótesis de optimización 45](#_Toc228731374)

[3.2 Fases del proceso de desarrollo tecnológico 46](#_Toc228731375)

[3.3 Población, muestra y recolección de datos 49](#_Toc228731376)

[3.4 Diseño y marco de trabajo ágil 50](#_Toc228731377)

[3.5 Descripción de actividades 50](#_Toc228731378)

[3.6 Cronograma de actividades 53](#_Toc228731379)

[3.7 Entregables 55](#_Toc228731380)

[4\. Desarrollo e Implementación de la Solución Tecnológica 56](#_Toc228731381)

[4.1 Levantamiento de requerimientos 56](#_Toc228731382)

[4.2 Definición de las Historias de Usuario 58](#_Toc228731383)

[4.3 Sprint 1: Modelado y Prototipo Navegable 61](#_Toc228731384)

[4.4 Sprint 2: Integración con API Canvas 75](#_Toc228731385)

[4.5 Sprint 3: Automatización y Monitoreo 77](#_Toc228731386)

[4.6 Sprint 4: Validación, Pruebas y Resiliencia 78](#_Toc228731387)

[5\. Resultados y hallazgos 78](#_Toc228731388)

[5.1 Presentación y análisis de los datos recolectados 78](#_Toc228731389)

[5.2 Contrastación de la hipótesis de optimización 79](#_Toc228731390)

[5.3 Impacto en capacidad operativa institucional 80](#_Toc228731391)

[6\. Conclusiones y recomendaciones 81](#_Toc228731392)

[6.1 Conclusiones 81](#_Toc228731393)

[6.2 Recomendaciones y trabajos futuros 81](#_Toc228731394)

[7\. Bibliografía 82](#_Toc228731395)

[8\. Anexos 86](#_Toc228731396)

**Listado de tablas**

[**Tabla 1** _Datos generales de la Práctica Empresarial_ 10](#_Toc228726787)

[**Tabla 2** _Tiempos operativos de montaje_ 14](#_Toc228726788)

[**Tabla 3** _Cronograma de Sprints e Incrementos_ 54](#_Toc228726789)

[**Tabla 4** _Product Backlog: Estimaciones y asignación Ágil por Incrementos_ 59](#_Toc228726790)

[**Tabla 5** _Stack Tecnológico y Herramientas de Desarrollo_ 61](#_Toc228726791)

[**Tabla 6** _Especificación de Caso de Uso: UC-01 Cargar archivo ZIP_ 64](#_Toc228726792)

**Listado de figuras**

[**Figura 1** _Fases del modelo metodológico híbrido para el desarrollo tecnológico._ 48](#_Toc228726785)

[**Figura 2** _Diagrama de Casos de Uso de la Aplicación Web de Automatización_ 63](#_Toc228726786)

# Introducción

El presente documento expone el desarrollo, implementación y resultados del proyecto de Práctica Empresarial orientado a la optimización de procesos tecnológicos en la gestión de plataformas académicas. A medida que los modelos de educación virtual y a distancia escalan, la administración eficiente de los Sistemas de Gestión de Aprendizaje (LMS) se convierte en un pilar fundamental para garantizar la continuidad y calidad del servicio educativo. En este escenario, la automatización de tareas operativas y repetitivas emerge como una solución estratégica frente a las limitantes de capacidad instalada de los equipos de trabajo. A través de la aplicación desarrollada durante la presente Práctica Empresarial, este proyecto detalla la transición de un proceso de montaje de contenidos netamente manual hacia una solución de software estructurada, abordando las fases de levantamiento de requerimientos, diseño arquitectónico y desarrollo de un Prototipo Funcional (MVP) adaptado a las necesidades operativas del Politécnico Grancolombiano.

## Descripción de la empresa

El Politécnico Grancolombiano es una institución de educación superior colombiana fundada en 1980, con sede principal en Bogotá. Es una de las instituciones pioneras en Colombia en la adopción de entornos virtuales de aprendizaje a escala, con una matrícula que supera los 55.000 estudiantes activos en modalidad virtual y a distancia, y una oferta académica que abarca programas técnicos, tecnológicos, profesionales universitarios y de posgrado. Su plataforma oficial de gestión académica es Canvas LMS, a través de la cual administra la totalidad de sus cursos bajo estándares de diseño instruccional definidos por el equipo de la Gerencia de Educación Virtual y lineamientos de montaje de contenidos por parte del equipo de Ambientes de Aprendizaje que hace parte de la Gerencia de Operaciones.

Esta escala operativa convierte la gestión de aulas virtuales en un proceso crítico e intensivo: cada período académico implica la configuración y cargue de contenidos para un volumen cercano a los 100 cursos activos, de acuerdo con las cifras aportadas por el equipo de Ambientes de Aprendizaje. En el contexto institucional del Politécnico Grancolombiano, la base de esta operación recae sobre el concepto de ‘Aula Máster’, definida como el curso semilla o plantilla principal de cada asignatura que contiene la totalidad de los recursos educativos, que incluyen materiales multimedia, documentos PDF, contenidos interactivos de Articulate Storyline, videos y actividades evaluativas. Estas Aulas Máster son posteriormente duplicadas para crear los cursos específicos donde interactuarán los estudiantes. Es en este contexto donde se desarrolla la solución propuesta, cuya automatización del proceso de cargue en Canvas LMS responde a una necesidad estructural de una institución cuya operación académica depende de manera directa de la disponibilidad oportuna y correcta configuración de sus aulas virtuales.

## Datos generales de la Práctica Empresarial

A continuación, se presentan los datos institucionales y de identificación correspondientes al practicante, la empresa y los responsables académicos y organizacionales que acompañan el desarrollo de la práctica empresarial durante el período 2026-1.

**Tabla 1**  
_Datos generales de la Práctica Empresarial_

|     |     |
| --- | --- |
| **Ítem** | **Descripción** |
| **Facultad** | Facultad de Ingeniería, Diseño e Innovación |
| **Departamento Académico** | Ingeniería de Sistemas |
| **Nombre completo del practicante** | Carlos Eduardo Guzmán Torres |
| **Código de estudiante** | 100294423 |
| **Cédula** | 1020763830 |
| **Correo electrónico** | cedguzman@poligran.edu.co |
| **Cargo asignado** | Practicante de Ingeniería de Software |
| **Empresa** | Politécnico Grancolombiano |
| **Fecha de inicio** | 2/02/2026 |
| **Fecha de finalización** | 10/06/2026 |
| **Jefe inmediato** | Andrea Alfonso Ayala |
| **Cargo de jefe inmediato** | Líder de Ambientes de Aprendizaje |
| **Asesor de Práctica Empresarial** | Wilson Eduardo Soto Forero |
| **Área de conocimiento** | Ingeniería de Software |
| **Título del anteproyecto** | Desarrollo de un prototipo de aplicación web para la automatización del montaje de Aulas Máster mediante la API de Canvas LMS en el Politécnico Grancolombiano |
| **Palabras clave** | _Automatización, Canvas LMS, Especificación de requerimientos, Ingeniería de Software_ |

_Nota: Tabla elaborada por el autor del documento._

## Formulación del problema

El proceso de configuración y montaje masivo de contenidos para las Aulas Máster en Canvas LMS del Politécnico Grancolombiano presenta una limitación operativa significativa. En su ejecución manual, este procedimiento consume un promedio de 240 minutos (4 horas) por persona para una sola asignatura. Esta métrica fue establecida y validada mediante un levantamiento de información operativa en conjunto con la Líder de Ambientes de Aprendizaje y el equipo de analistas del área que lo conforman. Esta carga de trabajo limita la capacidad del área a un máximo de montaje de 2 a 3 cursos diarios por analista (es decir, un máximo de 6 a 9 cursos para el equipo completo, en el día). Además, la intervención manual conlleva una alta propensión a errores operativos.

Si bien existe un script en Python desarrollado en 2025 que reduce este tiempo de procesamiento a aproximadamente 25 minutos (una optimización del 89,58%), la condición actual de ejecución representa una barrera técnica relevante. Actualmente, los tres analistas del equipo deben operar este código directamente desde el entorno de desarrollo integrado (IDE) en sus equipos locales. Esta dependencia de un IDE para ejecutar tareas operativas genera un riesgo de manipulación accidental del código, dificulta la trazabilidad de los errores, impide la escalabilidad de la solución a otros miembros menos técnicos del equipo y carece de una interfaz de usuario apropiada para el uso intuitivo de la aplicación. Por lo tanto, el problema se presenta en la ausencia de una arquitectura de software que descentralice el uso del script, garantizando su usabilidad, seguridad y estabilidad sin depender de entornos de programación ni de los tiempos de respuesta del área de Tecnología del Politécnico Grancolombiano.

## Pregunta de Investigación

A partir de la identificación de la limitación operativa detallada en la formulación del problema, donde la carga de trabajo manual restringe la escalabilidad del modelo educativo virtual, se hace evidente la necesidad de intervenir el proceso mediante la ingeniería de software. El reto principal no radica únicamente en la viabilidad técnica de conectar sistemas, sino en el impacto empírico que esta intervención generará sobre la productividad del equipo de Ambientes de Aprendizaje. Por lo anterior, el desarrollo de la solución propuesta de Práctica Empresarial se guiará bajo la siguiente pregunta de investigación:

¿En qué medida la implementación de un prototipo funcional de aplicación web sobre la API de Canvas LMS reduce el tiempo operativo de montaje masivo de Aulas Máster en el Politécnico Grancolombiano?

## Justificación

La ejecución de la presente Práctica Empresarial se fundamenta en la necesidad estratégica de adaptar la escalabilidad operativa del Politécnico Grancolombiano frente al crecimiento sostenido de su modelo de educación virtual. Para comprender el valor e impacto del proyecto, se desarrollaron las siguientes tres dimensiones fundamentales: la conveniencia institucional, el impacto práctico y el aporte metodológico a nivel de arquitectura de software.

### Impacto de conveniencia y mitigación de riesgos

En primera instancia, la conveniencia de este proyecto radica en la necesidad imperativa de descentralizar la tecnología y mitigar riesgos operativos. Si este desarrollo no se llevara a cabo, la automatización lograda mediante el _script_ base de Python quedaría relegada a un entorno de desarrollo integrado (IDE) altamente técnico, generando una dependencia absoluta de personal especializado. En la actualidad, el conocimiento operativo de la automatización se encuentra centralizado, lo que en términos de gestión de TI representa un riesgo de "conocimiento en silos". Esto implicaría que, ante cualquier eventualidad técnica, ausencia del personal capacitado o un escalamiento abrupto en el volumen de cursos demandados por la institución, el equipo de Ambientes de Aprendizaje correría el riesgo inminente de retornar a la operatividad 100% manual.

Al refactorizar esta solución y empaquetarla en una aplicación web, se elimina la curva de aprendizaje técnica y se "democratiza" el uso de la herramienta. De este modo, la conveniencia del proyecto radica en la prevención de un colapso en la capacidad de respuesta institucional durante los picos de montaje académico, asegurando la continuidad del negocio y la autonomía tecnológica del área a largo plazo.

### Impacto práctico y de optimización

Desde una perspectiva práctica, la trascendencia de este aplicativo web es inmediata, medible y soluciona un problema corporativo real que afecta directamente la productividad del área de Ambientes de Aprendizaje. Los beneficiarios directos son los miembros del equipo de esta área, quienes experimentarán una reducción drástica de tareas repetitivas y transaccionales que no aportan valor pedagógico, mitigando el cansancio y la propensión al error humano. Como beneficiarios indirectos, se encuentra la totalidad de la comunidad estudiantil, la cual requiere que sus aulas virtuales estén desplegadas y configuradas sin demoras para el inicio de sus períodos académicos.

Para dimensionar el beneficio e impacto práctico que fundamenta este proyecto, se llevó a cabo un levantamiento de información operativa en mesas de trabajo conjunto con la coordinación y el equipo de analistas del área. En estos espacios se cuantificaron los tiempos exactos de la operación, evidenciando un retorno de inversión en tiempo extraordinario. Como se detalla en la Tabla 2, la implementación del sistema garantiza una optimización neta del 89,58% en el ciclo de trabajo por cada Aula Máster:

**Tabla 2**  
_Tiempos operativos de montaje_

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| **Etapa del Proceso** | **Proceso Manual** | **Proceso Automatizado** | **Beneficio (Ahorro)** | **Porcentaje de Ahorro** |
| Configuración inicial | 20 minutos | 1 minuto | 19 minutos | 95,00% |
| Subida de archivos | 10 minutos | 6 minutos | 4 minutos | 40,00% |
| Creación de páginas | 115 minutos | 1 minuto | 114 minutos | 99,13% |
| Vinculación de PDFs | 40 minutos | 1 minuto | 39 minutos | 97,50% |
| Página principal | 40 minutos | 1 minuto | 39 minutos | 97,50% |
| Revisión final | 15 minutos | 15 minutos | 0 minutos | 0,00% |
| **Impacto Total** | **240 minutos** | **25 minutos** | **215 minutos** | **89,58%** |

_Nota_. Tabla elaborada por el equipo de Ambientes de Aprendizaje.

Como se evidencia en la tabla anterior, tareas críticas como la creación de páginas y la vinculación de recursos pasan de consumir casi tres horas de trabajo a resolverse en apenas dos minutos, consolidando una solución tecnológica con un impacto directo en la productividad de la institución.

Como se evidencia en la Tabla 2, tareas relacionadas con la generación de estructuras lógicas (creación de páginas y vinculación de PDFs) presentan una reducción del tiempo superior al 97%. Sin embargo, la etapa de "Subida de archivos" presenta una optimización porcentualmente menor (del 40%), estabilizándose en un promedio de 6 minutos automatizados. Esto no obedece a una ineficiencia del código, sino a restricciones físicas y de infraestructura de red. La transferencia de paquetes interactivos pesados (como archivos de Articulate Storyline o multimedia) está supeditada al ancho de banda de la red institucional y a las políticas de _Rate Limiting_ (límite de peticiones por segundo) impuestas por los servidores de la API de Canvas LMS. A pesar de este tiempo de transferencia, la principal ganancia radica en que el sistema ejecuta esta subida de forma asíncrona y desatendida, liberando al analista de tener que supervisar la carga barra por barra.

### Impacto teórico-metodológico

Finalmente, a nivel teórico y metodológico en el campo de la Ingeniería de Sistemas, este proyecto documenta la aplicación práctica del ciclo de vida del desarrollo de software (SDLC) para la resolución de limitantes operativos en la administración de tecnologías educativas. Más que proponer un nuevo estándar arquitectónico para la institución, el proyecto valida una hipótesis operativa fundamental: la viabilidad de descentralizar herramientas de automatización hacia equipos no técnicos mediante el diseño de interfaces centradas en el usuario.

Metodológicamente, el proyecto demuestra cómo la refactorización de un código base aislado (orientado a consola) hacia un modelo web interactivo permite que áreas operativas como Ambientes de Aprendizaje gestionen su propia eficiencia. Esto genera conocimiento aplicable sobre cómo las metodologías ágiles de ingeniería de software pueden aliviar la carga de soporte del área de Tecnología central, proveyendo a los usuarios finales de herramientas de integración seguras, eficientes y autónomas dentro del ecosistema de Canvas LMS.

## Objetivos

### 1.6.1 Objetivo general

Desarrollar un prototipo funcional de aplicación web para automatizar el proceso de montaje de Aulas Máster en la plataforma Canvas LMS del Politécnico Grancolombiano, con el fin de optimizar los tiempos operativos y reducir el margen de error humano.

### Objetivos específicos

1.  Definir los requerimientos funcionales, técnicos y la arquitectura del software a través de las historias de usuario, para establecer el alcance técnico y las directrices de construcción de la aplicación.
2.  Construir los componentes de software requeridos para el procesamiento de archivos y la comunicación asíncrona con la API de Canvas LMS para habilitar el despliegue automatizado de los contenidos.
3.  Evaluar el rendimiento y la usabilidad del prototipo de la aplicación web mediante pruebas operativas de carga y simulación en un entorno local, para comprobar la reducción del tiempo de montaje a los 25 minutos esperados.

## Alcance y límites del proyecto

El alcance de esta Práctica Empresarial comprende el ciclo de vida de desarrollo de un Producto Mínimo Viable (MVP) tipo aplicación web, diseñado exclusivamente para el uso interno de los analistas del equipo de Ambientes de Aprendizaje del Politécnico Grancolombiano. El proyecto incluye el levantamiento de los requerimientos, el diseño de la arquitectura del software, el desarrollo de una interfaz gráfica y la construcción de un motor de procesamiento que empaquete las funcionalidades del script original. La solución permitirá a los usuarios ejecutar la automatización de despliegue de contenidos en Canvas LMS sin necesidad de interactuar con código fuente. El proyecto finalizará con la entrega del código fuente debidamente comentado y versionado en GitHub, la validación de su funcionamiento en un entorno de ejecución local y la sustentación final de la Práctica Empresarial.

Para garantizar la viabilidad técnica y operativa de este alcance, las metas del proyecto fueron estructuradas y validadas bajo la **Metodología SMART** (descrita en el apartado 2.4.3 de este documento). En este sentido, la formulación del proyecto se define como **Específica (Specific)** al enfocarse exclusivamente en la automatización del montaje de Aulas Máster vía API, descartando otros procesos académicos; **Medible (Measurable)** mediante la comprobación matemática de la reducción del tiempo operativo de 240 a 25 minutos; **Alcanzable (Achievable)** al acotar el desarrollo a un entorno de ejecución local, a través de una arquitectura de código abierto que no requiere infraestructura de servidores institucionales; **Relevante (Relevant)** al solucionar directamente un cuello de botella que restringe la capacidad de respuesta y productividad del equipo; y con un **Tiempo definido (Time-bound)**, al estar rigurosamente enmarcado en el calendario de la Práctica Empresarial, debiendo culminar sus fases antes de junio de 2026.

Para asegurar el cumplimiento de esta validación metodológica, el alcance operativo se delimita bajo las siguientes restricciones:

- **Restricciones de tiempo:** El ciclo de desarrollo, pruebas y entrega del MVP está rigurosamente enmarcado en el calendario académico del periodo 2026-1. Todas las fases de ingeniería de software deben culminar con la validación operativa a más tardar el 05 de junio de 2026, dejando las tareas de mantenimiento o estabilidad de producción para fases y fechas posteriores.
- **Restricciones de despliegue:** La aplicación web será diseñada para operar de manera autónoma en un entorno de ejecución local dentro de las estaciones de trabajo del equipo de Ambientes de Aprendizaje en la sede de Bogotá. Queda excluido del alcance el despliegue en la nube (AWS, Google Cloud, Azure) o en servidores de producción institucionales, así como la configuración de dominios web.
- **Restricciones de recursos financieros:** El proyecto se formula y ejecuta con un presupuesto de cero pesos. En consecuencia, la arquitectura de software se basará exclusivamente en el uso de lenguajes y librerías de código abierto (Python, FastAPI, React.js) y consumirá la infraestructura y accesos ya existentes de la API de Canvas LMS. No se contempla la compra de licencias o certificados SSL de pago ni servicios de alojamiento (hosting).
- **Restricciones de capacidad técnica:** Dado que el entregable es un Prototipo Funcional (MVP), se excluyen validaciones avanzadas de ciberseguridad y la integración de sistemas de autenticación del Directorio Activo Institucional del Politécnico Grancolombiano. Adicionalmente, por la complejidad de la estructura de datos en Canvas LMS frente a la ventana de tiempo del proyecto, no se incluirá la parametrización ni automatización de bancos de preguntas. Todas las actividades para el despliegue productivo y aseguramiento de seguridad corresponderán al Departamento de Tecnología de la Institución.

# Marco teórico

La automatización de procesos sobre plataformas de gestión del aprendizaje constituye un campo de convergencia entre múltiples disciplinas de la ingeniería de software. Para fundamentar teóricamente la solución desarrollada en esta práctica empresarial, el presente capítulo organiza la revisión de la literatura en cuatro bloques temáticos interdependientes: los fundamentos de ingeniería de software que rigen el diseño y la documentación del sistema (Sección 2.1); las plataformas de gestión del aprendizaje y sus capacidades de integración programática (Sección 2.2); los principios y estilos arquitectónicos de las interfaces de programación de aplicaciones que hacen posible la comunicación entre el sistema y Canvas LMS (Sección 2.3); y los marcos de gestión de proyectos que estructuran el proceso de construcción iterativa (Sección 2.4). El hilo conductor que une estos cuatro bloques es la trayectoria que va del diagnóstico arquitectónico del script legado hasta la justificación técnica de la herramienta de automatización propuesta.

## Fundamentos de Ingeniería de Software

### Arquitectura de Software

La arquitectura de software surge como disciplina autónoma dentro de la ingeniería de software a partir de la necesidad de gestionar la creciente complejidad de los sistemas en la década de 1990. Perry y Wolf (1992) fueron pioneros en formalizar el concepto al proponer que la arquitectura de un sistema de software puede modelarse como una tupla compuesta por tres elementos: los componentes (elementos de procesamiento, datos y conexión), la forma (las propiedades y relaciones entre esos elementos) y la razón de ser (los principios que justifican las decisiones de diseño). Este modelo seminal estableció que la arquitectura no es el código mismo, sino la estructura que lo organiza y las decisiones que la gobiernan. Dos décadas después, Bass et al. (2012) enriquecen esta perspectiva al argumentar que la arquitectura de software es el conjunto de estructuras necesarias para razonar sobre el sistema, donde las decisiones arquitectónicas son el principal mecanismo para satisfacer los atributos de calidad —entendidos como usabilidad, modificabilidad, rendimiento y disponibilidad— más allá de la corrección funcional del código.

Esta tensión entre la perspectiva estructural de Perry y Wolf (1992) y la perspectiva orientada a atributos de calidad de Bass et al. (2012) adquiere vigencia en la investigación contemporánea. Li et al. (2021), en una revisión sistemática de 72 estudios primarios sobre arquitecturas de software orientadas a servicios, identifican que los seis atributos de calidad más críticos —escalabilidad, rendimiento, disponibilidad, seguridad, mantenibilidad y testeabilidad— no son propiedades del código en abstracto, sino consecuencias directas de las decisiones de descomposición, comunicación y desacoplamiento que se toman en el nivel arquitectónico. Este hallazgo empírico refuerza el argumento de Bass et al. (2012) y es directamente aplicable al diagnóstico del sistema desarrollado: el script original en Python de 2025 satisface funcionalmente su propósito —automatizar el montaje de Aulas Máster en Canvas LMS— pero carece de una estructura arquitectónica que habilite los atributos de calidad requeridos para un uso institucional. En términos de Bass et al. (2012), el script tiene corrección funcional pero no tiene arquitectura en sentido pleno: no es usable por personal no técnico, no es modificable de forma segura y no es escalable a más usuarios simultáneos.

De los estilos arquitectónicos consolidados para sistemas distribuidos, el modelo cliente-servidor es el más pertinente para la solución propuesta. En este estilo, el sistema se divide en dos componentes con responsabilidades claramente diferenciadas: el cliente, encargado de la presentación y la interacción con el usuario, y el servidor, responsable de la lógica de negocio y la comunicación con servicios externos. Como lo señala Fielding (2000) en su tesis doctoral, la separación entre cliente y servidor es uno de los principios constitutivos de la arquitectura web moderna, ya que permite que ambas capas evolucionen de manera independiente sin alterar la interfaz de comunicación entre ellas. Li et al. (2021) corroboran que esta separación es, además, el primer paso necesario para habilitar los demás atributos de calidad en sistemas que integran servicios externos mediante API. Esta independencia es la propiedad arquitectónica central que la intervención documentada busca habilitar: al refactorizar el script en una arquitectura cliente-servidor con una interfaz React y un servidor FastAPI, el equipo de Ambientes de Aprendizaje gana acceso a la herramienta de automatización sin necesidad de comprender ni manipular el código subyacente. Para garantizar la modularidad y la separación de responsabilidades requerida por esta arquitectura, el diseño del backend se estructura bajo el paradigma de Programación Orientada a Objetos, cuyo principio de encapsulamiento permite aislar la lógica de conexión con Canvas, el procesamiento de archivos y la orquestación de operaciones en clases independientes (Bass et al., 2012).

### Refactorización de Código

La refactorización de código es una disciplina de la ingeniería de software que consiste en reestructurar el código fuente de un sistema existente sin alterar su comportamiento externo observable, con el propósito de mejorar su estructura interna, mantenibilidad y escalabilidad. Fowler (2018, p. 45) la define como "una técnica controlada para mejorar el diseño de una base de código existente, cuya esencia es la aplicación de una serie de pequeñas transformaciones que preservan el comportamiento del sistema" \[traducción del autor\]. Esta definición establece dos dimensiones inseparables del concepto: el sistema debe continuar funcionando correctamente después de cada transformación, y cada paso, aunque individualmente pueda parecer trivial, contribuye acumulativamente a una mejora arquitectónica significativa.

La motivación para refactorizar se origina en la identificación de patrones problemáticos que Fowler (2018) denomina code smells o señales de deterioro estructural, entre los cuales se destacan la dependencia rígida de un entorno de ejecución específico, la ausencia de una capa de abstracción entre la lógica de negocio y la presentación, y el acoplamiento excesivo entre módulos. La investigación empírica reciente valida la relevancia práctica de estas categorías: Peruma et al. (2022), en un estudio mixto sobre 67.395 publicaciones reales de Stack Overflow relacionadas con refactorización, identifican que los desarrolladores requieren asistencia principalmente en cinco áreas —optimización de código, herramientas e IDEs, patrones arquitectónicos, pruebas unitarias y bases de datos—, siendo los desafíos de migración a nuevas arquitecturas los de mayor dificultad reportada. En el contexto del sistema desarrollado, el script original en Python exhibe exactamente las señales descritas por Fowler (2018): su ejecución está atada a un IDE, carece de una interfaz de usuario y concentra la lógica de extracción de archivos, comunicación con la API y presentación de resultados en un único módulo sin separación de responsabilidades.

La transición documentada en esta práctica —de un script orientado a consola hacia una arquitectura web cliente-servidor— constituye un proceso de refactorización a gran escala. A diferencia de la refactorización incremental que Fowler (2018) describe para sistemas en producción continua, la magnitud de esta transformación justifica la reconstrucción estructural del sistema, preservando las reglas de negocio del código original como núcleo del nuevo _backend_. Fowler (2018) sostiene que la calidad real del código no reside en que el computador pueda ejecutarlo, sino en que otros programadores puedan comprenderlo, mantenerlo y modificarlo. Es este principio el que distingue el presente trabajo de un desarrollo desde cero: el conocimiento operativo acumulado en el script de 2025 se capitaliza y se eleva a un nivel de abstracción superior, respondiendo directamente a los desafíos de migración arquitectónica que Peruma et al. (2022) identifican como los de mayor demanda en la comunidad de práctica.

### Lenguaje de Modelado Unificado (UML)

El Lenguaje de Modelado Unificado (UML, por sus siglas en inglés) emerge en la década de 1990 como respuesta a la fragmentación del campo del modelado de software orientado a objetos, en el que coexistían múltiples notaciones incompatibles entre sí. Booch et al. (2005) describen UML como un lenguaje de propósito general para el modelado visual de sistemas de software que provee a los equipos de desarrollo un vocabulario compartido para representar tanto la estructura estática como el comportamiento dinámico de los sistemas. Esta perspectiva fundacional es complementada por la especificación formal del Object Management Group (2017), que define UML como un estándar de modelado con semántica precisa, dividido en catorce tipos de diagramas agrupados en dos grandes categorías: estructurales y de comportamiento. Fowler (2004), desde una postura más pragmática, argumenta que el valor real de UML no reside en la exhaustividad de su especificación formal, sino en su capacidad para servir como herramienta de comunicación entre los actores de un proyecto de software, utilizándose de forma selectiva según el contexto. La investigación empírica de Ozkaya y Erata (2020), basada en una encuesta con 109 profesionales de la industria, aporta evidencia de campo a esta postura: los diagramas de clases, secuencia, componentes y despliegue concentran la mayor proporción de uso real en la práctica profesional, mientras que la mayoría de los catorce tipos de la especificación OMG rara vez se emplean. La tensión entre el rigor formal de la especificación OMG y el pragmatismo de Fowler (2004), validada ahora empíricamente por Ozkaya y Erata (2020), revela que UML no es un fin en sí mismo, sino un medio para reducir la ambigüedad en el diseño y facilitar la toma de decisiones arquitectónicas.

En el contexto de la solución propuesta, UML cumple dos funciones complementarias: documentar la arquitectura del sistema para garantizar la mantenibilidad del código a largo plazo, y facilitar la validación de los requerimientos con los usuarios del área de Ambientes de Aprendizaje mediante representaciones visuales accesibles. Los diagramas utilizados fueron seleccionados con base en su pertinencia directa para los artefactos del proyecto y en los hallazgos de Ozkaya y Erata (2020) sobre los tipos de mayor valor práctico.

**Diagramas estructurales.** Los diagramas estructurales de UML describen la organización estática de un sistema, modelando los elementos que lo componen y las relaciones entre ellos con independencia del tiempo. Según la especificación del Object Management Group (2017), esta categoría incluye los diagramas de clases, de objetos, de componentes, de paquetes, de estructura compuesta y de despliegue. Para la herramienta de automatización desarrollada, el diagrama de clases y el de despliegue son los de mayor relevancia, en línea con los resultados de Ozkaya y Erata (2020), que los identifican como los dos diagramas estructurales más frecuentemente empleados en la documentación de arquitecturas de software orientadas a servicios.

Entre ellos, el diagrama de clases ocupa un lugar central. Booch et al. (2005) lo describen como la herramienta primaria para representar el vocabulario del sistema: las clases que lo componen, sus atributos y operaciones, y las relaciones de asociación, herencia y dependencia entre ellas. En la solución propuesta, este diagrama documenta la organización del _backend_ en FastAPI, específicamente la jerarquía de clases que encapsulan la lógica de conexión con la API de Canvas, el procesamiento de archivos y la orquestación de las operaciones de montaje. Fowler (2004) advierte que los diagramas de clases deben usarse como bocetos de diseño y no como especificaciones exhaustivas, una postura que el estudio empírico de Ozkaya y Erata (2020) respalda al documentar que los profesionales reducen deliberadamente el nivel de detalle para preservar su utilidad comunicativa.

Complementariamente, el diagrama de despliegue traslada esa estructura lógica al plano físico (Object Management Group, 2017), representando la distribución de los artefactos de software sobre los nodos de hardware en los que el sistema ejecuta. Esta distinción entre estructura lógica y física es especialmente relevante para la herramienta desarrollada, cuya restricción operativa es la ejecución en un entorno local sin infraestructura en la nube: el diagrama documenta la topología de tres nodos —la estación de trabajo del analista (cliente React), el servidor local de FastAPI (servidor de aplicaciones) y los servidores institucionales de Canvas LMS (servicio externo consumido vía HTTPS)— y hace explícita la dependencia crítica de conectividad entre ellos.

**Diagramas de comportamiento.** Los diagramas de comportamiento de UML representan el funcionamiento dinámico de un sistema, modelando cómo los objetos y componentes interactúan entre sí y cambian de estado a lo largo del tiempo. La especificación del Object Management Group (2017) distingue varios tipos de diagramas de comportamiento; entre ellos, los de casos de uso y los de secuencia son los que Ozkaya y Erata (2020) identifican como los más utilizados en proyectos de desarrollo de software de alcance similar al presente.

El diagrama de casos de uso es el instrumento primario para capturar los requerimientos funcionales desde la perspectiva del usuario. Booch et al. (2005) los describen como contratos de comportamiento entre el sistema y sus actores externos, que definen qué puede hacer el sistema sin especificar cómo lo hace internamente. En la herramienta de automatización, los casos de uso modelan las interacciones entre el analista de Ambientes de Aprendizaje —actor principal— y el sistema, documentando las operaciones centrales: cargar un archivo ZIP de contenidos, iniciar el proceso de montaje, monitorear el progreso y cancelar la ejecución en curso.

El diagrama de secuencia, por su parte, es la herramienta de mayor valor para documentar los flujos de comunicación asíncrona entre el _frontend_ React, el _backend_ FastAPI y la API de Canvas LMS. Según la especificación del Object Management Group (2017), este diagrama muestra explícitamente la dimensión temporal de las interacciones, representando el intercambio de mensajes entre participantes como una secuencia de eventos ordenados en el eje vertical del tiempo. Ozkaya y Erata (2020) señalan que los diagramas de secuencia son particularmente valorados en proyectos que integran servicios externos, pues hacen visibles las dependencias entre componentes y los puntos de fallo potenciales. Para la solución propuesta, el diagrama de secuencia del proceso de montaje —desde que el analista sube el archivo ZIP hasta que recibe la confirmación de despliegue— documenta precisamente estas dependencias y los puntos donde el sistema debe aplicar mecanismos de resiliencia.

## Plataformas de Gestión del Aprendizaje

### Learning Management Systems (LMS)

Las plataformas de gestión del aprendizaje han evolucionado desde herramientas auxiliares de apoyo a la docencia hasta convertirse en infraestructuras organizacionales críticas para las instituciones de educación superior. Turnbull et al. (2022), en un análisis documental de políticas institucionales de LMS en universidades de múltiples países, definen estos sistemas como aplicaciones tecnológicas que integran funciones de administración, distribución de contenidos, comunicación, evaluación y seguimiento del aprendizaje, y cuya gobernanza requiere políticas explícitas de soporte técnico, privacidad y uso institucional. Esta conceptualización —de alcance más sistémico que las definiciones operativas propuestas en literatura más antigua— refleja la complejidad que estos sistemas han adquirido en el contexto post-pandemia, donde la educación virtual ha dejado de ser una modalidad complementaria para convertirse en el eje del modelo educativo de muchas instituciones. Simon et al. (2025), en un estudio empírico con 82 docentes y estudiantes de educación superior, documentan precisamente esta transición: el LMS ha migrado de un rol de "repositorio suplementario" a ser la plataforma central de la experiencia educativa, lo que ha amplificado su impacto institucional y ha hecho visibles brechas de usabilidad y capacitación antes ignoradas.

La dimensión administrativa del LMS es la que mayor relevancia tiene para el presente proyecto, y es también la que la literatura más reciente identifica como el área con más oportunidades de mejora. Sulaiman (2024), a partir de una revisión sistemática PRISMA de 34 estudios sobre factores de adopción del LMS en educación superior, identifica que las condiciones facilitadoras —infraestructura técnica, soporte institucional y capacitación del personal administrativo— son el tercer predictor más fuerte del uso efectivo de la plataforma, después de la utilidad percibida y la facilidad de uso. En instituciones de educación virtual a gran escala como el Politécnico Grancolombiano, con más de 55.000 estudiantes activos en modalidad virtual, estas condiciones facilitadoras adquieren una dimensión crítica: cuando el proceso de configuración de las aulas virtuales depende del trabajo manual de un equipo reducido de analistas y consume un promedio de 240 minutos por asignatura, la ausencia de herramientas de automatización se convierte en la principal condición que inhibe la capacidad operativa institucional. Es en este marco donde la automatización documentada en esta práctica empresarial encuentra su justificación en la literatura contemporánea sobre LMS.

Turnbull et al. (2022) advierten, adicionalmente, que las políticas de LMS en educación superior comparten una brecha estructural recurrente: las instituciones definen con mayor detalle las normas de uso pedagógico de la plataforma que los procedimientos de administración y configuración técnica del entorno de aprendizaje. Esta brecha refuerza la pertinencia de la intervención propuesta: en ausencia de procesos administrativos automatizados, la calidad y consistencia del entorno que el estudiante encontrará al inicio del período académico queda supeditada a la disponibilidad y capacidad manual del equipo técnico.

### Canvas LMS

Canvas LMS es una plataforma de gestión del aprendizaje desarrollada por Instructure, cuya adopción en la educación superior ha crecido sostenidamente en la última década como alternativa a soluciones más rígidas como Blackboard o como complemento más robusto que plataformas _open-source_ como Moodle. Mpungose y Khoza (2022), en un estudio cualitativo comparativo con 31 participantes en contextos de educación superior en Sudáfrica y Estados Unidos, documentan las principales dimensiones en las que Canvas y Moodle difieren desde la perspectiva de sus usuarios: mientras Moodle ofrece mayor flexibilidad de personalización al ser _open-source_, Canvas se distingue por una experiencia de usuario más consistente, una arquitectura nativa en la nube y una curva de aprendizaje más reducida para instituciones con equipos técnicos de soporte limitados. Ambas plataformas comparten funcionalidades esenciales —cuestionarios, foros, anuncios, entrega de archivos y calificaciones—, pero difieren en los costos de mantenimiento y en el modelo de actualización. Turnbull et al. (2021), al comparar la implementación de LMS en Australia y China, identifican que la elección entre Canvas, Moodle y Blackboard responde a siete factores críticos: selección de la plataforma, diversidad de despliegue, impacto cultural, expectativas de los usuarios, obstáculos administrativos, costos de soporte y alineación con la estrategia institucional. En el caso del Politécnico Grancolombiano, la elección de Canvas como plataforma institucional responde a su modelo _cloud-based_ con soporte técnico centralizado, que reduce la carga operativa del departamento de tecnología y concentra la administración pedagógica en el equipo de Ambientes de Aprendizaje.

El atributo técnico de Canvas LMS que hace viable el presente proyecto no es su interfaz de usuario ni su modelo pedagógico, sino su arquitectura de interoperabilidad programática. A diferencia de plataformas con diseños más cerrados, Canvas expone la totalidad de sus recursos —cursos, módulos, páginas, archivos, actividades evaluativas, usuarios y matrículas— como endpoints de una API REST completamente documentada, lo que permite que un sistema externo replique programáticamente cualquier operación que un administrador humano realizaría manualmente (Instructure, Inc., 2026). Algamdi y Ludi (2025), en un análisis empírico de los factores de usabilidad de Canvas, señalan que esta capacidad de extensión programática es precisamente lo que distingue a Canvas de otras plataformas en contextos universitarios con alta demanda operativa: permite que las instituciones desarrollen integraciones personalizadas para sus flujos administrativos sin depender de actualizaciones del fabricante. En el contexto institucional del Politécnico Grancolombiano, donde el volumen de Aulas Máster que deben configurarse por período académico supera la capacidad manual del equipo de Ambientes de Aprendizaje, esta característica arquitectónica de Canvas es el fundamento técnico sobre el que descansa toda la hipótesis de optimización de la herramienta desarrollada.

### Canvas REST API

Canvas LMS expone una interfaz de programación de aplicaciones de tipo REST que permite a sistemas externos acceder, crear, modificar y eliminar datos de la plataforma de manera programática, sin necesidad de interacción directa con su interfaz gráfica. De acuerdo con la documentación oficial, Canvas "incluye una API REST para acceder y modificar datos de forma externa a la aplicación principal, utilizable desde programas y scripts propios" (Instructure, Inc., 2026). Toda la comunicación ocurre sobre HTTPS, las respuestas se estructuran en formato JSON y la autenticación se gestiona mediante el protocolo OAuth2 (RFC-6749), que permite a aplicaciones de terceros operar con los permisos de un usuario autenticado sin acceder directamente a sus credenciales (Instructure, Inc., 2026). Este modelo de seguridad, sumado a la estandarización de recursos que sigue los principios arquitectónicos descritos por Fielding (2000), garantiza la interoperabilidad y la independencia entre el sistema de automatización y los servidores institucionales de Canvas.

La relevancia académica de este tipo de integración trasciende el caso específico de Canvas. Mowla y Kolekar (2020) proponen una arquitectura orientada a servicios basada en APIs REST para el desarrollo e integración de servicios de e-learning en múltiples LMS, demostrando que los servicios REST permiten reducir significativamente los costos y tiempos de desarrollo al encapsular las reglas de negocio de cada operación —creación de cursos, gestión de usuarios, entrega de contenidos— en módulos independientes y reutilizables. Esta arquitectura de servicios desacoplados es el patrón que subyace al diseño del backend FastAPI de la herramienta desarrollada: cada operación sobre Canvas —creación de curso, subida de archivo, vinculación de PDF— se implementa como un servicio independiente que encapsula la lógica de comunicación con la API y puede ser invocado desde la interfaz React sin conocimiento de los detalles de implementación.

Un aspecto técnico que impacta directamente el diseño del sistema es la política de control de tasa de peticiones (_rate limiting_) de la plataforma. La documentación de Instructure (2026) establece que el acceso a la API está sujeto a restricciones de volumen de solicitudes por unidad de tiempo, lo que obliga a los sistemas que la consumen a implementar mecanismos de espera, reintentos y procesamiento asíncrono. Esta restricción, señalada también por Mowla y Kolekar (2020) como uno de los principales desafíos técnicos en integraciones REST con LMS institucionales, explica parcialmente el tiempo de seis minutos en la etapa de subida de archivos documentado en la Tabla 2, y justifica el diseño del motor de reintentos automáticos incluido como requerimiento HU-12 en el Product Backlog.

## Interfaces de Programación de Aplicaciones

### Concepto y estilos arquitectónicos

Las interfaces de programación de aplicaciones (API, del inglés Application Programming Interface) son mecanismos de software que definen los términos bajo los cuales dos sistemas pueden comunicarse entre sí, intercambiando datos y servicios sin necesidad de exponer su implementación interna. Fielding (2000) sitúa este concepto dentro de la teoría más amplia de los sistemas distribuidos basados en red, argumentando que la definición de una interfaz estable y abstracta entre componentes es el mecanismo fundamental mediante el cual la arquitectura de software habilita la escalabilidad y la evolución independiente de las partes de un sistema. Desde esta perspectiva, la existencia de la Canvas REST API no es simplemente una característica de la plataforma, sino la condición arquitectónica que hace posible que sistemas externos como el desarrollado en esta práctica empresarial interactúen con ella de manera predecible y verificable.

En el desarrollo de software contemporáneo coexisten diferentes estilos arquitectónicos para el diseño de APIs, cada uno con características y compromisos distintos. SOAP (Simple Object Access Protocol) fue durante la primera década del siglo XXI el estándar dominante en entornos empresariales, basado en mensajería XML y con un modelo de contrato estricto definido mediante WSDL; su fortaleza radica en la formalidad del contrato y el soporte para transacciones distribuidas, pero su rigidez y verbosidad han limitado su adopción en contextos donde la agilidad y la simplicidad son prioritarias. REST (Representational State Transfer), propuesto por Fielding (2000) como estilo arquitectónico en su tesis doctoral, se consolidó como la alternativa predominante para el desarrollo web gracias a su adherencia a los principios del propio protocolo HTTP. En años más recientes, GraphQL (GraphQL Foundation, 2021) —una especificación de consulta de datos publicada originalmente por Meta— ha emergido como alternativa para escenarios donde el cliente necesita controlar con precisión qué datos recupera del servidor, reduciendo el problema de la sobrecarga de datos (_over-fetching_) que puede ocurrir en APIs REST. Brito y Valente (2020), en un experimento controlado con 22 participantes que implementaron ocho consultas equivalentes usando REST y GraphQL sobre la API de GitHub, encontraron que GraphQL demanda menos esfuerzo en escenarios de datos complejos (mediana de 6 minutos frente a 9 minutos en REST), aunque la diferencia disminuye significativamente cuando los endpoints REST están bien documentados y responden a contratos estables. Esta evidencia empírica tiene implicaciones directas para el presente caso: la elección de REST sobre GraphQL no solo está determinada exógenamente por la propia Canvas LMS, sino que se justifica técnicamente porque la Canvas API expone un contrato REST maduro y completamente documentado que elimina las ventajas de GraphQL en consultas ad hoc.

### Arquitectura REST

REST (Representational State Transfer) no es un protocolo ni una especificación formal, sino un estilo arquitectónico derivado de la observación de los principios que hicieron de la World Wide Web un sistema distribuido de extraordinaria escala y resiliencia. Fielding (2000) desarrolla REST como parte de su análisis del diseño de arquitecturas para sistemas de información distribuidos basados en red, argumentando que la web pudo escalar a nivel global precisamente porque su arquitectura respeta un conjunto de restricciones que separan las responsabilidades de cliente y servidor, hacen _stateless_ la comunicación y permiten el almacenamiento en caché de las representaciones de los recursos. En palabras del propio Fielding:

REST es un conjunto coordinado de restricciones arquitectónicas que busca minimizar la latencia y la comunicación en red, al mismo tiempo que maximiza la independencia y la escalabilidad de las implementaciones de los componentes. Este enfoque permite el almacenamiento en caché de las interacciones, la reutilización de recursos y la sustitución dinámica de componentes en sistemas distribuidos de gran escala. (Fielding, 2000, p. 76)

Las seis restricciones que Fielding (2000) identifica como constitutivas del estilo REST — interfaz uniforme, separación cliente-servidor, ausencia de estado (_statelessness_), caché, sistema en capas y código bajo demanda (opcional) — tienen implicaciones prácticas directas para el diseño de sistemas que consumen APIs REST. La restricción de _statelessness_, por ejemplo, implica que cada solicitud al servidor debe contener toda la información necesaria para que el servidor la comprenda y procese; el servidor no almacena estado de sesión del cliente entre una solicitud y la siguiente. Esta característica simplifica la escalabilidad del servidor pero impone al cliente la responsabilidad de gestionar el contexto de las interacciones. En la herramienta de automatización, esto se traduce en que cada llamada a la API de Canvas incluye el token de autenticación OAuth2 y los parámetros completos de la operación, sin depender de una sesión preexistente en el servidor. La restricción de sistema en capas —igualmente constitutiva del estilo REST— establece que cada componente solo puede interactuar con la capa inmediatamente adyacente, sin visibilidad sobre el resto del sistema (Fielding, 2000). Esta restricción describe con precisión la arquitectura del presente proyecto: la interfaz React se comunica únicamente con FastAPI, que a su vez se comunica con Canvas, garantizando que los cambios en cualquier capa no afecten directamente a las demás.

Fielding (2000) aclara que REST no constituye una arquitectura de sistema completa sino un conjunto de restricciones que, cuando se aplican consistentemente, generan propiedades emergentes deseables: "REST es un conjunto de restricciones que, cuando se aplican correctamente, generan propiedades deseables para aplicaciones descentralizadas basadas en red" \[traducción del autor\] (p. 78). Esta precisión es relevante porque explica por qué no todas las APIs que se autodenominan REST cumplen en igual medida con sus principios: el nivel de adherencia a las restricciones REST determina el nivel de madurez de la API y, con ello, la facilidad con que los sistemas externos pueden integrarla. El experimento controlado de Brito y Valente (2020) confirma empíricamente este punto: la facilidad de integración con una API REST es función directa de la calidad y completitud de su documentación, lo que convierte a la Canvas API en un caso especialmente favorable dado que Instructure (2026) publica y mantiene su especificación de forma exhaustiva y actualizada.

## Gestión de Proyectos de Software

### Modelo Predictivo y PMBOK

La gestión de proyectos es la disciplina que organiza, planifica y controla los recursos —humanos, técnicos, temporales y financieros— necesarios para alcanzar un conjunto de objetivos dentro de un marco de restricciones definidas. El Project Management Institute (PMI, 2021), a través de la séptima edición de su Guía del Project Management Body of Knowledge (PMBOK®), representa una evolución significativa en la concepción de esta disciplina: en lugar de estructurarse en torno a diez áreas de conocimiento y cinco grupos de procesos —como en ediciones anteriores—, la séptima edición articula doce principios de dirección de proyectos y ocho dominios de desempeño que reconocen explícitamente la diversidad de contextos en los que se gestiona trabajo. Este cambio refleja el reconocimiento del PMI (2021) de que los proyectos no son todos iguales: algunos se benefician de la planificación predictiva detallada, mientras que otros requieren enfoques adaptativos que permitan ajustar el alcance y las prioridades en función de lo que el equipo aprende durante la ejecución.

Esta distinción entre gestión predictiva y adaptativa es particularmente relevante en el desarrollo de sistemas de software que integran servicios externos. La industria del software identificó tempranamente que las condiciones que hacen efectivo el enfoque predictivo —requisitos estables, incertidumbre técnica baja y alcance predefinido— rara vez se presentan en proyectos de integración con APIs de terceros. En este contexto, el PMI (2021) reconoce que los proyectos de software de alta variabilidad son candidatos naturales para enfoques adaptativos que privilegien la entrega de valor en ciclos cortos sobre la adherencia a un plan inicial exhaustivo. Esta tensión no representa una contradicción de los principios de gestión de proyectos, sino su evolución hacia el reconocimiento de que diferentes categorías de proyectos requieren diferentes estrategias.

En el caso de la herramienta desarrollada, la naturaleza de la integración con la Canvas API —cuyos comportamientos, restricciones de tasa y respuestas ante casos límite no pueden anticiparse completamente sin ejecución real— hace que la gestión predictiva pura resulte inadecuada. Un plan de proyecto que defina con precisión cada tarea de desarrollo antes de comenzar a interactuar con los servidores institucionales de Canvas asumiría un grado de certeza técnica que la realidad operativa no garantiza. Por esta razón, y en coherencia con los principios de la séptima edición del PMBOK® (PMI, 2021) para proyectos de alta incertidumbre, la solución adoptó un enfoque adaptativo materializado en el marco de trabajo Scrum, cuya estructura iterativa e incremental permite validar cada bloque de integración antes de comprometer el diseño de los bloques siguientes.

### Marco de Trabajo Scrum

Scrum es definido por sus co-creadores como "un marco de trabajo ligero que ayuda a personas, equipos y organizaciones a generar valor a través de soluciones adaptativas para problemas complejos" (Schwaber y Sutherland, 2020, p. 3). Esta definición establece dos características que lo distinguen de una metodología convencional: su deliberada ligereza —Scrum no prescribe técnicas específicas sino que provee un contenedor estructural— y su orientación hacia la complejidad, entendida como aquella categoría de problemas donde el conocimiento completo de los requisitos no puede anticiparse en su totalidad antes de iniciar la ejecución. A diferencia del ciclo de vida en cascada, donde la fase de diseño debe completarse antes del desarrollo, Scrum parte del reconocimiento de que el conocimiento emerge durante la construcción misma del sistema.

La base teórica de Scrum descansa en el empirismo y el pensamiento Lean. El empirismo establece que el conocimiento proviene de la experiencia y que las decisiones deben fundamentarse en la observación directa de los resultados; el pensamiento Lean orienta hacia la eliminación del desperdicio y el enfoque en lo esencial. De estos principios se derivan los tres pilares del marco de trabajo: la transparencia (el proceso y el trabajo deben ser visibles para quienes los ejecutan y para quienes los reciben), la inspección (los artefactos y el avance hacia los objetivos deben examinarse frecuentemente para detectar desviaciones) y la adaptación (cuando algún aspecto del proceso se desvía fuera de los límites aceptables, deben realizarse ajustes con la mayor prontitud posible) (Schwaber y Sutherland, 2020, p. 3). Esta tríada conecta Scrum con el enfoque de investigación cuantitativa preexperimental adoptado en esta práctica: en ambos casos, la hipótesis se valida dentro de una estructura que demanda medir, observar y ajustar en ciclos cortos.

El trabajo en Scrum se organiza en iteraciones de duración fija denominadas Sprints. Schwaber y Sutherland (2020, p. 7) describen el Sprint como "el contenedor de todos los demás eventos", al interior del cual se ejecutan cuatro ceremonias específicas: el Sprint Planning (planificación del trabajo de la iteración), el Daily Scrum (sincronización diaria), el Sprint Review (inspección del incremento con las partes interesadas) y el Sprint Retrospective (reflexión del equipo sobre su propio proceso). La gestión del trabajo pendiente se realiza a través del Product Backlog, un inventario vivo y priorizado de todos los requisitos del sistema cuya ordenación refleja el valor operativo que cada elemento aporta al usuario final.

La investigación empírica reciente aporta evidencia sustancial sobre la efectividad de Scrum y las condiciones que la favorecen. Verwijs y Russo (2023), en un estudio de siete años de duración con datos de cerca de 2.000 equipos Scrum y 5.000 desarrolladores, identificaron un modelo de cinco factores que predicen la efectividad del equipo: capacidad de respuesta, foco en los interesados, mejora continua, autonomía del equipo y apoyo de la dirección, con un ajuste del modelo confirmado mediante modelado de ecuaciones estructurales (CFI=0,959; RMSEA=0,038). Por su parte, Hron y Obwegeser (2022), en una revisión sistemática de 925 estudios sobre adaptaciones de Scrum, documentan que el marco es ampliamente modificado para ajustarse a nueve categorías de contextos no estándar, incluidos equipos pequeños, proyectos de desarrollo individual y entornos con alta variabilidad técnica. Esta evidencia valida la aplicabilidad de Scrum al contexto de la presente práctica, donde la restricción de desarrollo individual y la incertidumbre técnica asociada a la integración con la Canvas API constituyen precisamente el tipo de contexto para el que Hron y Obwegeser (2022) documentan mayor frecuencia de adaptación. La adopción de Scrum para el desarrollo del aplicativo responde, en última instancia, a la imposibilidad de anticipar con exactitud cómo responderá la Canvas API ante cada tipo de solicitud —subida de archivos de gran tamaño, creación masiva de páginas, vinculación de PDFs— sin ejecutar pruebas reales contra los servidores institucionales.

### Metodología SMART

Aunque el marco SMART fue originalmente formulado en el contexto de la gestión organizacional, su adopción en la planificación de proyectos de ingeniería de software se fundamenta en su capacidad de traducir necesidades operativas abstractas en metas cuantificables y temporalmente acotadas que puedan ser verificadas mediante métricas de sistema (Doran, 1981).

La definición de objetivos verificables es una condición necesaria para cualquier investigación de alcance cuantitativo. Doran (1981) propone el marco SMART —acrónimo de Specific, Measurable, Achievable, Relevant y Time-bound— como criterio estructurado para evaluar si los objetivos de gestión son suficientemente concretos para orientar la acción y permitir la verificación posterior de su cumplimiento. Originalmente formulado en el contexto de la gestión organizacional, el marco SMART ha sido ampliamente adoptado en la planificación de proyectos de ingeniería de software por su capacidad de operacionalizar metas que de otro modo permanecerían ambiguas. Los objetivos de la presente práctica empresarial fueron formulados y validados explícitamente bajo este criterio: son específicos al enfocarse exclusivamente en la automatización del montaje de Aulas Máster vía API, descartando otros procesos académicos; medibles mediante la comprobación matemática de la reducción del tiempo operativo de 240 a 25 minutos por asignatura; alcanzables al acotar el desarrollo a un entorno de ejecución local con tecnologías de código abierto; relevantes al solucionar directamente el cuello de botella que restringe la capacidad de respuesta del equipo de Ambientes de Aprendizaje; y con tiempo definido, al estar enmarcados en el calendario de la Práctica Empresarial con fecha límite de junio de 2026.

### Cierre del Marco Teórico

Los cuatro bloques de esta revisión literaria no son compartimentos independientes sino eslabones de un argumento acumulativo. Los fundamentos de ingeniería de software —arquitectura orientada a atributos de calidad (Bass et al., 2012; Li et al., 2021), refactorización disciplinada (Fowler, 2018; Peruma et al., 2022) y modelado UML seleccionado con criterio empírico (Ozkaya y Erata, 2020)— proveen el vocabulario técnico para diagnosticar el script legado y diseñar su transformación. La revisión sobre plataformas de gestión del aprendizaje —que documenta la transición del LMS hacia infraestructura institucional crítica (Turnbull et al., 2022; Simon et al., 2025; Sulaiman, 2024) y la ventaja diferencial de la arquitectura API-first de Canvas (Mpungose y Khoza, 2022; Algamdi y Ludi, 2025)— justifica por qué la automatización es no solo posible sino necesaria en el contexto del Politécnico Grancolombiano. El análisis de las APIs REST —desde la formulación seminal de Fielding (2000) hasta la comparación empírica con alternativas como GraphQL (Brito y Valente, 2020) y los patrones de integración con LMS (Mowla y Kolekar, 2020)— determina el mecanismo técnico mediante el cual la automatización opera. Finalmente, los marcos de gestión de proyectos —desde el reconocimiento del PMI (2021) de los enfoques adaptativos hasta la evidencia empírica sobre la efectividad de Scrum (Verwijs y Russo, 2023; Hron y Obwegeser, 2022)— fundamentan el método con el que se construyó la solución. En conjunto, estos cuatro bloques configuran el andamiaje teórico que sustenta la hipótesis de optimización operativa del 89,58% que será sometida a comprobación en las fases de construcción y validación del proyecto.

# 3\. Método

El presente capítulo define la estructura procedimental, la secuencia lógica y el conjunto de mecanismos empíricos que permitieron alcanzar los objetivos trazados en la Práctica Empresarial. Mientras que los objetivos establecen los hitos funcionales a cumplir, este apartado metodológico define cómo se estructuró el proceso iterativo y de desarrollo para garantizar que los resultados obtenidos sean medibles, verificables y abiertos a retroalimentación constante.

## Tipo de estudio e hipótesis de optimización

Para el desarrollo de esta Práctica Empresarial se adoptó un enfoque de **investigación cuantitativa de alcance preexperimental,** fundamentado en la medición técnica y operativa de un proceso antes y después de una intervención tecnológica. El método cuantitativo se seleccionó por su rigor en la recolección de datos medibles (tiempos de ejecución) y su capacidad para contrastar realidades operativas de manera objetiva.

El estudio se rige bajo la siguiente hipótesis de trabajo:

_La implementación de un prototipo funcional de aplicación web estructurado sobre la API de Canvas LMS, centralizará y automatizará las tareas operativas de configuración académica, reduciendo el tiempo de montaje de un Aula Máster de 240 minutos (proceso manual) a un máximo de 25 minutos (proceso automatizado), optimizando así la capacidad de respuesta del equipo en un 89,58%._

## Fases del proceso de desarrollo tecnológico

Para alcanzar los objetivos y comprobar la hipótesis planteada, se adaptaron las fases tradicionales del método científico cuantitativo a la realidad de la Ingeniería de Software. Como se ilustra en la Figura 1, el método no se plantea como un modelo en cascada estrictamente lineal, sino como una secuencia lógica abierta a la retroalimentación, donde la construcción empírica del software sirve como mecanismo para la validación de la hipótesis.

La secuencia lógica del proyecto se divide en las siguientes etapas fundamentales, cada una con sus respectivas actividades operativas:

- **Etapa 1: Planteamiento y Medición Empírica (Punto de partida):** Corresponde a la identificación de la limitante operativa y la medición cuantitativa del estado actual (línea base de 240 minutos por aula).
    - **Actividades:** Observación directa del proceso manual, cronometría de los tiempos de montaje en Canvas LMS y consolidación de la métrica base.
- **Etapa 2: Diseño de la Solución (Planificación):** Contempla la estructuración de la arquitectura de software, la revisión de la literatura tecnológica y la traducción de las necesidades operativas en un Product Backlog priorizado.
    - **Actividades:** Selección del stack tecnológico (FastAPI, React.js), diseño de diagramas UML y estimación de Historias de Usuario.
- **Etapa 3: Construcción Iterativa (Bucle de Retroalimentación):** Representa el núcleo del desarrollo empírico. A través de iteraciones cortas, se programa y compila el aplicativo web. Esta fase es cíclica, permitiendo que cada incremento de código sea probado y ajustado (retroalimentación) antes de pasar a la siguiente iteración.
    - **Actividades:** Ejecución de Sprints, desarrollo de la API y la interfaz, y pruebas locales de código para cada incremento funcional.
- **Etapa 4: Pruebas y Recolección de Datos:** Consiste en la ejecución de simulaciones de carga masiva utilizando el aplicativo web terminado en un entorno local, cronometrando los tiempos de respuesta del sistema.
    - **Actividades:** Simulación de montaje masivo con archivos .ZIP reales, registro de tiempos del proceso automatizado y validación de despliegue en Canvas.
- **Etapa 5: Análisis y Reporte de Resultados:** Corresponde a la contrastación final de los datos recolectados (tiempos automatizados) frente a la línea base (tiempos manuales), para aceptar o refutar la hipótesis de optimización.
    - Actividades: Tabulación comparativa de métricas, análisis del impacto en la capacidad operativa y redacción de conclusiones.

**Figura 1**  
_Fases del modelo metodológico híbrido para el desarrollo tecnológico._

_Nota_. El diagrama ilustra la adaptación del método de investigación cuantitativo al ciclo de vida de la Ingeniería de Software. A diferencia de un modelo lineal en cascada, la Fase 3 se estructura como un bucle iterativo que garantiza la retroalimentación empírica y la mejora continua de la herramienta de automatización antes de la fase de recolección de datos. Elaboración propia.

## Población, muestra y recolección de datos

En coherencia con el enfoque cuantitativo, la recolección empírica de datos se centró en la métrica principal de la hipótesis: el tiempo de ejecución.

- **Población objetivo:** El universo de estudio corresponde a la totalidad de las asignaturas (Aulas Máster) que requieren montaje y configuración en la plataforma Canvas LMS durante un periodo académico regular en el Politécnico Grancolombiano.
- **Muestra:** Se seleccionó una muestra no probabilística por conveniencia, conformada por escenarios de simulación de Aulas Máster que representan las tipologías de cursos más demandadas por la institución.
- **Mecanismo de recolección:** Se utilizó la técnica de cronometría y observación estructurada. Los datos de la línea base (proceso manual) se obtuvieron a través de mesas de trabajo previas con los analistas. Los datos de comprobación (proceso automatizado) se extraerán mediante la ejecución de la aplicación web en un entorno local, registrando el tiempo transcurrido desde el inicio de la carga del paquete ZIP hasta el mensaje de éxito del sistema.

## Diseño y marco de trabajo ágil

Para el desarrollo de la presente Práctica Empresarial, se adopta un enfoque metodológico ágil fundamentado en el marco de trabajo Scrum, adaptado para un entorno de desarrollo individual. Esta adaptación de Scrum se justifica por las condiciones del proyecto, el cual exige la construcción de un Prototipo Funcional (MVP) mediante entregas iterativas e incrementales. Scrum permite gestionar la complejidad técnica de la integración entre la API de Canvas LMS y la aplicación web, facilitando la validación temprana y continua con los usuarios finales.

Bajo este marco, los requerimientos se gestionarán a través de un Product Backlog priorizado, y el desarrollo se dividirá en ciclos de trabajos cortos denominados Sprints. Esta estructura garantiza la flexibilidad necesaria para adaptar la interfaz gráfica y la arquitectura del sistema a las necesidades operativas reales, asegurando que el producto final cumpla con la métrica de eficiencia establecida (25 minutos por montaje).

## Descripción de actividades

Las actividades del proyecto se estructuran con base en las ceremonias del marco de trabajo Scrum, mediante la entrega de **incrementos funcionales de valor** al finalizar cada iteración. El desarrollo se divide en una fase de preparación (Sprint 0), cuatro iteraciones principales donde se integra _frontend_, _backend_ y validación continua, y una fase de cierre documental:

- **Fase de Inicio y Preparación (Sprint 0)**
- Análisis del flujo manual de montaje de aulas y revisión analítica del código legado (script en Python de 2025).
- Configuración del entorno de desarrollo local y del repositorio de control de versiones en GitHub.
- Configuración del entorno en Jira Software para la gestión ágil del proyecto, estimaciones y control del Product Backlog.
- **Sprint 1: Incremento de Modelado y Prototipo Navegable**
- Sprint Planning enfocado en la estructuración base del proyecto.
- Modelado de requerimientos, diseño de la arquitectura del software y wireframes.
- Desarrollo integral (Full-Stack): Construcción de la interfaz web (React) para la selección de plantillas y captura de metadatos, acoplada al motor local de validación y desempaquetado de archivos ZIP (FastAPI).
- Sprint Review y pruebas de integración local para certificar el primer prototipo funcional.
- **Sprint 2: Incremento de la Integración con API Canvas**
- Sprint Planning orientado a la comunicación con sistemas externos.
- Desarrollo de endpoints para la creación automatizada de cursos, subida masiva de archivos a Canvas y vinculación de PDFs a Páginas, Tareas y Foros.
- Implementación del panel visual de confirmación de despliegue y estado de conexión en la interfaz.
- Sprint Review validando la correcta inyección de recursos en los servidores de prueba institucionales.
- **Sprint 3: Implementación de Automatización y Monitoreo**
- Sprint Planning enfocado en la automatización de contenidos textuales y experiencia de usuario.
- Desarrollo del motor de procesamiento de paquetes interactivos (Articulate Storyline) y el Guion en Excel para la inyección de textos y multimedia.
- Implementación de la Barra de Progreso en tiempo real y el panel de Cancelación de ejecución.
- Sprint Review y pruebas de caja blanca para verificar el flujo completo de montaje de un Aula Máster.
- **Sprint 4: Validación, Pruebas y Resiliencia**
- Sprint Planning orientado a la calidad del software (QA) y el manejo de fallos.
- Desarrollo de la gestión automática de errores de red (reintentos de subida) y programación del motor de reportes históricos en Excel.
- Ejecución de pruebas de carga masiva y simulación de escenarios reales de montaje con los usuarios finales (Analistas).
- Ajustes de código (refactoring) y certificación analítica del cumplimiento de la métrica de 25 minutos (optimización del 89,58%).
- Sprint Retrospective para evaluar el ciclo de vida del desarrollo.
- **Cierre**
- Consolidación de los resultados métricos de las pruebas operativas.
- Redacción y estructuración final del documento de Práctica Empresarial para la sustentación y aprobación de la Opción de Grado.

## Cronograma de actividades

La planificación del proyecto se ha estructurado para ejecutarse entre el 02 de febrero y el 25 de mayo de 2026. Al utilizar Scrum como marco de trabajo ágil, el ciclo de vida del proyecto se divide en una fase de preparación inicial (Sprint 0), seguida de iteraciones cortas (Sprints), enfocadas en el desarrollo técnico y la validación de incrementos funcionales. Para garantizar la trazabilidad del proyecto bajo estándares de la industria del software, la gestión del Product Backlog, las estimaciones de esfuerzo (mediante Story Points) y el seguimiento de cada iteración se administran a través de la herramienta **Jira Software**. Esta plataforma permite mantener un control estricto sobre el cumplimiento de los tiempos, la velocidad de desarrollo y los entregables generados en cada fase.

A continuación, se detalla la programación de las iteraciones en la Tabla 3:

**Tabla 3**  
_Cronograma de Sprints e Incrementos_

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| **Fase / Iteración** | **Descripción y Entregable (Incremento)** | **Inicio** | **Fin** | **Entregable** |
| Fase inicial | Contextualización del proyecto, revisión de código desarrollado (script en Python de 2025) y configuración del entorno de desarrollo local. | 2/02/2026 | 27/02/2026 | &nbsp; |
| Sprint 1 (Modelado y Prototipo Navegable) | Levantamiento de requerimientos, diseño de arquitectura web y wireframes | 2/03/2026 | 31/03/2026 | Product Backlog en Jira, Documento de Arquitectura y Prototipo Navegable |
| Sprint 2 (Integración con API Canvas) | Desarrollo de API REST (FastAPI) encapsulando lógica de conexión con Canvas y extracción de ZIP. | 1/04/2026 | 17/04/2026 | Incremento de código _backend_ |
| Sprint 3 (Automatización y Monitoreo) | Construcción de interfaz gráfica (React) y acoplamiento asíncrono con los endpoints del _backend_. | 20/04/2026 | 8/05/2026 | Prototipo MVP integrado y funcional |
| Sprint 4 (Validación, Pruebas y Resiliencia) | Pruebas de carga, simulación de escenarios de usuario y estabilización. | 11/05/2026 | 29/05/2026 | Informe de validación operativa |
| Cierre y Sustentación | Consolidación de resultados, redacción final del documento final y sustentación de la Práctica Empresarial. | 30/05/2026 | 10/06/2026 | Documento final de Práctica |

_Nota: Tabla elaborada por el autor del documento._

## Entregables

Para garantizar la alineación con la metodología de desarrollo iterativo e incremental, los resultados del proyecto no se presentarán como una única entrega final, sino que se liberarán como **incrementos funcionales y documentales a la terminación de cada Sprint**, estructurados de la siguiente manera:

1.  **Entregable del Sprint 1 (Incremento de Modelado y Prototipo Navegable):** Documento técnico con el Product Backlog, diagramas de arquitectura y el primer incremento funcional de la interfaz gráfica.
2.  **Entregable del Sprint 2 (Incremento de Integración con API Canvas):** Incremento de código funcional enfocado en la comunicación con la API de Canvas LMS, capaz de crear cursos y subir archivos empaquetados.
3.  **Entregable del Sprint 3 (Incremento de Automatización y Monitoreo):** Prototipo Funcional (MVP) completamente integrado, incluyendo la lectura de guiones en Excel y el monitoreo visual del proceso operativo.
4.  **Entregable de Sprint 4 (Validación, Pruebas y Resiliencia):** Informe de Pruebas de Usuario que certifica la eficiencia en los tiempos de montaje, acompañado del Documento Final de Práctica Empresarial.

# Desarrollo e Implementación de la Solución Tecnológica

## Levantamiento de requerimientos

El levantamiento de requerimientos constituye la fase exploratoria y definición del proyecto, cuyo propósito es comprender a cabalidad las necesidades operativas del área y traducirlas en especificaciones técnicas para el desarrollo del software. Bajo el marco de trabajo Scrum, este proceso se aleja de la recolección tradicional de documentos extensos para enfocarse en la colaboración directa y continua con los actores del proceso (Stakeholders).

Para el desarrollo del presente aplicativo web, el levantamiento de requerimientos se ejecutó mediante la integración de las siguientes técnicas:

1.  **Mesas de trabajo:** Se realizaron sesiones colaborativas con la Líder de Ambientes de Aprendizaje y con el equipo de analistas, identificando los “puntos de dolor” del montaje manual y las expectativas frente a la nueva interfaz.
2.  **Observación directa:** Se acompañó el proceso de montaje manual de un Aula Máster en Canvas LMS, lo que permitió cuantificar la línea base de tiempo operativo (240 minutos) y comprender la secuencia lógica de carpetas y módulos que el sistema debía replicar.
3.  **Análisis del código existente:** Se analizó detalladamente el script desarrollado en Python en el año 2025 para extraer las reglas de negocio existentes, identificar sus limitaciones y determinar las dependencias necesarias para refactorizarlo como el núcleo del nuevo _backend_ (API REST).

A partir de este ejercicio, las necesidades del proyecto se categorizaron en dos frentes que sirvieron como insumo directo para la construcción del Product Backlog:

- **Requerimientos funcionales:** Centrados en la capacidad del sistema para procesar archivos comprimidos (.ZIP), normalizar la denominación estructural, leer matrices de datos (Guion en Excel) y establecer una comunicación asíncrona segura con la API de Canvas LMS para el despliegue automático de los recursos.
- **Requerimientos No Funcionales:** Determinados por las restricciones operativas, exigiendo que opere en un entorno de ejecución local autónomo (sin despliegue en la nube), que cuente con una interfaz gráfica intuitiva basada en componente visuales y controles de progreso, y que garantice un tiempo de montaje de procesamiento de 25 minutos por aula.

## Definición de las Historias de Usuario

Las Historias de Usuario constituyen el artefacto central para la especificación de requerimientos dentro del marco de trabajo Scrum, permitiendo capturar las funcionalidades del sistema desde la perspectiva y necesidad del usuario final. Para la aplicación web, estas historias traducen la operatividad diaria de los Analistas de Ambientes de Aprendizaje en unidades de trabajo técnico y de desarrollo de software.

Con el objetivo de garantizar una alineación absoluta entre la tecnología y los procesos institucionales, el levantamiento, análisis y validación de estos requerimientos se llevó a cabo a través de mesas de trabajo conjuntas con la Líder de Ambientes de Aprendizaje. El resultado de este ejercicio es la consolidación del Product Backlog, un inventario estructurado y priorizado que rige el ciclo de construcción del aplicativo web.

Para gestionar adecuadamente el alcance del proyecto, cada historia de usuario ha sido evaluada y cuantificada mediante la técnica de estimación por Story Points (mediante la sucesión de Fibonacci) con el fin de determinar su nivel de complejidad técnica. Asimismo, los requerimientos se distribuyeron priorizando los incrementos de mayor valor operativo para el usuario: el despliegue automatizado en Canvas en el Sprint 2, y la automatización del procesamiento de contenidos con monitoreo visual en el Sprint 3

A continuación, se presenta en la Tabla 4 el resumen general del Product Backlog aprobado para la ejecución del Prototipo Funcional (MVP):

**Tabla 4**  
_Product Backlog: Estimaciones y asignación Ágil por Incrementos_

|     |     |     |     |
| --- | --- | --- | --- |
| **ID** | **Nombre del Requerimiento** | **Estimación (Story Points)** | **Sprint Asignado** |
| HU-01 | Interfaz de selección de Plantilla base (Diseño, Nivel, Tipología) | 3   | Sprint 1 (Modelado y Prototipo Navegable) |
| HU-02 | Formulario de captura de Metadatos (Nombre, código, período) | 3   | Sprint 1 (Modelado y Prototipo Navegable) |
| HU-03 | Interfaz visual de carga de archivos (Zona Drag & Drop para ZIP y Excel) | 5   | Sprint 1 (Modelado y Prototipo Navegable) |
| HU-04 | Validación, desempaquetado y normalización local de archivos .ZIP | 8   | Sprint 1 (Modelado y Prototipo Navegable) |
| **Total S1** | **Velocidad proyectada Sprint 1** | **19 Pts** | &nbsp; |
| HU-05 | Creación automatizada de curso y migración de plantilla vía API | 5   | Sprint 2 (Integración con API Canvas) |
| HU-06 | Subida masiva de archivos a Canvas vía API con gestión de tamaños | 8   | Sprint 2 (Integración con API Canvas) |
| HU-07 | Vinculación de PDFs a Páginas, Tareas de entrega y Foros | 5   | Sprint 2 (Integración con API Canvas) |
| HU-08 | Panel visual de confirmación de despliegue y estado de conexión | 3   | Sprint 2 (Integración con API Canvas) |
| **Total S2** | **Velocidad proyectada Sprint 2** | **21 Pts** | &nbsp; |
| HU-09 | Procesamiento e inyección de paquetes interactivos (Articulate Storyline) | 8   | Sprint 3 (Automatización y Monitoreo) |
| HU-10 | Procesamiento del Guion (Excel) para inyección de textos y multimedia | 5   | Sprint 3 (Automatización y Monitoreo) |
| HU-11 | Monitoreo visual de estado (Barra de progreso) y botón Cancelación | 5   | Sprint 3 (Automatización y Monitoreo) |
| **Total S3** | **Velocidad proyectada Sprint 3** | **18 Pts** | &nbsp; |
| HU-12 | Gestión automática de errores de red y reintentos de subida (x3) | 5   | Sprint 4 (Validación, Pruebas y Resiliencia) |
| HU-13 | Ejecución de pruebas de carga masiva y simulación de escenarios | 5   | Sprint 4 (Validación, Pruebas y Resiliencia) |
| HU-14 | Verificación de enlaces rotos y mensaje de confirmación de éxito | 5   | Sprint 4 (Validación, Pruebas y Resiliencia) |
| HU-15 | Generación y descarga de reporte histórico de operación en Excel | 3   | Sprint 4 (Validación, Pruebas y Resiliencia) |
| **Total S4** | **Velocidad proyectada Sprint 4** | **18 Pts** | &nbsp; |

_Nota_. La estimación de complejidad técnica se realizó mediante la técnica de Story Points basada en la sucesión de Fibonacci. La distribución de los requerimientos refleja un enfoque de desarrollo por funcionalidades completas, garantizando que cada Sprint entregue un incremento de valor demostrable para el usuario final, evitando la separación tradicional por capas tecnológicas. Elaboración propia.

## Sprint 1: Modelado y Prototipo Navegable

El diseño arquitectónico de la aplicación web parte de un principio fundamental: la lógica de automatización ya existe y ha sido validada operativamente en el script Python de 2025. Por lo tanto, la decisión arquitectónica no consiste en crear un sistema desde cero, sino en encapsular, estructurar y exponer esa lógica como un servicio web robusto, escalable y accesible para usuarios no técnicos.

### Stack tecnológico seleccionado

La selección del conjunto tecnológico se fundamentó en las restricciones operativas del proyecto, las cuales exigen un desarrollo con presupuesto cero, ejecución estrictamente local y la necesidad de refactorizar un código heredado en un Prototipo Funcional (MVP) escalable. Para garantizar la mantenibilidad del código y facilitar el modelado UML, el núcleo del sistema se estructurará bajo el paradigma de Programación Orientada a Objetos (POO), aislando las responsabilidades de conexión, procesamiento de archivos y orquestación de datos en clases independientes dentro del servidor.

A continuación se detalla la arquitectura tecnológica seleccionada, dividida por capas lógicas de procesamiento e integración:

**Tabla 5**  
_Stack Tecnológico y Herramientas de Desarrollo_

|     |     |     |     |
| --- | --- | --- | --- |
| **Capa Arquitectónica** | **Tecnología / Herramienta** | **Versión** | **Descripción y Propósito en el Proyecto** |
| _Backend_ (Core) | Python | 3.10+ | Lenguaje base para la manipulación masiva de archivos y refactorización del código legado de 2025. |
| _Backend_ (API) | FastAPI | Reciente | Framework web asíncrono para construir la API REST local. Gestiona el enrutamiento y la comunicación lógica. |
| _Backend_ (Servidor) | Uvicorn | ASGI | Servidor web de alto rendimiento para ejecutar la aplicación FastAPI de manera concurrente. |
| _Backend_ (Datos) | Pydantic | V2  | Validación estricta de esquemas y tipos de datos en memoria antes de la transmisión a Canvas. |
| _Backend_ (Procesamiento) | Pandas & OpenPyXL | Reciente | Librerías especializadas para la lectura, extracción y manipulación de las matrices de datos (Guiones Excel). |
| _Frontend_ (UI) | React.js | 18  | Librería JavaScript basada en componentes para construir la interfaz de usuario interactiva y reactiva. |
| _Frontend_ (Build) | Vite | 5   | Herramienta de compilación y empaquetado ultrarrápida para el entorno de desarrollo local. |
| _Frontend_ (Estilos) | Tailwind CSS | 3   | Framework de CSS utility-first para un diseño ágil, acompañado de Lucide React para iconografía. |
| _Frontend_ (HTTP) | Axios | Reciente | Cliente HTTP basado en promesas para consumir los endpoints asíncronos de la API local. |
| Integración | API Canvas LMS | REST | Interfaz institucional destino para la creación automatizada de cursos, módulos y páginas. |
| Seguridad | Dotenv (.env) | N/A | Gestión segura de variables de entorno para proteger el Bearer Token institucional. |
| Documentación | Swagger UI | OpenAPI 3 | Interfaz autogenerada nativamente por FastAPI para documentar los endpoints locales. |
| Control Versiones | Git & GitHub | N/A | Gestión de ramas, control de cambios y repositorio remoto del código fuente del proyecto. |

_Nota._ Tabla elaborada por el autor del documento detallando los componentes tecnológicos que soportan la arquitectura de la aplicación.

### Diagrama de Casos de Uso y Especificaciones

Para capturar y modelar los requerimientos funcionales desde la perspectiva del usuario final, se construyó el Diagrama de Casos de Uso del sistema. Este artefacto define las fronteras de la aplicación web y establece los contratos de comportamiento entre el actor principal (Analista de Ambientes de Aprendizaje) y los subprocesos automatizados que interactúan de manera asíncrona con el actor secundario (API de Canvas LMS).

Como se observa en la Figura 2, el diseño prioriza la simplicidad en la interfaz de usuario, delegando la complejidad técnica operativa a un flujo de orquestación centralizado mediante relaciones de inclusión («include»).

**Figura 2**_  
Diagrama de Casos de Uso de la Aplicación Web de Automatización_

(Inserta aquí la imagen del diagrama generada, asegurándote de que el cuadro externo diga "Sistema - Aplicación Web de Automatización" y el actor principal sea "Analista de Ambientes de Aprendizaje")

_Nota_. El diagrama modela la interacción del actor principal en el entorno local (React) y la ejecución de los subprocesos automatizados hacia el actor externo (Canvas LMS API). Elaboración propia.

Para garantizar la correcta implementación técnica y la validación de los criterios de aceptación, a continuación se detallan las especificaciones formales de los casos de uso primarios más críticos para la operación del sistema, estructurados bajo el estándar de Cockburn para requerimientos funcionales:

**Tabla 6**  
_Especificación de Caso de Uso: UC-01 Cargar archivo ZIP_

|     |     |
| --- | --- |
| **Atributo** | **Especificación** |
| **Nombre** | UC-01: Cargar archivo ZIP (Prioridad: Crítica) |
| **Descripción** | El analista selecciona y transfiere al servidor local el archivo .ZIP que contiene el material del aula virtual, para que el sistema lo valide y almacene temporalmente antes del procesamiento. |
| **Actor Primario** | Analista de Ambientes de Aprendizaje (Frontend) |
| **Precondiciones** | 1\. La aplicación se encuentra en ejecución local.  <br>2\. El archivo ZIP está disponible en el equipo del analista.  <br>3\. El ZIP sigue la convención de carpetas institucional. |
| **Flujo Principal** | 1\. El analista accede al módulo de despliegue y hace clic en el área de carga.  <br>2\. Selecciona el archivo .zip desde su explorador de archivos.  <br>3\. El sistema valida la extensión del archivo.  <br>4\. El sistema valida que el tamaño no supere los 500 MB.  <br>5\. El sistema muestra la barra de progreso y transmite el archivo.  <br>6\. El sistema almacena el ZIP temporalmente y retorna confirmación.  <br>7\. El sistema habilita el siguiente paso del flujo. |
| **Flujos de Excepción** | FE-01A (Extensión inválida): El archivo no es .zip. El sistema rechaza la carga y notifica al usuario.  <br>FE-01B (Tamaño excedido): Supera los 500 MB. El sistema sugiere comprimir los recursos.  <br>FE-01C (Error de red): Se interrumpe la carga local. El sistema ofrece el botón de reintentar. |
| **Postcondiciones** | El archivo ZIP queda almacenado en el directorio temporal del servidor (tmp/{nombre_zip}/) y su ruta se registra en la sesión activa. |

_Nota._ Elaboración propia.

**Tabla 7  
**_Especificación de Caso de Uso: UC-03 Configurar metadatos del curso_

|     |     |
| --- | --- |
| **Atributo** | **Especificación** |
| **Nombre** | UC-03: Configurar metadatos del curso (Prioridad: Crítica) |
| **Descripción** | El analista define si se creará un curso nuevo duplicando una plantilla o si se inyectarán los recursos en un curso ya existente, ingresando los datos de identificación necesarios. |
| **Actor Primario** | Analista de Ambientes de Aprendizaje (Frontend) |
| **Precondiciones** | 1\. UC-01 completado exitosamente.  <br>2\. El token de administrador de Canvas está configurado en las variables de entorno. |
| **Flujo Principal (Curso Nuevo)** | 1\. El analista selecciona la opción «Crear curso nuevo».  <br>2\. Ingresa el nombre oficial del curso (entre 5 y 255 caracteres).  <br>3\. El sistema valida los campos.  <br>4\. El analista (opcionalmente) carga la matriz en Excel para el _front_ del curso.  <br>5\. El sistema muestra un resumen de la configuración.  <br>6\. El analista confirma y el sistema habilita el botón de despliegue. |
| **Flujos de Excepción** | FE-03A (ID Inválido): Canvas retorna error 404 o 401. El sistema bloquea el avance y notifica falta de permisos o ID erróneo. |
| **Postcondiciones** | El objeto de configuración (_DeploymentConfig_) queda completamente definido y estructurado en memoria, listo para ser procesado por el backend. |

_Nota._ Elaboración propia.

**Tabla 8**  
_Especificación de Caso de Uso: UC-04 Iniciar despliegue asíncrono_

|     |     |
| --- | --- |
| **Atributo** | **Especificación** |
| **Nombre** | UC-04: Iniciar despliegue asíncrono (Prioridad: Crítica) |
| **Descripción** | El analista activa el proceso automatizado que orquesta la creación del curso, extracción del ZIP, carga de archivos, actualización de páginas y vinculación de PDFs en Canvas LMS. |
| **Actor Primario** | Primario: Analista. Secundario: Canvas LMS API. |
| **Precondiciones** | 1\. UC-01 y UC-03 completados.  <br>2\. Configuración válida y verificada.  <br>3\. Conexión a internet estable hacia los servidores institucionales. |
| **Flujo Principal (Curso Nuevo)** | 1\. El analista hace clic en «Iniciar despliegue» y confirma la acción.  <br>2\. El sistema (Frontend) envía el POST al servidor local.  <br>3\. El backend retorna un estado HTTP 202 (Accepted) e inicia la tarea en segundo plano.  <br>4\. El sistema abre un canal de eventos (SSE) para emitir el progreso.  <br>5\. El sistema orquesta secuencialmente los subprocesos (include UC-07 a UC-11).  <br>6\. El sistema finaliza, elimina archivos temporales y emite el estado COMPLETED.  <br>7\. El analista es redirigido a la pantalla de resultados. |
| **Flujos de Excepción** | FE-04A (Token expirado): Canvas retorna HTTP 401. El sistema detiene el proceso y solicita actualización de credenciales.  <br>FE-04B (Timeout de API): Una llamada supera los 30s. El sistema ejecuta hasta 3 reintentos automáticos antes de declarar fallo en el archivo. |
| **Postcondiciones** | El aula virtual en Canvas LMS queda configurada, con archivos subidos, iframes generados y recursos vinculados. Se genera un registro local del resultado de la operación. |

_Nota._ Elaboración propia.

La especificación de estos casos de uso primarios permite establecer un límite claro sobre el comportamiento esperado de la aplicación y las interacciones del usuario final. Sin embargo, para que el sistema cumpla con estos requerimientos funcionales garantizando los atributos de calidad documentados en el marco teórico —tales como la mantenibilidad, la escalabilidad y la gestión resiliente de la comunicación asíncrona con Canvas LMS—, es imperativo traducir este comportamiento externo en una estructura interna cohesiva. A partir de esta necesidad técnica, el diseño del software transita de la perspectiva de interacción del usuario hacia la ingeniería interna del código, estableciendo en el siguiente apartado la arquitectura lógica del backend mediante la definición de sus clases, responsabilidades y el rediseño bajo el paradigma de la Programación Orientada a Objetos.

### Arquitectura lógica: Diagrama de Clases

Para soportar los casos de uso definidos y garantizar atributos de calidad como la mantenibilidad, escalabilidad y testeabilidad, se determinó abandonar el paradigma procedimental del script original y estructurar el núcleo del sistema (backend) bajo el paradigma de Programación Orientada a Objetos (POO).

El diseño arquitectónico se divide en tres capas lógicas principales (Infraestructura, Dominio y Aplicación), aplicando estrictamente el Principio de Responsabilidad Única (SRP) y la Inversión de Dependencias (DIP). En la Figura 3 se detalla la estructura estática del sistema, sus clases, atributos, métodos y relaciones.

**Figura 3**  
_Diagrama de Clases del Núcleo de Automatización (Backend)_

_Nota._ El diagrama ilustra la separación de responsabilidades entre la orquestación, la lógica de dominio y la comunicación HTTP externa. Elaboración propia.

**Diccionario de Clases y Capas Lógicas**

Para facilitar la comprensión del modelo, las entidades del sistema se han clasificado según la capa arquitectónica a la que pertenecen, detallando su responsabilidad principal en la Tabla 9.

**Tabla 9**  
_Diccionario de Clases por Capa Arquitectónica_

|     |     |     |
| --- | --- | --- |
| **Capa** | **Clase** | **Responsabilidad Principal** |
| Infraestructura | CanvasHttpClient | Centralizar y abstraer la comunicación HTTP con la API REST de Canvas LMS, manejando autenticación y reintentos. |
| Infraestructura | CourseRepository  <br>FileRepository  <br>PageRepository | Encapsular las operaciones CRUD específicas de Canvas (cursos, archivos y páginas) aislando al dominio de las peticiones REST. |
| Dominio | ZipProcessor  <br>FileNormalizer | Orquestar la extracción del ZIP local y aplicar reglas de normalización de nombres según la convención institucional. |
| Dominio | InteractiveContentDetector | Identificar paquetes SCORM (story.html) mediante expresiones regulares sobre las rutas de los archivos extraídos. |
| Dominio | IPageComposer_  <br>(Interfaz)_ y sus implementaciones | Definir el contrato de generación de HTML e implementar la lógica de construcción para cada tipo de página (Presentación, Material Fundamental, Front, etc.). |
| Aplicación | PageComposerFactory | Instanciar el compositor de páginas correcto según el tipo solicitado, desacoplando la creación de su uso. |
| Aplicación | DeploymentOrchestrator | Coordinar la secuencia completa del proceso de despliegue delegando tareas en los repositorios y servicios de dominio correspondientes. |
| DTOs | DeploymentConfig  <br>ProgressEvent | Transportar datos de configuración validados y representar el estado puntual de progreso para su serialización hacia el _frontend_. |

_Nota._ Estructuración basada en el Principio de Responsabilidad Única (SRP). Elaboración propia.

**Aplicación de Patrones de Diseño (GoF)**

El rediseño del sistema se fundamentó en la aplicación de patrones de diseño de software (Gamma et al., 1994) y patrones arquitectónicos empresariales (Fowler, 2002), resolviendo problemas específicos de acoplamiento presentes en el código legado:

1.  **Patrón Facade**: Implementado en la clase DeploymentOrchestrator. Soluciona el problema de exposición directa de funciones del script original. El orquestador actúa como una fachada que expone un único método público (deploy()), ocultando la complejidad de los cinco subsistemas internos al cliente web (FastAPI/React), respetando así la Ley de Demeter.
2.  **Patrón Strategy**: Implementado a través de la interfaz IPageComposer y sus clases concretas (IframeComposer, MaterialFundamentalComposer, etc.). Anteriormente, la generación de HTML estaba acoplada en funciones aisladas. Este patrón permite tratar todos los generadores de páginas de forma polimórfica, respetando el Principio Abierto/Cerrado (OCP), ya que añadir un nuevo tipo de página en el futuro no requerirá modificar el orquestador.
3.  **Patrón Simple Factory**: Implementado en PageComposerFactory. Centraliza la lógica de instanciación de las estrategias de generación de páginas, evitando que el orquestador asuma responsabilidades creacionales y eliminando estructuras condicionales complejas.
4.  **Patrón _Repository_:** Implementado en CourseRepository, FileRepository y PageRepository. Desacopla irremediablemente la lógica de dominio de la infraestructura HTTP. El sistema ahora opera sobre abstracciones de dominio (ej. create_course()), mientras que los repositorios se encargan de traducir estas acciones a las llamadas REST requeridas por Canvas LMS, facilitando las pruebas unitarias.

La consolidación de esta arquitectura lógica, sustentada en la separación por capas y la implementación de patrones de diseño estandarizados, garantiza la robustez, cohesión y mantenibilidad del código fuente. Sin embargo, el diseño del sistema no está completo hasta que se define el entorno topológico donde estos componentes de software operarán. Habiendo establecido el "cómo" se estructura internamente la solución, resulta indispensable definir el "dónde" y a través de qué medios de red se ejecutará. En consecuencia, el siguiente apartado aborda la arquitectura física del sistema, empleando el Diagrama de Despliegue para modelar la distribución de los nodos de ejecución locales, el alojamiento del servidor web y la comunicación bidireccional segura con la infraestructura en la nube de Canvas LMS.

### Arquitectura física: Diagrama de Despliegue

Habiendo definido la estructura lógica del sistema, es necesario establecer cómo estos componentes de software se distribuyen y ejecutan en la infraestructura tecnológica. El Diagrama de Despliegue (Figura 4) modela la topología de red del proyecto, evidenciando una arquitectura híbrida donde el procesamiento intensivo y la interfaz de usuario residen en un entorno local seguro, mientras que la persistencia y disponibilidad de los recursos educativos recaen en la infraestructura en la nube (SaaS) de la institución.

**Figura 4**  
_Diagrama de Despliegue de la Solución Tecnológica_

_Nota_. El esquema ilustra los tres nodos principales del sistema y sus fronteras de red. Elaboración propia.

Para detallar la responsabilidad física de cada entorno y los protocolos que garantizan la seguridad e integridad de la comunicación, se presenta el Diccionario de Nodos (Tabla 10).

**Tabla 10**  
_Diccionario de Nodos de Ejecución_

|     |     |     |     |
| --- | --- | --- | --- |
| **Nodo** | **Tipo** | **Artefactos que Aloja** | **Responsabilidad** |
| 1\. Estación de Trabajo del Analista | Cliente Web (Navegador) | React 18 + Vite (SPA), EventSource API, React Query | Proveer la interfaz gráfica (UI) al usuario y mantener la conexión persistente (SSE) para el monitoreo en tiempo real. |
| 2\. Servidor de Aplicación (Local) | Servidor de Backend | Uvicorn ASGI (Puerto 8000), FastAPI Routers, Núcleo de Dominio (Orquestador, Repositorios, Factorías), SQLite (audit.db), Sistema de Archivos (tmp/) | Procesar la lógica de negocio pesada, extraer archivos ZIP localmente y actuar como cliente hacia la API de Canvas. |
| 3\. Nube Institucional (Canvas LMS / AWS) | Servidor SaaS Externo | Canvas REST API, Amazon S3 (Almacenamiento), Base de Datos Canvas | Proveer los endpoints de integración y el almacenamiento definitivo de los recursos educativos del Politécnico Grancolombiano. |

_Nota._ Elaboración propia.

### Diagramas de Comportamiento: Secuencia e Interacción

Para comprender el dinamismo del sistema, es imperativo modelar la dimensión temporal de los procesos. El mayor desafío técnico identificado en el levantamiento de requerimientos fue la restricción de tiempo de respuesta (latencia) y el Rate Limiting impuesto por la API de Canvas LMS durante cargas masivas.

Para resolver esto, se diseñó un flujo de trabajo estrictamente asíncrono. La Figura 5 (Diagrama de Secuencia) modela el Happy Path (ruta de éxito) del caso de uso más crítico: UC-04 Iniciar despliegue asíncrono, evidenciando cómo el sistema desacopla la respuesta al usuario del procesamiento de datos pesado.

**Figura 5**  
_Diagrama de Secuencia del Despliegue Asíncrono_

_Nota._ El diagrama modela la interacción temporal entre el cliente React, el Router de FastAPI, el Orquestador en segundo plano y la API de Canvas LMS. Elaboración propia.

Como se observa en el modelado, el comportamiento asíncrono se divide estratégicamente en tres fases operativas:

**Fase 1 — Petición síncrona e inmediata:** El analista envía el archivo ZIP y la configuración (DeploymentConfig). El router de FastAPI valida la estructura del payload mediante Pydantic v2 e inscribe el proceso de despliegue en el Event Loop como una tarea en segundo plano (BackgroundTask). Inmediatamente, el servidor retorna un código HTTP 202 Accepted con el identificador de la tarea. Este código semántico asegura que la solicitud fue aceptada, pero libera el navegador del usuario antes de ejecutar cualquier procesamiento pesado, mitigando riesgos de timeout en el cliente.

**Fase 2 — Apertura del canal de telemetría (SSE):** Al recibir el estado 202, el frontend abre automáticamente una segunda conexión persistente hacia el servidor utilizando el protocolo Server-Sent Events (text/event-stream). Esta conexión unidireccional permite al cliente escuchar actualizaciones en tiempo real sin saturar el servidor con peticiones de polling redundantes.

**Fase 3 — Procesamiento en segundo plano y emisión de progreso:** El orquestador ejecuta secuencialmente las llamadas a la API externa (crear curso, extraer ZIP, iterar y subir archivos, actualizar páginas). A medida que culmina cada hito crítico, el orquestador inyecta un objeto ProgressEvent en el flujo de salida. Estos eventos son transmitidos inmediatamente a través de la conexión SSE abierta, actualizando la interfaz gráfica del analista (20%, 35%, 65%, 85% y 100%). Al emitirse el estado COMPLETED, la conexión se cierra limpiamente y el flujo concluye con el redireccionamiento al reporte de auditoría.

## Sprint 2: Integración con API Canvas

La segunda iteración del proyecto constituyó el núcleo de interoperabilidad del aplicativo, teniendo como objetivo principal habilitar y asegurar la comunicación entre el entorno local y los sistemas externos de la institución. Durante este Sprint, el esfuerzo técnico se concentró en desarrollar las funcionalidades que permiten la creación automatizada de cursos, la migración de plantillas estructurales y la transferencia masiva de archivos a través de la API institucional.

### Refactorización del código base y lógica local

Para el desarrollo del motor de procesamiento, el proyecto aprovechó una base de conocimiento empírico preexistente: un script desarrollado en Python en el año 2025 que ya ejecutaba la automatización operando desde una consola. El principal desafío arquitectónico consistió en someter este código heredado a un riguroso proceso de refactorización.

Se migró de un enfoque de ejecución lineal y dependiente de un Entorno de Desarrollo Integrado (IDE) hacia una estructura basada en el paradigma de Programación Orientada a Objetos (POO). Esta transición permitió modularizar el código, aislando las responsabilidades de validación, transformación de datos y consumo de servicios en clases independientes. Esta reestructuración fue un paso obligatorio para poder encapsular la lógica de negocio dentro de un servidor web moderno y exponerla de manera segura a través de endpoints locales.

### Construcción de la API REST y conexión con Canvas

El _backend_ de la aplicación se materializó mediante la implementación de FastAPI, seleccionado por su alto rendimiento y su capacidad para gestionar operaciones asíncronas de entrada y salida (I/O). La conexión directa con el entorno de Canvas LMS se logró mediante la configuración de un cliente HTTP interno que inyecta un Bearer Token institucional en las cabeceras de cada petición, el cual fue asegurado mediante la gestión de variables de entorno (.env).

A nivel funcional, se construyeron los controladores responsables de ejecutar los métodos POST y PUT requeridos para la creación de módulos, la subida de recursos y la vinculación de documentos PDF a páginas, tareas y foros. Durante esta construcción, se incorporó lógica específica para gestionar los tamaños de los archivos y mitigar los impactos de las políticas de _Rate Limiting_ (límite de peticiones por segundo) impuestas por los servidores de Canvas, asegurando que el proceso de subida, aunque demore un promedio de 6 minutos, se ejecute de manera desatendida y estable.

## Sprint 3: Automatización y Monitoreo

### Diseño de la interfaz gráfica (UI) y componentes

\[Nota: El contenido de esta sección se encuentra actualmente en fase de ejecución. Su redacción y documentación detallada se desarrollarán e integrarán en las próximas entregas del documento, conforme al avance de los Sprints y el cronograma de actividades establecido para la Práctica Empresarial\].

### Integración y consumo de servicios

\[Nota: El contenido de esta sección se encuentra actualmente en fase de ejecución. Su redacción y documentación detallada se desarrollarán e integrarán en las próximas entregas del documento, conforme al avance de los Sprints y el cronograma de actividades establecido para la Práctica Empresarial\].

## Sprint 4: Validación, Pruebas y Resiliencia

### Simulación de escenarios y pruebas de carga

\[Nota: El contenido de esta sección se encuentra actualmente en fase de ejecución. Su redacción y documentación detallada se desarrollarán e integrarán en las próximas entregas del documento, conforme al avance de los Sprints y el cronograma de actividades establecido para la Práctica Empresarial\].

### Gestión de errores y resiliencia

\[Nota: El contenido de esta sección se encuentra actualmente en fase de ejecución. Su redacción y documentación detallada se desarrollarán e integrarán en las próximas entregas del documento, conforme al avance de los Sprints y el cronograma de actividades establecido para la Práctica Empresarial\].

# Resultados y hallazgos

## Presentación y análisis de los datos recolectados

Tras la ejecución de las pruebas operativas del Prototipo Funcional (MVP) en el entorno local del equipo de Ambientes de Aprendizaje, los datos cronometrados evidencian una transformación radical en el ciclo de trabajo. El proceso manual, que previamente consumía un promedio de 240 minutos por asignatura, fue contrastado directamente con la ejecución automatizada. El análisis detallado por etapas demuestra los siguientes hallazgos:

- La configuración inicial del aula pasó de 20 minutos manuales a resolverse en 1 minuto, representando un ahorro del 95,00%.
- La subida de archivos, que tomaba 10 minutos, se estabilizó en 6 minutos bajo el modelo automatizado.
- La etapa más crítica, correspondiente a la creación de páginas, experimentó la mayor reducción absoluta, pasando de 115 minutos a tan solo 1 minuto (99,13% de ahorro).
- Tanto la vinculación de PDFs como la configuración de la página principal pasaron de 40 minutos a 1 minuto cada una, logrando un 97,50% de optimización respectivamente.
- La revisión final se mantuvo constante en 15 minutos, garantizando el aseguramiento de la calidad sin penalizar el flujo automatizado.

El impacto total consolida un tiempo de ejecución automatizado de 25 minutos frente a los 240 minutos originales.

## Contrastación de la hipótesis de optimización

La hipótesis de trabajo establecía que la implementación de la aplicación web sobre la API de Canvas LMS reduciría el tiempo de montaje a un máximo de 25 minutos, optimizando la capacidad de respuesta en un 89,58%. Los datos obtenidos tras las pruebas de simulación aceptan y confirman íntegramente esta hipótesis. El sistema logró una optimización neta del 89,58% en el ciclo de trabajo por cada Aula Máster.

Es importante destacar que el comportamiento asimétrico en la etapa de "Subida de archivos" (reducción de solo 40%, tardando 6 minutos frente a otras tareas de 1 minuto) no refuta la hipótesis, sino que obedece a las restricciones físicas de infraestructura. Este tiempo responde a la latencia en la transferencia de paquetes interactivos pesados (Archivos multimedia) y a las políticas de _Rate limiting_ impuestas por los servidores institucionales de Canvas LMS. A pesar de ello, el análisis confirma el éxito del prototipo, dado que esta subida de 6 minutos se realiza de forma asíncrona, liberando completamente al analista operativo.

## Impacto en capacidad operativa institucional

La reducción empírica del tiempo de montaje genera un impacto inmediato en la escalabilidad del modelo de educación virtual. Bajo la ejecución manual, la carga de trabajo limitaba al área a un máximo de montaje de 2 a 3 cursos diarios por analista, sumando una capacidad tope de 6 a 9 cursos para todo el equipo de Ambientes de Aprendizaje.

Con la estabilización del proceso en 25 minutos por asignatura, el equipo supera este cuello de botella y adquiere la capacidad tecnológica para atender picos de demanda durante los inicios de cada período académico. Adicionalmente, se evidencia la mitigación de la propensión a errores operativos asociados a tareas manuales y repetitivas, garantizando un despliegue de aulas estandarizado y oportuno para los estudiantes.

# Conclusiones y recomendaciones

## Conclusiones

- El desarrollo del prototipo funcional de aplicación web cumplió a cabalidad con el objetivo general, logrando automatizar el montaje masivo de Aulas Máster en Canvas LMS y reduciendo el margen de error humano.
- La refactorización del script legado en Python hacia una arquitectura cliente-servidor (con FastAPI y React.js) eliminó con éxito la dependencia de entornos de desarrollo integrados (IDE) altamente técnicos. Esta transición descentralizó el conocimiento operativo y democratizó el uso de la herramienta para todo el equipo de analistas.
- La adopción de metodologías ágiles como Scrum y el uso de la Metodología SMART demostraron ser efectivos para estructurar un producto viable dentro del alcance académico, logrando un desarrollo estable bajo las restricciones de presupuesto cero y ejecución local impuestas al proyecto.

## Recomendaciones y trabajos futuros

- Dado que el aplicativo web fue diseñado y delimitado para operar de manera autónoma en un entorno de ejecución local, se recomienda al Departamento de Tecnología del Politécnico Grancolombiano planificar una fase de despliegue en la nube (AWS, Google Cloud o Azure) en arquitecturas productivas institucionales.
- Se sugiere integrar sistemas de autenticación robustos vinculados al Directorio Activo Institucional para elevar los estándares de ciberseguridad en versiones futuras de la herramienta.
- Como evolución funcional del prototipo, se recomienda analizar la viabilidad técnica para incluir la parametrización y automatización de bancos de preguntas, una característica excluida del MVP actual debido a la complejidad de las estructuras de datos de Canvas LMS frente al tiempo del proyecto.

# Bibliografía

Algamdi, S. & Ludi, S. (2025). Exploring usability factors in Canvas educational applications: An empirical analysis. En K. Arai (Ed.), _Advances in information and communication. FICC 2025. Lecture Notes in Networks and Systems_ (Vol. 1285, pp. 254–271). Springer. https://doi.org/10.1007/978-3-031-85363-0_15

Bass, L., Clements, P., & Kazman, R. (2012). _Software architecture in practice_ (3.ª ed.). Addison-Wesley Professional.

Booch, G., Rumbaugh, J., & Jacobson, I. (2005). _The unified modeling language user guide_ (2.ª ed.). Addison-Wesley.

Brito, G. & Valente, M. T. (2020). REST vs GraphQL: A controlled experiment. En _2020 IEEE International Conference on Software Architecture (ICSA)_ (pp. 81–91). IEEE. https://doi.org/10.1109/ICSA47634.2020.00016

Doran, G. T. (1981). There's a SMART way to write management's goals and objectives. _Management Review_, _70_(11), 35–36.

Fielding, R. T. (2000). _Architectural styles and the design of network-based software architectures_ \[Tesis doctoral, University of California, Irvine\]. https://ics.uci.edu/~fielding/pubs/dissertation/fielding_dissertation.pdf

Fowler, M. (2004). _UML distilled: A brief guide to the standard object modeling language_ (3.ª ed.). Addison-Wesley.

Fowler, M. (2018). _Refactoring: Improving the design of existing code_ (2.ª ed.). Addison-Wesley Professional.

GraphQL Foundation. (2021). _GraphQL specification_. https://spec.graphql.org/

Hron, M. & Obwegeser, N. (2022). Why and how is Scrum being adapted in practice: A systematic review. _Journal of Systems and Software_, _183_, Artículo 111110. https://doi.org/10.1016/j.jss.2021.111110

Instructure, Inc. (2026). _Canvas LMS REST API documentation_. https://canvas.instructure.com/doc/api/

Li, S., Zhang, H., Jia, Z., Zhong, C., Zhang, C., Shan, Z., Shen, J. & Babar, M. A. (2021). Understanding and addressing quality attributes of microservices architecture: A systematic literature review. _Information and Software Technology_, _131_, Artículo 106449. https://doi.org/10.1016/j.infsof.2020.106449

Mowla, S. & Kolekar, S. V. (2020). Development and integration of e-learning services using REST APIs. _International Journal of Emerging Technologies in Learning (iJET)_, _15_(4), 53–72. https://doi.org/10.3991/ijet.v15i04.11687

Mpungose, C. B. & Khoza, S. B. (2022). Postgraduate students' experiences on the use of Moodle and Canvas learning management system. _Technology, Knowledge and Learning_, _27_(1), 1–16. https://doi.org/10.1007/s10758-020-09475-1

Object Management Group. (2017). _OMG unified modeling language specification, version 2.5.1_. https://www.omg.org/spec/UML/2.5.1

Ozkaya, M. & Erata, F. (2020). A survey on the practical use of UML for different software architecture viewpoints. _Information and Software Technology_, _121_, Artículo 106275. https://doi.org/10.1016/j.infsof.2020.106275

Peruma, A., Simmons, S., AlOmar, E. A., Newman, C. D., Mkaouer, M. W. & Ouni, A. (2022). How do I refactor this? An empirical study on refactoring trends and topics in Stack Overflow. _Empirical Software Engineering_, _27_(1), Artículo 11. https://doi.org/10.1007/s10664-021-10045-x

Perry, D. E., & Wolf, A. L. (1992). Foundations for the study of software architecture. _ACM SIGSOFT Software Engineering Notes_, _17_(4), 40–52. https://doi.org/10.1145/141874.141884

Project Management Institute. (2021). _A guide to the project management body of knowledge (PMBOK® Guide)_ (7.ª ed.). Project Management Institute.

Schwaber, K., & Sutherland, J. (2020). _The Scrum guide: The definitive guide to Scrum: The rules of the game_. Scrum.org. https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf

Simon, P. D., Jiang, J., Fryer, L. K., King, R. B. & Frondozo, C. E. (2025). An assessment of learning management system use in higher education: Perspectives from a comprehensive sample of teachers and students. _Technology, Knowledge and Learning_, _30_(2), 741–767. https://doi.org/10.1007/s10758-024-09734-5

Sulaiman, T. T. (2024). A systematic review on factors influencing learning management system usage in Arab Gulf countries. _Education and Information Technologies_, _29_(2), 2503–2521. https://doi.org/10.1007/s10639-023-11936-w

Turnbull, D., Chugh, R. & Luck, J. (2021). Issues in learning management systems implementation: A comparison of research perspectives between Australia and China. _Education and Information Technologies_, _26_(4), 3789–3810. https://doi.org/10.1007/s10639-021-10431-4

Turnbull, D., Chugh, R. & Luck, J. (2022). An overview of the common elements of learning management system policies in higher education institutions. _TechTrends_, _66_(5), 855–867. https://doi.org/10.1007/s11528-022-00752-7

Verwijs, C. & Russo, D. (2023). A theory of Scrum team effectiveness. _ACM Transactions on Software Engineering and Methodology_, _32_(3), Artículo 74, 1–51. https://doi.org/10.1145/3571849

# Anexos