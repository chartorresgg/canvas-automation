"""
Schemas Pydantic de request/response para los endpoints de la API.

Separados de los value objects de dominio para respetar la separación
entre capa de presentación y capa de dominio.

Capa: Presentación
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DeployStartResponse(BaseModel):
    """Respuesta del endpoint POST /api/v1/deploy."""
    task_id:    str = Field(description="ID único de la tarea de despliegue.")
    stream_url: str = Field(description="URL del endpoint SSE para monitorear el progreso.")
    message:    str = Field(description="Confirmación de inicio del proceso.")


class ProgressEventSchema(BaseModel):
    """Schema de un evento de progreso para la documentación de Swagger."""
    step:        int   = Field(description="Paso actual (0-5).")
    total_steps: int   = Field(description="Total de pasos del proceso.")
    message:     str   = Field(description="Mensaje descriptivo del estado.")
    percentage:  float = Field(description="Porcentaje de avance (0.0-100.0).")
    status:      str   = Field(description="Estado: pending/running/completed/failed/cancelled.")
    detail:      str | None = Field(default=None)
    course_id:   int | None = Field(default=None)
    error:       str | None = Field(default=None)