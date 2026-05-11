"""
Implementación SQLite del repositorio de auditoría.

Usa aiosqlite para operaciones async sin bloquear el event loop.
La base de datos se crea automáticamente en la primera ejecución.

Para migrar a PostgreSQL en el futuro:
    1. Crear postgres_audit_repository.py implementando IAuditRepository
    2. Cambiar la inyección en dependencies.py
    3. No tocar ningún otro archivo

Capa: Infraestructura — persistencia
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from app.domain.interfaces.i_audit_repository import IAuditRepository
from app.domain.value_objects.audit_entry import AuditEntry

logger = logging.getLogger(__name__)

# DDL de la tabla principal
_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS audit_despliegues (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id              TEXT    NOT NULL UNIQUE,
    course_id            INTEGER,
    course_name          TEXT    NOT NULL DEFAULT '',
    template_id          INTEGER,
    zip_filename         TEXT    NOT NULL DEFAULT '',
    total_archivos       INTEGER NOT NULL DEFAULT 0,
    archivos_subidos     INTEGER NOT NULL DEFAULT 0,
    duracion_seg         REAL    NOT NULL DEFAULT 0,
    estado               TEXT    NOT NULL DEFAULT 'completed',
    error_detalle        TEXT,
    iniciado_en          TEXT    NOT NULL,
    finalizado_en        TEXT    NOT NULL,
    modelo_instruccional TEXT    NOT NULL DEFAULT '',
    nivel_formacion      TEXT    NOT NULL DEFAULT ''
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_audit_iniciado
ON audit_despliegues (iniciado_en DESC);
"""


class SQLiteAuditRepository(IAuditRepository):
    """
    Repositorio de auditoría persistente en SQLite.

    El archivo .db se crea automáticamente al primer uso.
    Toda operación I/O es async vía aiosqlite.

    Args:
        db_path: Ruta al archivo SQLite.
                 Default: backend/data/audit_log.db
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    async def _inicializar(self, conn: aiosqlite.Connection) -> None:
        """Crea la tabla e índices si no existen."""
        await conn.execute(_CREATE_TABLE)
        await conn.execute(_CREATE_INDEX)
        await conn.commit()

    async def guardar(self, entry: AuditEntry) -> None:
        """
        Persiste una entrada de auditoría.

        Usa INSERT OR REPLACE para manejar el caso donde el mismo
        task_id se intenta guardar dos veces (idempotente).
        """
        async with aiosqlite.connect(str(self._db_path)) as conn:
            await self._inicializar(conn)
            await conn.execute(
                """
                INSERT OR REPLACE INTO audit_despliegues (
                    task_id, course_id, course_name, template_id,
                    zip_filename, total_archivos, archivos_subidos,
                    duracion_seg, estado, error_detalle,
                    iniciado_en, finalizado_en,
                    modelo_instruccional, nivel_formacion
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    entry.task_id,
                    entry.course_id,
                    entry.course_name,
                    entry.template_id,
                    entry.zip_filename,
                    entry.total_archivos,
                    entry.archivos_subidos,
                    entry.duracion_seg,
                    entry.estado,
                    entry.error_detalle,
                    entry.iniciado_en.isoformat(),
                    entry.finalizado_en.isoformat(),
                    entry.modelo_instruccional,
                    entry.nivel_formacion,
                ),
            )
            await conn.commit()
            logger.info(
                "Auditoría guardada: task_id=%s estado=%s curso=%s",
                entry.task_id, entry.estado, entry.course_name,
            )

    async def listar(
        self,
        limite:  int = 100,
        offset:  int = 0,
        estado:  str | None = None,
    ) -> list[AuditEntry]:
        """Retorna entradas ordenadas por fecha más reciente primero."""
        async with aiosqlite.connect(str(self._db_path)) as conn:
            conn.row_factory = aiosqlite.Row
            await self._inicializar(conn)

            if estado:
                cursor = await conn.execute(
                    """
                    SELECT * FROM audit_despliegues
                    WHERE estado = ?
                    ORDER BY iniciado_en DESC
                    LIMIT ? OFFSET ?
                    """,
                    (estado, limite, offset),
                )
            else:
                cursor = await conn.execute(
                    """
                    SELECT * FROM audit_despliegues
                    ORDER BY iniciado_en DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limite, offset),
                )

            filas = await cursor.fetchall()
            return [self._fila_a_entry(f) for f in filas]

    async def contar(self, estado: str | None = None) -> int:
        """Cuenta el total de registros para paginación."""
        async with aiosqlite.connect(str(self._db_path)) as conn:
            await self._inicializar(conn)
            if estado:
                cursor = await conn.execute(
                    "SELECT COUNT(*) FROM audit_despliegues WHERE estado = ?",
                    (estado,),
                )
            else:
                cursor = await conn.execute(
                    "SELECT COUNT(*) FROM audit_despliegues"
                )
            row = await cursor.fetchone()
            return row[0] if row else 0

    @staticmethod
    def _fila_a_entry(fila: aiosqlite.Row) -> AuditEntry:
        """Convierte una fila SQLite en un AuditEntry."""
        return AuditEntry(
            task_id=          fila["task_id"],
            course_id=        fila["course_id"],
            course_name=      fila["course_name"],
            template_id=      fila["template_id"],
            zip_filename=     fila["zip_filename"],
            total_archivos=   fila["total_archivos"],
            archivos_subidos= fila["archivos_subidos"],
            duracion_seg=     fila["duracion_seg"],
            estado=           fila["estado"],
            error_detalle=    fila["error_detalle"],
            iniciado_en=      datetime.fromisoformat(fila["iniciado_en"]),
            finalizado_en=    datetime.fromisoformat(fila["finalizado_en"]),
            modelo_instruccional= fila["modelo_instruccional"],
            nivel_formacion=      fila["nivel_formacion"],
        )