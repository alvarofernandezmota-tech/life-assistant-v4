"""
src/api/routers/habits.py - Router para gestión de hábitos
CRUD completo: crear, listar, actualizar, eliminar, completar
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from ...core.database import get_db
from ...services.habits import HabitService
from ...config.settings import settings

router = APIRouter(prefix="/habits", tags=["Habits"])


# ─── Schemas ────────────────────────────────────────────────

class HabitCreate(BaseModel):
    name: str
    frequency: str = "daily"  # daily, weekly, custom
    time_of_day: Optional[str] = None
    reminder: bool = False
    icon: Optional[str] = "⭐"
    active: bool = True

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    frequency: Optional[str] = None
    time_of_day: Optional[str] = None
    reminder: Optional[bool] = None
    icon: Optional[str] = None
    active: Optional[bool] = None

class HabitComplete(BaseModel):
    date: str  # YYYY-MM-DD
    notes: Optional[str] = ""


# ─── Endpoints ──────────────────────────────────────────────

@router.get("/")
def list_habits(db: Session = Depends(get_db)):
    """Lista todos los hábitos activos del usuario."""
    service = HabitService(db, settings.DEFAULT_USER_ID)
    habits = service.list_habits()
    return [
        {
            "id": h.id,
            "name": h.name,
            "frequency": h.frequency,
            "time_of_day": h.time_of_day,
            "reminder": h.reminder,
            "icon": h.icon,
            "streak": h.streak,
            "active": h.active,
            "created_at": h.created_at.isoformat() if h.created_at else None,
        }
        for h in habits
    ]


@router.get("/{habit_id}")
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    """Obtiene un hábito por ID."""
    service = HabitService(db, settings.DEFAULT_USER_ID)
    habit = service.get_habit(habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    return {
        "id": habit.id,
        "name": habit.name,
        "frequency": habit.frequency,
        "time_of_day": habit.time_of_day,
        "reminder": habit.reminder,
        "icon": habit.icon,
        "streak": habit.streak,
        "active": habit.active,
        "created_at": habit.created_at.isoformat() if habit.created_at else None,
    }


@router.post("/")
def create_habit(habit: HabitCreate, db: Session = Depends(get_db)):
    """Crea un nuevo hábito."""
    service = HabitService(db, settings.DEFAULT_USER_ID)
    new_habit = service.create_habit(
        name=habit.name,
        frequency=habit.frequency,
        time_of_day=habit.time_of_day,
        reminder=habit.reminder,
        icon=habit.icon,
    )
    return {
        "id": new_habit.id,
        "name": new_habit.name,
        "message": "Hábito creado exitosamente",
    }


@router.put("/{habit_id}")
def update_habit(habit_id: int, habit: HabitUpdate, db: Session = Depends(get_db)):
    """Actualiza un hábito existente."""
    service = HabitService(db, settings.DEFAULT_USER_ID)
    
    updates = {k: v for k, v in habit.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No hay cambios para aplicar")
    
    updated = service.update_habit(habit_id, **updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    
    return {"message": "Hábito actualizado", "habit_id": habit_id}


@router.delete("/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    """Elimina un hábito (soft delete)."""
    service = HabitService(db, settings.DEFAULT_USER_ID)
    success = service.delete_habit(habit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    return {"message": "Hábito eliminado", "habit_id": habit_id}


@router.post("/{habit_id}/complete")
def complete_habit(habit_id: int, body: HabitComplete, db: Session = Depends(get_db)):
    """Marca un hábito como completado para una fecha específica."""
    service = HabitService(db, settings.DEFAULT_USER_ID)
    
    # Convertir string a date
    try:
        completion_date = date.fromisoformat(body.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (usa YYYY-MM-DD)")
    
    log = service.complete_habit(habit_id, completion_date, body.notes)
    if not log:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    
    return {
        "message": "Hábito completado",
        "habit_id": habit_id,
        "date": body.date,
        "log_id": log.id,
    }


@router.get("/{habit_id}/logs")
def get_habit_logs(habit_id: int, db: Session = Depends(get_db)):
    """Obtiene el historial de completados de un hábito."""
    service = HabitService(db, settings.DEFAULT_USER_ID)
    logs = service.get_habit_logs(habit_id)
    return [
        {
            "id": log.id,
            "habit_id": log.habit_id,
            "completed": log.completed,
            "notes": log.notes,
            "date": log.date.isoformat() if log.date else None,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.get("/stats/today")
def get_today_stats(db: Session = Depends(get_db)):
    """Estadísticas de hábitos para hoy."""
    service = HabitService(db, settings.DEFAULT_USER_ID)
    today = date.today()
    
    habits = service.list_habits()
    completed_today = [h for h in habits if service.is_completed_on_date(h.id, today)]
    
    return {
        "total": len(habits),
        "completed": len(completed_today),
        "pending": len(habits) - len(completed_today),
        "percentage": round(len(completed_today) / len(habits) * 100, 1) if habits else 0,
    }
