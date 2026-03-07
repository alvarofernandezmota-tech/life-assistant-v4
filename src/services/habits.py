"""
habits.py - Habit Service (Business Logic Layer)
Migrado y refactorizado desde V3
"""
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..core.models import Habit, HabitLog
from ..core.utils import calc_streak
import uuid

def uid():
    return uuid.uuid4().hex[:16]

class HabitService:
    """
    Service para gestión completa de hábitos
    
    Métodos:
    - CRUD básico (crear, leer, actualizar, eliminar)
    - Marcar como completado
    - Estadísticas y rachas
    - Filtros avanzados
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ═══════════════════════════════════════════════════════════════
    # CREATE
    # ═══════════════════════════════════════════════════════════════
    
    def create_habit(
        self,
        name: str,
        description: str = "",
        frequency: str = "daily",
        time: Optional[str] = None,
        color: str = "#7c6ef5",
        group_name: str = "general"
    ) -> Habit:
        """
        Crea un nuevo hábito
        
        Args:
            name: Nombre del hábito
            description: Descripción (opcional)
            frequency: daily, weekly, custom
            time: Hora en formato HH:MM
            color: Color hex
            group_name: Grupo de organización
        
        Returns:
            Habit creado
        """
        if not name or len(name.strip()) == 0:
            raise ValueError("El nombre del hábito no puede estar vacío")
        
        # Calcular posición al final
        max_order = self.db.query(func.max(Habit.order_pos)).scalar() or 0
        
        habit = Habit(
            id=uid(),
            name=name.strip(),
            description=description.strip(),
            frequency=frequency,
            time=time,
            color=color,
            group_name=group_name,
            order_pos=max_order + 1
        )
        
        self.db.add(habit)
        self.db.commit()
        self.db.refresh(habit)
        
        return habit
    
    # ═══════════════════════════════════════════════════════════════
    # READ
    # ═══════════════════════════════════════════════════════════════
    
    def get_habit_by_id(self, habit_id: str) -> Optional[Habit]:
        """Obtiene un hábito por ID"""
        return self.db.query(Habit).filter(Habit.id == habit_id).first()
    
    def get_all_habits(self, group: Optional[str] = None) -> List[Habit]:
        """
        Obtiene todos los hábitos, opcionalmente filtrados por grupo
        
        Args:
            group: Filtrar por grupo (morning, evening, etc.)
        
        Returns:
            Lista de hábitos ordenados
        """
        query = self.db.query(Habit)
        
        if group:
            query = query.filter(Habit.group_name == group)
        
        return query.order_by(Habit.group_name, Habit.order_pos).all()
    
    def get_habits_with_status(
        self,
        target_date: Optional[date] = None,
        group: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene hábitos con estado de completado para una fecha
        
        Args:
            target_date: Fecha objetivo (default: hoy)
            group: Filtrar por grupo
        
        Returns:
            Lista de dicts con info del hábito + 'completed' boolean
        """
        if target_date is None:
            target_date = date.today()
        
        habits = self.get_all_habits(group=group)
        logs = self.db.query(HabitLog).filter(
            HabitLog.log_date == target_date
        ).all()
        
        # Mapa rápido de logs
        log_map = {log.habit_id: log.completed for log in logs}
        
        result = []
        for habit in habits:
            result.append({
                "id": habit.id,
                "name": habit.name,
                "description": habit.description,
                "time": habit.time,
                "group": habit.group_name,
                "color": habit.color,
                "frequency": habit.frequency,
                "completed": log_map.get(habit.id, False),
                "streak": calc_streak(self.db, habit.id, HabitLog)
            })
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # COMPLETION
    # ═══════════════════════════════════════════════════════════════
    
    def mark_completed(
        self,
        habit_id: str,
        target_date: Optional[date] = None,
        completed: bool = True
    ) -> bool:
        """
        Marca un hábito como completado (o no) en una fecha
        
        Args:
            habit_id: ID del hábito
            target_date: Fecha (default: hoy)
            completed: True = completado, False = desmarcar
        
        Returns:
            True si exitoso, False si hábito no existe
        """
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return False
        
        if target_date is None:
            target_date = date.today()
        
        # Buscar log existente
        log = self.db.query(HabitLog).filter(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date == target_date
            )
        ).first()
        
        if log:
            log.completed = completed
        else:
            log = HabitLog(
                id=uid(),
                habit_id=habit_id,
                log_date=target_date,
                completed=completed
            )
            self.db.add(log)
        
        self.db.commit()
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # UPDATE
    # ═══════════════════════════════════════════════════════════════
    
    def update_habit(
        self,
        habit_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        frequency: Optional[str] = None,
        time: Optional[str] = None,
        color: Optional[str] = None,
        group_name: Optional[str] = None
    ) -> Optional[Habit]:
        """
        Actualiza propiedades de un hábito (actualización parcial)
        
        Returns:
            Hábito actualizado o None si no existe
        """
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return None
        
        if name is not None:
            habit.name = name.strip()
        if description is not None:
            habit.description = description.strip()
        if frequency is not None:
            habit.frequency = frequency
        if time is not None:
            habit.time = time
        if color is not None:
            habit.color = color
        if group_name is not None:
            habit.group_name = group_name
        
        self.db.commit()
        self.db.refresh(habit)
        return habit
    
    # ═══════════════════════════════════════════════════════════════
    # DELETE
    # ═══════════════════════════════════════════════════════════════
    
    def delete_habit(self, habit_id: str) -> bool:
        """
        Elimina un hábito y todos sus logs (permanente)
        
        Returns:
            True si eliminado, False si no existe
        """
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return False
        
        # Eliminar logs primero
        self.db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id
        ).delete()
        
        # Eliminar hábito
        self.db.delete(habit)
        self.db.commit()
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # STATISTICS
    # ═══════════════════════════════════════════════════════════════
    
    def get_completion_rate(
        self,
        habit_id: str,
        start_date: date,
        end_date: date
    ) -> float:
        """
        Calcula tasa de completado de un hábito en un rango
        
        Returns:
            Porcentaje 0-100
        """
        total_days = (end_date - start_date).days + 1
        
        completed = self.db.query(func.count(HabitLog.id)).filter(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date >= start_date,
                HabitLog.log_date <= end_date,
                HabitLog.completed == True
            )
        ).scalar() or 0
        
        return (completed / total_days * 100) if total_days > 0 else 0.0