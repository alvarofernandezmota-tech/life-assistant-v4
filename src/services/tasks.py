"""
tasks.py - Task Service (Business Logic Layer)
Migrado y refactorizado desde V3
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..core.models import Task
import uuid

def uid():
    return uuid.uuid4().hex[:16]

class TaskService:
    """
    Service para gestión completa de tareas
    
    Métodos:
    - CRUD básico
    - Filtros por estado, prioridad, fecha
    - Tareas vencidas
    - Operaciones masivas
    - Estadísticas
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ═══════════════════════════════════════════════════════════════
    # CREATE
    # ═══════════════════════════════════════════════════════════════
    
    def create_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[date] = None,
        due_time: Optional[str] = None,
        priority: str = "medium",
        category: str = "general"
    ) -> Task:
        """
        Crea una nueva tarea
        
        Args:
            title: Título de la tarea (requerido)
            description: Descripción
            due_date: Fecha límite
            due_time: Hora límite (HH:MM)
            priority: low, medium, high, urgent
            category: general, work, personal, etc.
        
        Returns:
            Task creada
        """
        if not title or len(title.strip()) == 0:
            raise ValueError("El título de la tarea no puede estar vacío")
        
        max_order = self.db.query(func.max(Task.order_pos)).scalar() or 0
        
        task = Task(
            id=uid(),
            title=title.strip(),
            description=description.strip(),
            due_date=due_date,
            due_time=due_time,
            priority=priority,
            category=category,
            status="pending",
            order_pos=max_order + 1
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    # ═══════════════════════════════════════════════════════════════
    # READ
    # ═══════════════════════════════════════════════════════════════
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Obtiene una tarea por ID"""
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def get_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        due_date: Optional[date] = None,
        include_completed: bool = False
    ) -> List[Task]:
        """
        Obtiene tareas con filtros opcionales
        
        Args:
            status: pending, in_progress, done, cancelled
            priority: low, medium, high, urgent
            category: Categoría de tarea
            due_date: Filtrar por fecha límite específica
            include_completed: Incluir tareas completadas
        
        Returns:
            Lista de tareas ordenadas
        """
        query = self.db.query(Task)
        
        # Filtro de estado
        if status:
            query = query.filter(Task.status == status)
        elif not include_completed:
            query = query.filter(Task.status.in_(["pending", "in_progress"]))
        
        # Filtro de prioridad
        if priority:
            query = query.filter(Task.priority == priority)
        
        # Filtro de categoría
        if category:
            query = query.filter(Task.category == category)
        
        # Filtro de fecha
        if due_date:
            query = query.filter(Task.due_date == due_date)
        
        # Ordenar por fecha límite y prioridad
        query = query.order_by(Task.due_date, Task.priority, Task.order_pos)
        
        return query.all()
    
    def get_overdue_tasks(self) -> List[Task]:
        """
        Obtiene todas las tareas vencidas (fecha pasada, no completadas)
        
        Returns:
            Lista de tareas vencidas
        """
        today = date.today()
        return self.db.query(Task).filter(
            and_(
                Task.due_date < today,
                Task.status.in_(["pending", "in_progress"])
            )
        ).order_by(Task.due_date).all()
    
    def get_tasks_today(self) -> List[Task]:
        """Obtiene tareas de hoy (no completadas)"""
        today = date.today()
        return self.get_tasks(due_date=today, include_completed=False)
    
    # ═══════════════════════════════════════════════════════════════
    # UPDATE
    # ═══════════════════════════════════════════════════════════════
    
    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[date] = None,
        due_time: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Task]:
        """
        Actualiza propiedades de una tarea (actualización parcial)
        
        Returns:
            Tarea actualizada o None si no existe
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip()
        if due_date is not None:
            task.due_date = due_date
        if due_time is not None:
            task.due_time = due_time
        if priority is not None:
            task.priority = priority
        if status is not None:
            task.status = status
            if status == "done":
                task.completed_at = datetime.utcnow()
        if category is not None:
            task.category = category
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def mark_completed(self, task_id: str) -> Optional[Task]:
        """Marca una tarea como completada"""
        return self.update_task(task_id, status="done")
    
    def mark_in_progress(self, task_id: str) -> Optional[Task]:
        """Marca una tarea como en progreso"""
        return self.update_task(task_id, status="in_progress")
    
    # ═══════════════════════════════════════════════════════════════
    # DELETE
    # ═══════════════════════════════════════════════════════════════
    
    def delete_task(self, task_id: str) -> bool:
        """
        Elimina una tarea permanentemente
        
        Returns:
            True si eliminada, False si no existe
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        self.db.delete(task)
        self.db.commit()
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # BULK OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def postpone_task(self, task_id: str, days: int) -> Optional[Task]:
        """
        Pospone una tarea N días
        
        Args:
            task_id: ID de la tarea
            days: Días a posponer (puede ser negativo)
        
        Returns:
            Tarea actualizada o None
        """
        task = self.get_task_by_id(task_id)
        if not task or not task.due_date:
            return None
        
        task.due_date = task.due_date + timedelta(days=days)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    # ═══════════════════════════════════════════════════════════════
    # STATISTICS
    # ═══════════════════════════════════════════════════════════════
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de tareas
        
        Returns:
            Dict con contadores por estado y prioridad
        """
        today = date.today()
        
        total = self.db.query(func.count(Task.id)).scalar() or 0
        pending = self.db.query(func.count(Task.id)).filter(
            Task.status == "pending"
        ).scalar() or 0
        in_progress = self.db.query(func.count(Task.id)).filter(
            Task.status == "in_progress"
        ).scalar() or 0
        completed = self.db.query(func.count(Task.id)).filter(
            Task.status == "done"
        ).scalar() or 0
        overdue = self.db.query(func.count(Task.id)).filter(
            and_(
                Task.due_date < today,
                Task.status.in_(["pending", "in_progress"])
            )
        ).scalar() or 0
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "overdue": overdue
        }