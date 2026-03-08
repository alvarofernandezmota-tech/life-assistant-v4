"""
src/api/routers/rpg.py - Router FastAPI para el sistema RPG Caronte
Endpoints: perfil, dados, indulgencias, artefactos, malos hábitos
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date

from ...core.database import get_db
from ...services.rpg import RPGService
from ...services.caronte_dice import (
    daily_dice_roll,
    buy_indulgence_before,
    buy_indulgence_after,
    get_indulgence_cost,
)
from ...config.settings import settings

router = APIRouter(prefix="/rpg", tags=["RPG"])


# ─── Schemas ─────────────────────────────────────

class BadHabitIn(BaseModel):
    habit_type: str
    notes: Optional[str] = ""
    source: Optional[str] = "web"

class EndOfDayIn(BaseModel):
    habits_completed: bool
    tasks_completed: bool

class IndulgenceBeforeIn(BaseModel):
    habit_type: str

class IndulgenceAfterIn(BaseModel):
    habit_type: str
    wyrd_lost: int

class UseIndulgenciaIn(BaseModel):
    habit_type: str
    ind_type: str          # prevention | absolution
    wyrd_to_recover: Optional[int] = 0


# ─── Perfil ──────────────────────────────────────

@router.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    """Perfil RPG completo del usuario (nivel, XP, Wyrd, monedas, héroe)."""
    rpg = RPGService(db, settings.DEFAULT_USER_ID)
    return rpg.get_profile_dict()


# ─── Fin de día + Tirada de dados ─────────────────────

@router.post("/end-of-day")
def end_of_day(body: EndOfDayIn, db: Session = Depends(get_db)):
    """
    Cierre del día: aplica recompensas base y lanza los dados CARONTE.
    Devuelve el resultado de la tirada (combo, premios, narrativa) para el frontend.
    """
    rpg = RPGService(db, settings.DEFAULT_USER_ID)
    profile = rpg.get_or_create_profile()

    # Recompensas base del día
    summary: dict = {}
    if body.habits_completed and body.tasks_completed:
        summary["perfect_day"] = rpg.reward_perfect_day()
    elif body.tasks_completed:
        summary["all_tasks"] = rpg.reward_all_tasks_completed()

    # Tirada de dados
    dice_result = daily_dice_roll(
        db=db,
        user_id=settings.DEFAULT_USER_ID,
        level=profile.level,
        streak_days=profile.streak,
        habits_completed=body.habits_completed,
        tasks_completed=body.tasks_completed,
    )

    return {
        "rewards_base": summary,
        "dice":         dice_result,
        "profile":      rpg.get_profile_dict(),
    }


# ─── Malos hábitos ─────────────────────────────────

@router.post("/bad-habit")
def log_bad_habit(body: BadHabitIn, db: Session = Depends(get_db)):
    """Registra un mal hábito y aplica penalizaciones de Wyrd + monedas."""
    rpg = RPGService(db, settings.DEFAULT_USER_ID)
    result = rpg.log_bad_habit(
        habit_type=body.habit_type,
        source=body.source,
        notes=body.notes or "",
    )
    return result


# ─── Indulgencias ────────────────────────────────

@router.get("/indulgencia/coste")
def indulgence_cost(habit_type: str, db: Session = Depends(get_db)):
    """Calcula el coste de una indulgencia (con descuento de racha aplicado)."""
    rpg = RPGService(db, settings.DEFAULT_USER_ID)
    profile = rpg.get_or_create_profile()
    cost = get_indulgence_cost(habit_type, profile.streak)
    return {"habit_type": habit_type, "cost": cost, "streak": profile.streak}


@router.post("/indulgencia/prevencion")
def indulgence_prevention(body: IndulgenceBeforeIn, db: Session = Depends(get_db)):
    """Compra una indulgencia ANTES de cometer el mal hábito (más barato)."""
    rpg = RPGService(db, settings.DEFAULT_USER_ID)
    profile = rpg.get_or_create_profile()
    return buy_indulgence_before(db, settings.DEFAULT_USER_ID, body.habit_type, profile.streak)


@router.post("/indulgencia/absolucion")
def indulgence_absolution(body: IndulgenceAfterIn, db: Session = Depends(get_db)):
    """Compra una absolución DESPUÉS de cometer el mal hábito (50% más caro, recupera Wyrd)."""
    rpg = RPGService(db, settings.DEFAULT_USER_ID)
    profile = rpg.get_or_create_profile()
    return buy_indulgence_after(
        db, settings.DEFAULT_USER_ID, body.habit_type, profile.streak, body.wyrd_lost
    )


@router.post("/indulgencia/usar")
def use_indulgencia(body: UseIndulgenciaIn, db: Session = Depends(get_db)):
    """Consume un token de indulgencia del perfil."""
    rpg = RPGService(db, settings.DEFAULT_USER_ID)
    return rpg.use_indulgencia(body.habit_type, body.ind_type, body.wyrd_to_recover)


# ─── Artefactos ──────────────────────────────────

@router.get("/market")
def get_market(db: Session = Depends(get_db)):
    """Catálogo de artefactos disponibles en el mercado."""
    rpg = RPGService(db, settings.DEFAULT_USER_ID)
    artifacts = rpg.get_market_artifacts()
    return [
        {
            "id":          a.id,
            "name":        a.name,
            "emoji":       a.emoji,
            "rarity":      a.rarity,
            "description": a.description,
            "effect":      a.effect,
            "price":       a.price,
            "price_type":  a.price_type,
        }
        for a in artifacts
    ]


@router.get("/artifacts")
def get_user_artifacts(db: Session = Depends(get_db)):
    """Artefactos en posesión del usuario."""
    rpg = RPGService(db, settings.DEFAULT_USER_ID)
    user_artifacts = rpg.get_user_artifacts()
    return [
        {
            "id":           ua.id,
            "artifact_id":  ua.artifact_id,
            "name":         ua.artifact.name if ua.artifact else ua.artifact_id,
            "emoji":        ua.artifact.emoji if ua.artifact else "⚔️",
            "rarity":       ua.artifact.rarity if ua.artifact else "common",
            "effect":       ua.artifact.effect if ua.artifact else "",
            "uses_left":    ua.uses_left,
            "source":       ua.source,
            "equipped":     ua.equipped,
            "obtained_at":  ua.purchased_at.isoformat() if ua.purchased_at else None,
        }
        for ua in user_artifacts
    ]
