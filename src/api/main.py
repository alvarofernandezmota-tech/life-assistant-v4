"""
src/api/main.py - FastAPI Application Entry Point
Autor: alvarofernandezmota-tech
Fecha: 2026-03-07
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import rpg
from ..config.settings import settings

app = FastAPI(
    title="Life Assistant V4 API",
    description="Sistema RPG Caronte + Gestión de Vida",
    version="1.5.0",
)

# CORS (permitir frontend local + producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: lista específica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(rpg.router)

@app.get("/")
def root():
    return {
        "app":     "Life Assistant V4",
        "version": "1.5.0",
        "status":  "operational",
        "system":  "Caronte RPG + Dados",
    }

@app.get("/health")
def health():
    return {"status": "ok", "message": "API funcionando correctamente"}
