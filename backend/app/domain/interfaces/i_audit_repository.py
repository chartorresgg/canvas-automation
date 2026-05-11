"""
Interfaz del repositorio de auditoría.

Define el contrato que deben cumplir todas las implementaciones
de persistencia (SQLite, PostgreSQL, etc.).

Capa: Dominio — interfaces
Patrón: Repository
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.value_objects.audit_entry import AuditEntry


class IAuditRepository(ABC):
    """
    Contrato de persistencia para el registro de auditoría.

    Implementaciones:
        SQLiteAuditRepository  — desarrollo y MVP local
        PostgresAuditRepository — producción en nube (futura)

    El orquestador y los routers dependen de esta abstracción,
    nunca de una implementación concreta (principio DIP).
    """

    @abstractmethod
    async def guardar(self, entry: AuditEntry) -> None:
        """Persiste una entrada de auditoría."""

    @abstractmethod
    async def listar(
        self,
        limite:  int = 100,
        offset:  int = 0,
        estado:  str | None = None,
    ) -> list[AuditEntry]:
        """
        Retorna entradas de auditoría ordenadas por fecha descendente.

        Args:
            limite: Máximo de registros a retornar.
            offset: Desplazamiento para paginación.
            estado: Filtrar por estado ('completed', 'failed', 'cancelled').
        """

    @abstractmethod
    async def contar(self, estado: str | None = None) -> int:
        """Cuenta el total de registros (para paginación)."""