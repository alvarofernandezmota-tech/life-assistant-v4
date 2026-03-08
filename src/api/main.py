"""
src/api/main.py - FastAPI Application Entry Point
Autor: alvarofernandezmota-tech
Fecha: 2026-03-08

API completa con:
- CRUD Hábitos, Tareas, Eventos
- Sistema RPG Caronte
- Chat con Groq AI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import habits, tasks, events, rpg, chat
from ..config.settings import settings

app = FastAPI(
    title="Life Assistant V4 API",
    description="Sistema RPG Caronte + Gestión de Vida + Chat AI",
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

# ─── Registrar Routers ────────────────────────────────────────────────
app.include_router(habits.router)
app.include_router(tasks.router)
app.include_router(events.router)
app.include_router(rpg.router)
app.include_router(chat.router)


# ─── Endpoints Raíz ────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "app":     "Life Assistant V4",
        "version": "1.5.0",
        "status":  "operational",
        "system":  "Caronte RPG + Dados + Chat AI",
        "endpoints": {
            "habits":  "/habits",
            "tasks":   "/tasks",
            "events":  "/events",
            "rpg":     "/rpg",
            "chat":    "/chat",
            "docs":    "/docs",
            "health":  "/health",
        }
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "API funcionando correctamente",
        "routers": [
            "habits",
            "tasks",
            "events",
            "rpg",
            "chat",
        ]
    }
