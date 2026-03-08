"""
src/api/routers/chat.py - Router para chat con Caronte (Groq AI)
Integración con Groq para asistente conversacional
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os
import httpx

from ...core.database import get_db
from ...core.models import ChatMsg
from ...config.settings import settings

router = APIRouter(prefix="/chat", tags=["Chat"])

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # Modelo rápido de Groq


# ─── Schemas ────────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str
    include_context: bool = True  # Incluir contexto de hábitos/tareas


# ─── System Prompt Caronte ───────────────────────────────

SYSTEM_PROMPT = """
Eres Caronte, el barquero del río Estigia en la mitología griega.
Tu trabajo es ayudar al usuario a gestionar su vida como si transportaras almas al otro lado del río.

Personalidad:
- Serio pero sabio y comprensivo
- Usas metáforas relacionadas con el río y el viaje al inframundo
- Motivas al usuario a completar sus tareas ("almas que deben cruzar")
- Cuando el usuario falla, recuerdas que todos los mortales tropiezan

Contexto del sistema:
- El usuario tiene hábitos diarios que debe completar
- Tiene tareas con fechas límite
- Tiene eventos/citas en su calendario
- Gana XP y monedas (obolos, dracmas) al completar objetivos
- Pierde Wyrd (vida/destino) con malos hábitos
- Cada noche tira dados para ganar recompensas

Responde de forma concisa (máximo 3-4 líneas), útil y con un toque místico.
"""


# ─── Helpers ──────────────────────────────────────────────

def get_user_context(db: Session, user_id: int) -> str:
    """
    Genera un resumen del estado actual del usuario para dar contexto a Caronte.
    """
    from ...services.habits import HabitService
    from ...services.tasks import TaskService
    from ...services.rpg import RPGService
    from datetime import date
    
    habit_service = HabitService(db, user_id)
    task_service = TaskService(db, user_id)
    rpg_service = RPGService(db, user_id)
    
    # Perfil RPG
    profile = rpg_service.get_profile_dict()
    
    # Hábitos de hoy
    habits = habit_service.list_habits()
    today = date.today()
    completed_habits = sum(1 for h in habits if habit_service.is_completed_on_date(h.id, today))
    
    # Tareas pendientes
    tasks = task_service.list_tasks()
    pending_tasks = [t for t in tasks if not t.completed]
    overdue_tasks = [t for t in pending_tasks if t.due_date and t.due_date < today]
    
    context = f"""
Estado del usuario:
- Nivel: {profile['level']} ({profile['hero']['name']})
- Wyrd: {profile['wyrd']}/100 ({profile['wyrd_state']['name']})
- Monedas: {profile['obolos']} óbolos, {profile['dracmas']} dracmas
- Racha: {profile['streak']} días
- Hábitos hoy: {completed_habits}/{len(habits)} completados
- Tareas pendientes: {len(pending_tasks)} (vencidas: {len(overdue_tasks)})
"""
    return context.strip()


async def call_groq_api(messages: List[dict]) -> str:
    """
    Llama a la API de Groq y devuelve la respuesta.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY no configurada en variables de entorno"
        )
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GROQ_API_URL, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error llamando a Groq API: {str(e)}")


# ─── Endpoints ──────────────────────────────────────────────

@router.post("/message")
async def send_message(body: ChatMessage, db: Session = Depends(get_db)):
    """
    Envía un mensaje a Caronte y recibe respuesta.
    """
    user_id = settings.DEFAULT_USER_ID
    
    # Construir mensajes para Groq
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    # Añadir contexto del usuario si se solicita
    if body.include_context:
        context = get_user_context(db, user_id)
        messages.append({
            "role": "system",
            "content": f"Contexto actual del usuario:\n{context}"
        })
    
    # Añadir mensaje del usuario
    messages.append({
        "role": "user",
        "content": body.message
    })
    
    # Llamar a Groq
    response = await call_groq_api(messages)
    
    # Guardar mensaje en DB
    user_msg = ChatMsg(
        user_id=user_id,
        role="user",
        content=body.message,
    )
    caronte_msg = ChatMsg(
        user_id=user_id,
        role="assistant",
        content=response,
    )
    db.add(user_msg)
    db.add(caronte_msg)
    db.commit()
    
    return {
        "message": body.message,
        "response": response,
        "context_included": body.include_context,
    }


@router.get("/history")
def get_chat_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de conversaciones con Caronte.
    """
    user_id = settings.DEFAULT_USER_ID
    
    messages = db.query(ChatMsg).filter(
        ChatMsg.user_id == user_id
    ).order_by(ChatMsg.created_at.desc()).limit(limit).all()
    
    # Invertir para orden cronológico
    messages.reverse()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        }
        for msg in messages
    ]


@router.delete("/history")
def clear_chat_history(db: Session = Depends(get_db)):
    """
    Borra todo el historial de chat del usuario.
    """
    user_id = settings.DEFAULT_USER_ID
    
    deleted = db.query(ChatMsg).filter(
        ChatMsg.user_id == user_id
    ).delete()
    db.commit()
    
    return {
        "message": f"{deleted} mensajes eliminados",
        "deleted_count": deleted,
    }


@router.get("/status")
def get_chat_status():
    """
    Verifica si la API de Groq está configurada.
    """
    api_key = os.getenv("GROQ_API_KEY")
    return {
        "groq_configured": bool(api_key),
        "model": GROQ_MODEL,
        "status": "ready" if api_key else "not_configured",
        "message": "Groq API lista para usar" if api_key else "Configura GROQ_API_KEY en .env",
    }
