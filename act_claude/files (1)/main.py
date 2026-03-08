"""
src/api/main.py - FastAPI application principal
Life Assistant V4 — La Barca de Caronte
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy.orm import Session
from datetime import date

from ..config.settings import settings
from ..core.database import get_db, init_db
from ..services.habits import HabitService
from ..services.tasks import TaskService
from ..services.events import EventService
from ..services.rpg import RPGService
from .routers import rpg as rpg_router

# ─── App ────────────────────────────────────────────────────

app = FastAPI(
    title="Life Assistant V4 — La Barca de Caronte",
    description="Sistema de productividad gamificado con mecánicas RPG",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(rpg_router.router)

# Static / Templates
BASE_DIR = Path(__file__).parent.parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ─── Startup ────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()


# ─── Dashboard ──────────────────────────────────────────────

@app.get("/")
def root(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    habits  = HabitService(db).get_habits_with_status(today)
    tasks   = TaskService(db).get_tasks_today()
    events  = EventService(db).get_events_for_date(today)
    profile = RPGService(db, settings.DEFAULT_USER_ID).get_profile_dict()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "habits":  habits,
        "tasks":   tasks,
        "events":  events,
        "profile": profile,
        "today":   today.isoformat(),
    })


@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    """API endpoint — resumen completo del día."""
    today   = date.today()
    habits  = HabitService(db).get_habits_with_status(today)
    tasks   = TaskService(db).get_tasks_today()
    overdue = TaskService(db).get_overdue_tasks()
    events  = EventService(db).get_events_for_date(today)
    profile = RPGService(db, settings.DEFAULT_USER_ID).get_profile_dict()

    habits_done    = all(h["completed"] for h in habits) if habits else False
    tasks_done     = len(tasks) > 0 and all(t.status == "done" for t in tasks)

    return {
        "date":             today.isoformat(),
        "habits":           habits,
        "habits_done":      habits_done,
        "tasks":            [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority} for t in tasks],
        "tasks_done":       tasks_done,
        "overdue_count":    len(overdue),
        "events":           events,
        "profile":          profile,
    }


# ─── Hábitos ────────────────────────────────────────────────

@app.get("/habits")
def get_habits(db: Session = Depends(get_db)):
    return HabitService(db).get_habits_with_status()


@app.post("/habits", status_code=201)
def create_habit(data: dict, db: Session = Depends(get_db)):
    svc = HabitService(db)
    habit = svc.create_habit(
        name=data["name"],
        description=data.get("description", ""),
        frequency=data.get("frequency", "daily"),
        time=data.get("time"),
        color=data.get("color", "#7c6ef5"),
        group_name=data.get("group_name", "general"),
    )
    from ..core.utils import to_dict
    return to_dict(habit)


@app.patch("/habits/{habit_id}/complete")
def complete_habit(habit_id: str, db: Session = Depends(get_db)):
    svc = HabitService(db)
    ok = svc.mark_completed(habit_id)
    if not ok:
        raise HTTPException(404, "Hábito no encontrado")
    # Recompensa RPG
    RPGService(db, settings.DEFAULT_USER_ID).reward_habit_completed(habit_id)
    return {"success": True}


@app.delete("/habits/{habit_id}")
def delete_habit(habit_id: str, db: Session = Depends(get_db)):
    ok = HabitService(db).delete_habit(habit_id)
    if not ok:
        raise HTTPException(404, "Hábito no encontrado")
    return {"success": True}


# ─── Tareas ─────────────────────────────────────────────────

@app.get("/tasks")
def get_tasks(status: str = None, priority: str = None, db: Session = Depends(get_db)):
    return TaskService(db).get_tasks(status=status, priority=priority, include_completed=bool(status))


@app.post("/tasks", status_code=201)
def create_task(data: dict, db: Session = Depends(get_db)):
    from datetime import date as dt
    due = dt.fromisoformat(data["due_date"]) if data.get("due_date") else None
    task = TaskService(db).create_task(
        title=data["title"],
        description=data.get("description", ""),
        due_date=due,
        priority=data.get("priority", "medium"),
        category=data.get("category", "general"),
    )
    from ..core.utils import to_dict
    return to_dict(task)


@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: str, db: Session = Depends(get_db)):
    task = TaskService(db).mark_completed(task_id)
    if not task:
        raise HTTPException(404, "Tarea no encontrada")
    RPGService(db, settings.DEFAULT_USER_ID).add_xp(20, f"Tarea completada: {task.title}")
    return {"success": True}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    ok = TaskService(db).delete_task(task_id)
    if not ok:
        raise HTTPException(404, "Tarea no encontrada")
    return {"success": True}


# ─── Eventos ────────────────────────────────────────────────

@app.get("/events")
def get_events(day: str = None, db: Session = Depends(get_db)):
    svc = EventService(db)
    if day:
        return svc.get_events_for_date(date.fromisoformat(day))
    return svc.get_events_today()


@app.post("/events", status_code=201)
def create_event(data: dict, db: Session = Depends(get_db)):
    event = EventService(db).create_event(
        title=data["title"],
        event_date=date.fromisoformat(data["date"]),
        start_time=data["start_time"],
        end_time=data.get("end_time"),
        category=data.get("category", "general"),
        notes=data.get("notes", ""),
        recurring=data.get("recurring", "none"),
    )
    from ..core.utils import to_dict
    return to_dict(event)


@app.delete("/events/{event_id}")
def delete_event(event_id: str, db: Session = Depends(get_db)):
    ok = EventService(db).delete_event(event_id)
    if not ok:
        raise HTTPException(404, "Evento no encontrado")
    return {"success": True}


# ─── Run ────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
