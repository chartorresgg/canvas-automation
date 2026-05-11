"""Fábrica de la aplicación FastAPI — Canvas LMS Automation API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.presentation.routers import health, deploy, audit
from app.presentation.routers import health, deploy
from app.presentation.routers import health, deploy, audit, benchmark

app = FastAPI(
    title="Canvas LMS Automation API",
    description="API para automatizar el montaje de aulas virtuales en Canvas LMS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(deploy.router, prefix="/api/v1", tags=["Deploy"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(deploy.router, prefix="/api/v1", tags=["Deploy"])
app.include_router(audit.router,  prefix="/api/v1", tags=["Audit"])
app.include_router(health.router,     prefix="/api/v1", tags=["Health"])
app.include_router(deploy.router,     prefix="/api/v1", tags=["Deploy"])
app.include_router(audit.router,      prefix="/api/v1", tags=["Audit"])
app.include_router(benchmark.router,  prefix="/api/v1", tags=["Benchmark"])