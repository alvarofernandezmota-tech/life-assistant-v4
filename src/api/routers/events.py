"""
src/api/routers/events.py - Router para gestión de eventos/citas
CRUD completo: crear, listar, actualizar, eliminar
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from ...core.database import get_db
from ...services.events import EventService
from ...config.settings import settings

router = APIRouter(prefix="/events", tags=["Events"])


# ─── Schemas ────────────────────────────────────────────────

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    start_date: str  # YYYY-MM-DD
    end_date: Optional[str] = None  # YYYY-MM-DD
    start_time: Optional[str] = None  # HH:MM
    end_time: Optional[str] = None  # HH:MM
    location: Optional[str] = ""
    category: Optional[str] = "general"
    reminder: bool = False
    all_day: bool = False

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    reminder: Optional[bool] = None
    all_day: Optional[bool] = None


# ─── Endpoints ──────────────────────────────────────────────

@router.get("/")
def list_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos los eventos del usuario con filtros opcionales."""
    service = EventService(db, settings.DEFAULT_USER_ID)
    events = service.list_events()
    
    # Aplicar filtros
    if start_date:
        try:
            start = date.fromisoformat(start_date)
            events = [e for e in events if e.start_date >= start]
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato start_date inválido")
    
    if end_date:
        try:
            end = date.fromisoformat(end_date)
            events = [e for e in events if e.start_date <= end]
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato end_date inválido")
    
    if category:
        events = [e for e in events if e.category == category]
    
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "start_date": e.start_date.isoformat() if e.start_date else None,
            "end_date": e.end_date.isoformat() if e.end_date else None,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "location": e.location,
            "category": e.category,
            "reminder": e.reminder,
            "all_day": e.all_day,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]


@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Obtiene un evento por ID."""
    service = EventService(db, settings.DEFAULT_USER_ID)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "start_date": event.start_date.isoformat() if event.start_date else None,
        "end_date": event.end_date.isoformat() if event.end_date else None,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "location": event.location,
        "category": event.category,
        "reminder": event.reminder,
        "all_day": event.all_day,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


@router.post("/")
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Crea un nuevo evento."""
    service = EventService(db, settings.DEFAULT_USER_ID)
    
    # Convertir fechas
    try:
        start_date_obj = date.fromisoformat(event.start_date)
        end_date_obj = date.fromisoformat(event.end_date) if event.end_date else start_date_obj
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (usa YYYY-MM-DD)")
    
    new_event = service.create_event(
        title=event.title,
        description=event.description,
        start_date=start_date_obj,
        end_date=end_date_obj,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        category=event.category,
        reminder=event.reminder,
        all_day=event.all_day,
    )
    return {
        "id": new_event.id,
        "title": new_event.title,
        "message": "Evento creado exitosamente",
    }


@router.put("/{event_id}")
def update_event(event_id: int, event: EventUpdate, db: Session = Depends(get_db)):
    """Actualiza un evento existente."""
    service = EventService(db, settings.DEFAULT_USER_ID)
    
    updates = {k: v for k, v in event.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No hay cambios para aplicar")
    
    # Convertir fechas si existen
    try:
        if "start_date" in updates:
            updates["start_date"] = date.fromisoformat(updates["start_date"])
        if "end_date" in updates:
            updates["end_date"] = date.fromisoformat(updates["end_date"])
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido")
    
    updated = service.update_event(event_id, **updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    return {"message": "Evento actualizado", "event_id": event_id}


@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Elimina un evento."""
    service = EventService(db, settings.DEFAULT_USER_ID)
    success = service.delete_event(event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return {"message": "Evento eliminado", "event_id": event_id}


@router.get("/calendar/month")
def get_month_calendar(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Obtiene todos los eventos de un mes específico."""
    service = EventService(db, settings.DEFAULT_USER_ID)
    
    # Validar mes
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Mes debe estar entre 1 y 12")
    
    # Calcular rango del mes
    from calendar import monthrange
    start = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end = date(year, month, last_day)
    
    all_events = service.list_events()
    month_events = [
        e for e in all_events
        if e.start_date and start <= e.start_date <= end
    ]
    
    return {
        "year": year,
        "month": month,
        "total_events": len(month_events),
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "start_date": e.start_date.isoformat(),
                "start_time": e.start_time,
                "category": e.category,
                "all_day": e.all_day,
            }
            for e in month_events
        ]
    }


@router.get("/upcoming")
def get_upcoming_events(days: int = 7, db: Session = Depends(get_db)):
    """Obtiene eventos próximos (por defecto 7 días)."""
    service = EventService(db, settings.DEFAULT_USER_ID)
    today = date.today()
    from datetime import timedelta
    future = today + timedelta(days=days)
    
    all_events = service.list_events()
    upcoming = [
        e for e in all_events
        if e.start_date and today <= e.start_date <= future
    ]
    
    # Ordenar por fecha
    upcoming.sort(key=lambda e: e.start_date)
    
    return [
        {
            "id": e.id,
            "title": e.title,
            "start_date": e.start_date.isoformat(),
            "start_time": e.start_time,
            "location": e.location,
            "days_until": (e.start_date - today).days,
        }
        for e in upcoming
    ]
