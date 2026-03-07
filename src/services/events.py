"""
events.py - Event Service (Business Logic Layer)
Migrado y refactorizado desde V3
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..core.models import Event
from ..core.utils import expand_events
import uuid

def uid():
    return uuid.uuid4().hex[:16]

class EventService:
    """
    Service para gestión de eventos/citas del calendario
    
    Métodos:
    - CRUD básico
    - Eventos recurrentes (daily, weekly, weekdays)
    - Filtros por fecha y categoría
    - Expansión de eventos recurrentes
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ═══════════════════════════════════════════════════════════════
    # CREATE
    # ═══════════════════════════════════════════════════════════════
    
    def create_event(
        self,
        title: str,
        event_date: date,
        start_time: str,
        end_time: Optional[str] = None,
        category: str = "general",
        notes: str = "",
        recurring: str = "none"
    ) -> Event:
        """
        Crea un nuevo evento
        
        Args:
            title: Título del evento
            event_date: Fecha del evento
            start_time: Hora inicio (HH:MM)
            end_time: Hora fin (HH:MM)
            category: Categoría (work, personal, etc.)
            notes: Notas adicionales
            recurring: none, daily, weekly, weekdays
        
        Returns:
            Event creado
        """
        if not title or len(title.strip()) == 0:
            raise ValueError("El título del evento no puede estar vacío")
        
        event = Event(
            id=uid(),
            title=title.strip(),
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            category=category,
            notes=notes.strip(),
            recurring=recurring
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    # ═══════════════════════════════════════════════════════════════
    # READ
    # ═══════════════════════════════════════════════════════════════
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Obtiene un evento por ID"""
        return self.db.query(Event).filter(Event.id == event_id).first()
    
    def get_events(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> List[Event]:
        """
        Obtiene eventos con filtros opcionales
        
        Args:
            start_date: Fecha inicio del rango
            end_date: Fecha fin del rango
            category: Filtrar por categoría
        
        Returns:
            Lista de eventos ordenados por fecha y hora
        """
        query = self.db.query(Event)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    Event.event_date >= start_date,
                    Event.event_date <= end_date
                )
            )
        elif start_date:
            query = query.filter(Event.event_date >= start_date)
        elif end_date:
            query = query.filter(Event.event_date <= end_date)
        
        if category:
            query = query.filter(Event.category == category)
        
        return query.order_by(Event.event_date, Event.start_time).all()
    
    def get_events_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """
        Obtiene eventos para una fecha específica (incluyendo recurrentes)
        
        Args:
            target_date: Fecha objetivo
        
        Returns:
            Lista de eventos expandidos (incluye recurrentes)
        """
        return expand_events(self.db, target_date, Event)
    
    def get_events_today(self) -> List[Dict[str, Any]]:
        """Obtiene eventos de hoy (incluyendo recurrentes)"""
        return self.get_events_for_date(date.today())
    
    # ═══════════════════════════════════════════════════════════════
    # UPDATE
    # ═══════════════════════════════════════════════════════════════
    
    def update_event(
        self,
        event_id: str,
        title: Optional[str] = None,
        event_date: Optional[date] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        category: Optional[str] = None,
        notes: Optional[str] = None,
        recurring: Optional[str] = None
    ) -> Optional[Event]:
        """
        Actualiza propiedades de un evento (actualización parcial)
        
        Returns:
            Evento actualizado o None si no existe
        """
        event = self.get_event_by_id(event_id)
        if not event:
            return None
        
        if title is not None:
            event.title = title.strip()
        if event_date is not None:
            event.event_date = event_date
        if start_time is not None:
            event.start_time = start_time
        if end_time is not None:
            event.end_time = end_time
        if category is not None:
            event.category = category
        if notes is not None:
            event.notes = notes.strip()
        if recurring is not None:
            event.recurring = recurring
        
        self.db.commit()
        self.db.refresh(event)
        return event
    
    # ═══════════════════════════════════════════════════════════════
    # DELETE
    # ═══════════════════════════════════════════════════════════════
    
    def delete_event(self, event_id: str) -> bool:
        """
        Elimina un evento permanentemente
        
        Returns:
            True si eliminado, False si no existe
        """
        event = self.get_event_by_id(event_id)
        if not event:
            return False
        
        self.db.delete(event)
        self.db.commit()
        return True