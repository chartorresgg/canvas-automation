# backend/app/presentation/routers/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check() -> dict:
    """Verifica que el servidor está operativo."""
    return {
        "status": "ok",
        "service": "Canvas LMS Automation API",
        "version": "0.1.0",
    }