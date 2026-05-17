"""
Gestor de sesiones para autenticación por token de Canvas.

Almacena en memoria el token Canvas asociado a cada sesión activa.
El token nunca se persiste en disco — se pierde al reiniciar el servidor
o al cerrar sesión explícitamente, por diseño de seguridad.

Capa: Presentación
HU-16: Token de Canvas como contraseña de ingreso
"""

from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class SessionEntry:
    """Entrada de sesión activa."""
    session_id:   str
    canvas_token: str
    user_name:    str
    user_email:   str
    creada_en:    datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class SessionManager:
    """
    Registro en memoria de sesiones activas.

    Responsabilidad única: asociar un session_id generado por el sistema
    al token Canvas del analista, de modo que cada request posterior
    pueda recuperar el token sin que el frontend lo reenvíe completo.

    El token nunca toca el disco. Al reiniciar el servidor, todas
    las sesiones se pierden y el analista debe volver a ingresar.
    """

    def __init__(self) -> None:
        self._sesiones: dict[str, SessionEntry] = {}

    def crear_sesion(
        self,
        canvas_token: str,
        user_name:    str,
        user_email:   str,
    ) -> str:
        """
        Crea una nueva sesión y retorna el session_id.

        El session_id es un token seguro de 32 bytes generado con
        secrets.token_urlsafe — no predecible ni enumerable.
        """
        session_id = secrets.token_urlsafe(32)
        self._sesiones[session_id] = SessionEntry(
            session_id=session_id,
            canvas_token=canvas_token,
            user_name=user_name,
            user_email=user_email,
        )
        logger.info("Sesión creada para usuario: %s", user_name)
        return session_id

    def obtener_token(self, session_id: str) -> str | None:
        """Retorna el token Canvas de una sesión activa o None."""
        entry = self._sesiones.get(session_id)
        return entry.canvas_token if entry else None

    def obtener_usuario(self, session_id: str) -> SessionEntry | None:
        """Retorna la entrada completa de sesión o None."""
        return self._sesiones.get(session_id)

    def cerrar_sesion(self, session_id: str) -> bool:
        """Elimina una sesión activa. Retorna True si existía."""
        if session_id in self._sesiones:
            entry = self._sesiones.pop(session_id)
            logger.info("Sesión cerrada: %s", entry.user_name)
            return True
        return False

    def existe(self, session_id: str) -> bool:
        """Verifica si una sesión está activa."""
        return session_id in self._sesiones


# Singleton — una instancia por proceso del servidor
session_manager = SessionManager()