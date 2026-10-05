# Canvas LMS Automation — Documentación Técnica

Documentación técnica del proyecto de grado desarrollado para el
**Politécnico Grancolombiano** — Práctica Empresarial, Ingeniería de Sistemas.

* **Autor:** Carlos Eduardo Guzmán Torres
* **Asesor:** Wilson Eduardo Soto Forero
* **Tutor:** Javier Fernando Niño Velásquez

---

## ¿Qué es este proyecto?

Aplicación web que automatiza el montaje de aulas virtuales en Canvas LMS,
reduciendo el tiempo de configuración de **~240 minutos a ~25 minutos por aula**
(reducción del 89.6%).

---

## Contenido del Wiki

| Página | Descripción |
|---|---|
| [Getting-Started](https://github.com/chartorresgg/canvas-automation/wiki/Getting%E2%80%90Started) | Instalación, configuración y primer despliegue |
| [Architecture](https://github.com/chartorresgg/canvas-automation/wiki/Architecture) | Clean Architecture, patrones de diseño y flujo del sistema |
| [API Reference](https://github.com/chartorresgg/canvas-automation/wiki/API%E2%80%90Reference) | Los 9 endpoints REST con contratos de entrada/salida |
| [Conventions](https://github.com/chartorresgg/canvas-automation/wiki/Conventions) | Conventional Commits, nomenclatura y estándares de código |
| [Troubleshooting](https://github.com/chartorresgg/canvas-automation/wiki/Troubleshooting) | Errores frecuentes y sus soluciones |

---

## Estado del proyecto

| Sprint | Objetivo | HU | Estado |
|---|---|---|---|
| Sprint 1 | Arquitectura base y dominio | HU-01 a HU-04 | ✅ Completo |
| Sprint 2 | Integración Canvas API | HU-05 a HU-08 | ✅ Completo |
| Sprint 3 | Automatización y monitoreo | HU-09 a HU-11, HU-14 | ✅ Completo |
| Sprint 4 | Resiliencia y despliegue | HU-12, HU-13, HU-15 | ✅ Completo |

**Fase 1 completa:** 17 Historias de Usuario · 84 Story Points · 400+ tests unitarios

---

## Stack tecnológico
* Backend:  Python 3.11 · FastAPI · SQLite · httpx (async)
* Frontend: React 18 · TypeScript · Vite · Tailwind CSS
* LMS: Canvas Instructure API (poli.instructure.com)
* CI/CD: GitHub Actions

---

## Links rápidos

- [Repositorio](https://github.com/chartorresgg/canvas-aulas-master)
- [API Swagger](http://localhost:8000/docs) ← disponible con el servidor corriendo
- [Backlog completo de HU](https://github.com/chartorresgg/canvas-aulas-master/blob/main/historias_de_usuario.md)
