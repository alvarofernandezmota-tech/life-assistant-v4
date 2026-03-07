"""
models.py - Modelos SQLAlchemy (Core: Hábitos, Tareas, Eventos, Diario)
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, Date, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base

def uid():
    """Genera ID único de 16 caracteres"""
    return uuid.uuid4().hex[:16]

# ============================================
# MODELOS CORE - HÁBITOS, TAREAS, EVENTOS
# ============================================

class Habit(Base):
    """Hábitos del usuario"""
    __tablename__ = "habits"
    
    id          = Column(String, primary_key=True, default=uid)
    name        = Column(String, nullable=False)
    description = Column(Text, default="")
    frequency   = Column(String, default="daily")  # daily, weekly, custom
    time        = Column(String, nullable=True)    # HH:MM formato
    color       = Column(String, default="#7c6ef5")
    group_name  = Column(String, default="general")
    order_pos   = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base):
    """Registro de completado de hábitos"""
    __tablename__ = "habit_logs"
    
    id        = Column(String, primary_key=True, default=uid)
    habit_id  = Column(String, ForeignKey("habits.id"), nullable=False)
    log_date  = Column(Date, nullable=False)
    completed = Column(Boolean, default=False)
    
    # Relaciones
    habit = relationship("Habit", back_populates="logs")

class Task(Base):
    """Tareas del usuario"""
    __tablename__ = "tasks"
    
    id           = Column(String, primary_key=True, default=uid)
    title        = Column(String, nullable=False)
    description  = Column(Text, default="")
    due_date     = Column(Date, nullable=True)
    due_time     = Column(String, nullable=True)
    priority     = Column(String, default="medium")  # low, medium, high
    status       = Column(String, default="pending") # pending, in_progress, done, cancelled
    category     = Column(String, default="general")
    order_pos    = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    """Eventos/Citas del calendario"""
    __tablename__ = "events"
    
    id         = Column(String, primary_key=True, default=uid)
    title      = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    start_time = Column(String, nullable=False)
    end_time   = Column(String, nullable=True)
    category   = Column(String, default="general")
    notes      = Column(Text, default="")
    recurring  = Column(String, default="none")  # none, daily, weekly, weekdays
    created_at = Column(DateTime, default=datetime.utcnow)

class Diary(Base):
    """Entradas del diario personal"""
    __tablename__ = "diary"
    
    id         = Column(String, primary_key=True, default=uid)
    entry_date = Column(Date, nullable=False, unique=True)
    content    = Column(Text, nullable=False)
    tags       = Column(Text, default="[]")  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================
# MODELOS SECUNDARIOS
# ============================================

class Mood(Base):
    """Estado de ánimo y energía diaria"""
    __tablename__ = "moods"
    
    id         = Column(String, primary_key=True, default=uid)
    mood_date  = Column(Date, nullable=False, unique=True)
    mood_level = Column(Integer, nullable=False)  # 1-5
    energy     = Column(Integer, nullable=False)  # 1-5
    notes      = Column(Text, default="")

class Goal(Base):
    """Metas a largo plazo"""
    __tablename__ = "goals"
    
    id          = Column(String, primary_key=True, default=uid)
    title       = Column(String, nullable=False)
    description = Column(Text, default="")
    deadline    = Column(Date, nullable=True)
    progress    = Column(Integer, default=0)  # 0-100
    status      = Column(String, default="active")  # active, completed, cancelled
    created_at  = Column(DateTime, default=datetime.utcnow)

class Reminder(Base):
    """Recordatorios programados"""
    __tablename__ = "reminders"
    
    id           = Column(String, primary_key=True, default=uid)
    title        = Column(String, nullable=False)
    message      = Column(Text, default="")
    remind_time  = Column(String, nullable=False)  # HH:MM
    days         = Column(String, default="1,2,3,4,5,6,7")  # Días de la semana
    active       = Column(Boolean, default=True)
    last_sent    = Column(Date, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

class ChatMsg(Base):
    """Historial de chat con IA"""
    __tablename__ = "chat"
    
    id         = Column(String, primary_key=True, default=uid)
    role       = Column(String)  # user, assistant, system
    content    = Column(Text)
    source     = Column(String, default="web")  # web, telegram
    created_at = Column(DateTime, default=datetime.utcnow)