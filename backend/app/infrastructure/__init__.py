# infrastructure/persistence/__init__.py
"""
Persistencia: esta aplicación no usa base de datos local.
Es stateless entre despliegues — el estado vive en Canvas LMS.
El único estado en memoria es el TaskManager (queues SSE activas)
que se reinicia con el servidor.
"""