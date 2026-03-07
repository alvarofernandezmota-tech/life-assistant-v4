"""
utils.py - Funciones auxiliares compartidas
"""
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Any

def to_dict(obj) -> Dict[str, Any]:
    """Convierte modelo SQLAlchemy a diccionario"""
    d = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, (date, datetime)):
            val = val.isoformat()
        d[col.name] = val
    return d

def week_range(ref: str) -> List[date]:
    """Retorna lista de 7 días (Lunes-Domingo) de la semana de una fecha"""
    d = date.fromisoformat(ref)
    monday = d - timedelta(days=d.weekday())
    return [(monday + timedelta(days=i)) for i in range(7)]

def expand_events(db: Session, target: date, Event) -> List[Dict[str, Any]]:
    """
    Expande eventos recurrentes para una fecha específica
    
    Args:
        db: Sesión de base de datos
        target: Fecha objetivo
        Event: Modelo Event (pasado para evitar import circular)
    
    Returns:
        Lista de eventos aplicables para la fecha
    """
    rows = db.query(Event).all()
    result = []
    seen = set()
    
    for e in rows:
        ok = False
        
        # Evento en fecha específica
        if e.event_date == target:
            ok = True
        
        # Evento diario
        elif e.recurring == "daily" and e.event_date <= target:
            ok = True
        
        # Evento semanal (mismo día de la semana)
        elif e.recurring == "weekly" and e.event_date <= target and e.event_date.weekday() == target.weekday():
            ok = True
        
        # Evento entre semana (Lunes-Viernes)
        elif e.recurring == "weekdays" and e.event_date <= target and target.weekday() < 5:
            ok = True
        
        if ok:
            # Evitar duplicados
            key = (e.title, e.start_time)
            if key not in seen:
                seen.add(key)
                event_dict = to_dict(e)
                event_dict["date"] = target.isoformat()
                result.append(event_dict)
    
    return sorted(result, key=lambda x: x["start_time"])

def calc_streak(db: Session, habit_id: str, HabitLog) -> int:
    """
    Calcula la racha actual de un hábito
    
    Args:
        db: Sesión de base de datos
        habit_id: ID del hábito
        HabitLog: Modelo HabitLog (pasado para evitar import circular)
    
    Returns:
        Número de días consecutivos completado
    """
    today = date.today()
    streak = 0
    
    for i in range(365):
        check_date = today - timedelta(days=i)
        log = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.log_date == check_date,
            HabitLog.completed == True
        ).first()
        
        if log:
            streak += 1
        else:
            break
    
    return streak

def format_weekday(d: date, lang: str = "es") -> str:
    """Formatea día de la semana en español"""
    if lang == "es":
        weekdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return weekdays[d.weekday()]
    return d.strftime("%A")

def get_daily_summary(db: Session, Habit, HabitLog, Event, Task, Mood, Goal) -> Dict[str, Any]:
    """
    Genera resumen completo del día actual
    
    Args:
        db: Sesión de base de datos
        Modelos pasados para evitar imports circulares
    
    Returns:
        Diccionario con resumen del día
    """
    from sqlalchemy import func
    
    today = date.today()
    
    # Hábitos
    habits = db.query(Habit).all()
    logs = db.query(HabitLog).filter(HabitLog.log_date == today).all()
    
    done_habits = [h.name for h in habits if any(l.habit_id == h.id and l.completed for l in logs)]
    pending_habits = [h.name for h in habits if not any(l.habit_id == h.id and l.completed for l in logs)]
    
    # Eventos
    schedule = expand_events(db, today, Event)
    
    # Tareas
    tasks_today = db.query(Task).filter(
        Task.due_date == today,
        Task.status.in_(["pending", "in_progress"])
    ).all()
    
    tasks_overdue = db.query(func.count(Task.id)).filter(
        Task.due_date < today,
        Task.status.in_(["pending", "in_progress"])
    ).scalar()
    
    # Estado de ánimo
    mood = db.query(Mood).filter(Mood.mood_date == today).first()
    
    # Metas activas
    goals = db.query(Goal).filter(Goal.status == "active").all()
    
    return {
        "date": today.isoformat(),
        "habits_done": done_habits,
        "habits_pending": pending_habits,
        "schedule": [f"{s['start_time']} — {s['title']}" for s in schedule],
        "tasks_today": [t.title for t in tasks_today],
        "tasks_overdue": tasks_overdue,
        "mood": mood.mood_level if mood else None,
        "energy": mood.energy if mood else None,
        "goals": [f"{g.title} ({g.progress}%)" for g in goals],
    }

def format_daily_summary_text(summary: Dict[str, Any]) -> str:
    """
    Formatea resumen del día para Telegram (Markdown)
    
    Args:
        summary: Diccionario del resumen (de get_daily_summary)
    
    Returns:
        Texto formateado en Markdown
    """
    today = date.today()
    weekday = format_weekday(today)
    
    lines = [f"📋 *Resumen del día — {weekday} {today.strftime('%d/%m')}*\n"]
    
    if summary["habits_done"]:
        lines.append("✅ *Hábitos completados:*\n" + "\n".join(f"  · {h}" for h in summary["habits_done"]))
    
    if summary["habits_pending"]:
        lines.append("⏳ *Hábitos pendientes:*\n" + "\n".join(f"  · {h}" for h in summary["habits_pending"]))
    
    if summary["schedule"]:
        lines.append("📅 *Agenda hoy:*\n" + "\n".join(f"  · {s}" for s in summary["schedule"]))
    
    if summary["tasks_today"]:
        lines.append("☑️ *Tareas de hoy:*\n" + "\n".join(f"  · {t}" for t in summary["tasks_today"]))
    
    if summary["tasks_overdue"]:
        lines.append(f"🔴 *Tareas vencidas: {summary['tasks_overdue']}*")
    
    if summary["mood"]:
        mood_emoji = ["", "😞", "😕", "😐", "🙂", "😄"][summary["mood"]]
        lines.append(f"{mood_emoji} *Estado de ánimo:* {summary['mood']}/5  ⚡ Energía: {summary['energy']}/5")
    
    if summary["goals"]:
        lines.append("🎯 *Metas activas:*\n" + "\n".join(f"  · {g}" for g in summary["goals"]))
    
    return "\n\n".join(lines)