"""Fábrica de la aplicación FastAPI — Canvas LMS Automation API."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.routers import health, deploy, audit, benchmark, auth

app = FastAPI(
    title="Canvas LMS Automation API",
    version="1.0.0",
    description="API para automatizar el montaje de aulas en Canvas LMS.",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# En desarrollo: acepta localhost
# En producción: acepta la URL de Vercel configurada en FRONTEND_URL
_origenes = ["http://localhost:5173", "http://localhost:4173"]
_frontend_url = os.getenv("FRONTEND_URL", "")

if _frontend_url:
    _origenes.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origenes,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registro de Rutas ─────────────────────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/v1", tags=["Auth"])
app.include_router(health.router,    prefix="/api/v1", tags=["Health"])
app.include_router(deploy.router,    prefix="/api/v1", tags=["Deploy"])
app.include_router(audit.router,     prefix="/api/v1", tags=["Audit"])
app.include_router(benchmark.router, prefix="/api/v1", tags=["Benchmark"])