"""
Router de autenticación por token de Canvas.

Expone los endpoints de login, logout y validación de sesión.
El token Canvas se valida contra la API institucional antes de
crear la sesión, garantizando que solo tokens válidos son aceptados.

Capa: Presentación
HU-16: Token de Canvas como contraseña de ingreso
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.infrastructure.canvas.http_client import CanvasHttpClient, CanvasAuthError
from app.presentation.session_manager import session_manager

logger = logging.getLogger(__name__)
router = APIRouter()


class LoginRequest(BaseModel):
    """Cuerpo del request de login."""
    canvas_token: str


@router.post(
    "/auth/login",
    summary="Iniciar sesión con token Canvas",
    description=(
        "Valida el token Canvas contra la API institucional. "
        "Si es válido, crea una sesión y retorna el session_id "
        "que el frontend debe enviar en cada request posterior "
        "como header X-Session-ID."
    ),
)
async def login(body: LoginRequest) -> JSONResponse:
    """
    Valida el token Canvas y crea una sesión activa.

    Llama a GET /api/v1/users/self con el token proporcionado.
    Si Canvas responde con 200, el token es válido y se crea la sesión.
    Si Canvas responde con 401 o 403, el token es inválido o sin permisos.

    Returns:
        JSON con session_id, nombre y email del usuario Canvas.
    """
    if not body.canvas_token or not body.canvas_token.strip():
        raise HTTPException(
            status_code=400,
            detail="El token Canvas no puede estar vacío.",
        )

    # Validar token contra Canvas
    try:
        http = CanvasHttpClient(token=body.canvas_token.strip())
        await http.__aenter__()
        try:
            user_info = await http.get("users/self")
        finally:
            await http.__aexit__(None, None, None)

    except CanvasAuthError:
        raise HTTPException(
            status_code=401,
            detail=(
                "Token Canvas inválido o sin permisos suficientes. "
                "Verifica que el token sea correcto y tenga permisos "
                "de administrador en Canvas."
            ),
        )
    except Exception as exc:
        logger.error("Error al validar token Canvas: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="No fue posible conectar con Canvas LMS. "
                   "Verifica tu conexión a internet.",
        )

    user_name  = user_info.get("name", "Usuario")
    user_email = user_info.get("email", "")

    session_id = session_manager.crear_sesion(
        canvas_token=body.canvas_token.strip(),
        user_name=user_name,
        user_email=user_email,
    )

    logger.info("Login exitoso: %s (%s)", user_name, user_email)

    return JSONResponse({
        "session_id": session_id,
        "user_name":  user_name,
        "user_email": user_email,
        "message":    f"Bienvenido, {user_name}.",
    })


@router.post(
    "/auth/logout",
    summary="Cerrar sesión",
)
async def logout(
    x_session_id: str = Header(alias="X-Session-ID", default=""),
) -> JSONResponse:
    """Cierra la sesión activa y elimina el token de la memoria."""
    cerrada = session_manager.cerrar_sesion(x_session_id)
    if not cerrada:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada o ya cerrada.",
        )
    return JSONResponse({"message": "Sesión cerrada correctamente."})


@router.get(
    "/auth/validate",
    summary="Validar sesión activa",
)
async def validate_session(
    x_session_id: str = Header(alias="X-Session-ID", default=""),
) -> JSONResponse:
    """
    Verifica si una sesión está activa.

    El frontend llama a este endpoint al cargar la app para saber
    si el analista ya tiene una sesión válida o debe hacer login.
    """
    entry = session_manager.obtener_usuario(x_session_id)
    if not entry:
        raise HTTPException(
            status_code=401,
            detail="Sesión no encontrada o expirada.",
        )
    return JSONResponse({
        "valid":      True,
        "user_name":  entry.user_name,
        "user_email": entry.user_email,
    })