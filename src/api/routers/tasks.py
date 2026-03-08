"""
src/api/routers/tasks.py - Router para gestión de tareas
CRUD completo: crear, listar, actualizar, eliminar, completar
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from ...core.database import get_db
from ...services.tasks import TaskService
from ...config.settings import settings

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ─── Schemas ────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    due_date: Optional[str] = None  # YYYY-MM-DD
    priority: str = "medium"  # low, medium, high
    category: Optional[str] = "general"
    reminder: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    reminder: Optional[bool] = None
    completed: Optional[bool] = None


# ─── Endpoints ──────────────────────────────────────────────

@router.get("/")
def list_tasks(
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todas las tareas del usuario con filtros opcionales."""
    service = TaskService(db, settings.DEFAULT_USER_ID)
    tasks = service.list_tasks()
    
    # Aplicar filtros
    if completed is not None:
        tasks = [t for t in tasks if t.completed == completed]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "priority": t.priority,
            "category": t.category,
            "completed": t.completed,
            "reminder": t.reminder,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tasks
    ]


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Obtiene una tarea por ID."""
    service = TaskService(db, settings.DEFAULT_USER_ID)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority,
        "category": task.category,
        "completed": task.completed,
        "reminder": task.reminder,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }


@router.post("/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Crea una nueva tarea."""
    service = TaskService(db, settings.DEFAULT_USER_ID)
    
    # Convertir due_date si existe
    due_date_obj = None
    if task.due_date:
        try:
            due_date_obj = date.fromisoformat(task.due_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido (usa YYYY-MM-DD)")
    
    new_task = service.create_task(
        title=task.title,
        description=task.description,
        due_date=due_date_obj,
        priority=task.priority,
        category=task.category,
        reminder=task.reminder,
    )
    return {
        "id": new_task.id,
        "title": new_task.title,
        "message": "Tarea creada exitosamente",
    }


@router.put("/{task_id}")
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """Actualiza una tarea existente."""
    service = TaskService(db, settings.DEFAULT_USER_ID)
    
    updates = {k: v for k, v in task.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No hay cambios para aplicar")
    
    # Convertir due_date si existe
    if "due_date" in updates and updates["due_date"]:
        try:
            updates["due_date"] = date.fromisoformat(updates["due_date"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido")
    
    updated = service.update_task(task_id, **updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return {"message": "Tarea actualizada", "task_id": task_id}


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Elimina una tarea."""
    service = TaskService(db, settings.DEFAULT_USER_ID)
    success = service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"message": "Tarea eliminada", "task_id": task_id}


@router.post("/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Marca una tarea como completada."""
    service = TaskService(db, settings.DEFAULT_USER_ID)
    success = service.complete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"message": "Tarea completada", "task_id": task_id}


@router.post("/{task_id}/uncomplete")
def uncomplete_task(task_id: int, db: Session = Depends(get_db)):
    """Marca una tarea como NO completada."""
    service = TaskService(db, settings.DEFAULT_USER_ID)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    service.update_task(task_id, completed=False)
    return {"message": "Tarea marcada como pendiente", "task_id": task_id}


@router.get("/stats/today")
def get_today_stats(db: Session = Depends(get_db)):
    """Estadísticas de tareas para hoy."""
    service = TaskService(db, settings.DEFAULT_USER_ID)
    today = date.today()
    
    all_tasks = service.list_tasks()
    today_tasks = [t for t in all_tasks if t.due_date == today]
    completed_today = [t for t in today_tasks if t.completed]
    
    return {
        "total": len(today_tasks),
        "completed": len(completed_today),
        "pending": len(today_tasks) - len(completed_today),
        "percentage": round(len(completed_today) / len(today_tasks) * 100, 1) if today_tasks else 0,
    }


@router.get("/overdue")
def get_overdue_tasks(db: Session = Depends(get_db)):
    """Lista tareas vencidas (no completadas y fecha pasada)."""
    service = TaskService(db, settings.DEFAULT_USER_ID)
    today = date.today()
    
    all_tasks = service.list_tasks()
    overdue = [
        t for t in all_tasks
        if not t.completed and t.due_date and t.due_date < today
    ]
    
    return [
        {
            "id": t.id,
            "title": t.title,
            "due_date": t.due_date.isoformat(),
            "priority": t.priority,
            "days_overdue": (today - t.due_date).days,
        }
        for t in overdue
    ]
