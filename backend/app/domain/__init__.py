# domain/models/__init__.py
"""
Este sistema no define entidades de dominio persistidas (User, Course, etc.)
porque actúa como orquestador: los datos de negocio viven en Canvas LMS.
Las reglas de negocio están encapsuladas en:
  - domain/value_objects/  → DeploymentConfig, ProgressEvent
  - domain/services/       → ZipProcessor, FileNormalizer, etc.
"""