"""
Value Object de entrada de auditoría de despliegue.

Representa un registro inmutable de un despliegue ejecutado.
Capa: Dominio
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditEntry:
    """
    Registro inmutable de un despliegue de aula virtual.

    Todos los campos son establecidos al momento de la creación
    y no pueden modificarse (frozen=True).
    """
    task_id:          str
    course_id:        int | None
    course_name:      str
    template_id:      int | None
    zip_filename:     str
    total_archivos:   int
    archivos_subidos: int
    duracion_seg:     float
    estado:           str        # "completed" | "failed" | "cancelled"
    error_detalle:    str | None
    iniciado_en:      datetime
    finalizado_en:    datetime
    modelo_instruccional: str
    nivel_formacion:  str

    @property
    def duracion_display(self) -> str:
        """Duración formateada como '4m 32s'."""
        minutos = int(self.duracion_seg // 60)
        segundos = int(self.duracion_seg % 60)
        if minutos > 0:
            return f"{minutos}m {segundos}s"
        return f"{segundos}s"

    @property
    def estado_display(self) -> str:
        """Estado con emoji para visualización."""
        return {
            "completed": "✅ Exitoso",
            "failed":    "❌ Error",
            "cancelled": "⊘ Cancelado",
        }.get(self.estado, self.estado)

    def to_dict(self) -> dict:
        """Serializa para JSON o exportación Excel."""
        return {
            "task_id":            self.task_id,
            "course_id":          self.course_id,
            "course_name":        self.course_name,
            "template_id":        self.template_id,
            "zip_filename":       self.zip_filename,
            "total_archivos":     self.total_archivos,
            "archivos_subidos":   self.archivos_subidos,
            "duracion_seg":       round(self.duracion_seg, 1),
            "duracion_display":   self.duracion_display,
            "estado":             self.estado,
            "estado_display":     self.estado_display,
            "error_detalle":      self.error_detalle,
            "iniciado_en":        self.iniciado_en.isoformat(),
            "finalizado_en":      self.finalizado_en.isoformat(),
            "modelo_instruccional": self.modelo_instruccional,
            "nivel_formacion":    self.nivel_formacion,
        }