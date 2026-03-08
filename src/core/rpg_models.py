"""
rpg_models.py - Modelos del sistema de gamificación RPG (Caronte)
Actualizado 2026-03-07:
  - Añadida columna `indulgencias` en UserProfile
  - Añadidos modelos IndulgenciaLog y DiceRollLog
  - Unificado BadHabitLog (eliminada BadHabitLogExtra redundante)
  - Añadida columna `rarity` y `source` en Artifact / UserArtifact
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base

def uid():
    return uuid.uuid4().hex[:16]


# ═══════════════════════════════════════════════════════════
# PERFIL PRINCIPAL
# ═══════════════════════════════════════════════════════════

class UserProfile(Base):
    __tablename__ = "user_profile"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, unique=True, nullable=False)
    level         = Column(Integer, default=1)
    xp            = Column(Integer, default=0)
    wyrd          = Column(Integer, default=100)
    obolos        = Column(Integer, default=0)
    dracmas       = Column(Integer, default=0)
    tetradracmas  = Column(Integer, default=0)
    decadracmas   = Column(Integer, default=0)
    indulgencias  = Column(Integer, default=0)      # ← NUEVO: tokens para cubrir malos hábitos
    hero          = Column(String, default="Alma Errante")
    streak        = Column(Integer, default=0)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at    = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
# LOGS DE ECONOMÍA
# ═══════════════════════════════════════════════════════════

class XPLog(Base):
    __tablename__ = "xp_log"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    amount     = Column(Integer, nullable=False)
    reason     = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class WyrdLog(Base):
    __tablename__ = "wyrd_log"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, nullable=False)
    amount      = Column(Integer, nullable=False)
    reason      = Column(String, default="")
    wyrd_before = Column(Integer, nullable=False)
    wyrd_after  = Column(Integer, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)


class CoinsLog(Base):
    __tablename__ = "coins_log"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    coin_type  = Column(String, nullable=False)
    amount     = Column(Integer, nullable=False)
    reason     = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
# ARTEFACTOS
# ═══════════════════════════════════════════════════════════

class Artifact(Base):
    __tablename__ = "artifacts"

    id           = Column(String, primary_key=True, default=uid)
    name         = Column(String, nullable=False)
    hero_origin  = Column(String, default="")
    emoji        = Column(String, default="⚔️")
    description  = Column(Text, default="")
    effect       = Column(Text, default="")
    effect_type  = Column(String, default="")
    effect_value = Column(Integer, default=1)
    rarity       = Column(String, default="common")   # common | rare | legendary
    price_type   = Column(String, default="tetradracma")
    price        = Column(Integer, nullable=False)
    active       = Column(Boolean, default=True)

    user_artifacts = relationship("UserArtifact", back_populates="artifact")


class UserArtifact(Base):
    __tablename__ = "user_artifacts"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, nullable=False)
    artifact_id  = Column(String, ForeignKey("artifacts.id"), nullable=False)
    equipped     = Column(Boolean, default=False)
    uses_left    = Column(Integer, default=1)
    source       = Column(String, default="market")   # market | dice_combo
    purchased_at = Column(DateTime, default=datetime.utcnow)
    used_at      = Column(DateTime, nullable=True)

    artifact = relationship("Artifact", back_populates="user_artifacts")


# ═══════════════════════════════════════════════════════════
# SISTEMA DE DADOS CARONTE — NUEVO
# ═══════════════════════════════════════════════════════════

class DiceRollLog(Base):
    """Registro de tiradas diarias de dados al final del día."""
    __tablename__ = "dice_roll_log"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, nullable=False)
    dice_count   = Column(Integer, nullable=False)
    die_tier     = Column(Integer, nullable=False)
    roll_result  = Column(Text, nullable=False)     # JSON ["⚙️","⚙️","🪙"]
    combo        = Column(String, nullable=False)
    rewards_json = Column(Text, default="{}")       # JSON {"obolos":4,"xp":20}
    artifact_id  = Column(String, nullable=True)
    streak_mult  = Column(String, default="1.0")
    created_at   = Column(DateTime, default=datetime.utcnow)


class IndulgenciaLog(Base):
    """Registro de indulgencias compradas para cubrir malos hábitos."""
    __tablename__ = "indulgencias_log"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, nullable=False)
    habit_type     = Column(String, nullable=False)
    type           = Column(String, nullable=False)   # prevention | absolution
    cost_json      = Column(Text, default="{}")       # JSON {"dracmas":4}
    wyrd_recovered = Column(Integer, default=0)
    created_at     = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
# MALOS HÁBITOS (unificado — eliminada BadHabitLogExtra)
# ═══════════════════════════════════════════════════════════

class BadHabitLog(Base):
    """
    Registro unificado de malos hábitos.
    source: 'auto' (motor RPG), 'web' (interfaz web), 'telegram' (bot)
    """
    __tablename__ = "bad_habits_log"

    id                     = Column(Integer, primary_key=True, autoincrement=True)
    user_id                = Column(Integer, nullable=False, default=1)
    habit_type             = Column(String, nullable=False)
    wyrd_lost              = Column(Integer, nullable=False, default=0)
    coin_penalty_json      = Column(Text, default="{}")   # JSON {"dracmas":3}
    covered_by_indulgencia = Column(Boolean, default=False)
    notes                  = Column(Text, default="")
    source                 = Column(String, default="auto")
    created_at             = Column(DateTime, default=datetime.utcnow)


class DailyCheck(Base):
    __tablename__ = "daily_checks"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    check_date = Column(Date, nullable=False)
    smoked     = Column(Boolean, default=False)
    drank      = Column(Boolean, default=False)
    junk_food  = Column(Boolean, default=False)
    no_sleep   = Column(Boolean, default=False)
    party      = Column(Boolean, default=False)
    completed  = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
# PROGRESIÓN
# ═══════════════════════════════════════════════════════════

class Achievement(Base):
    __tablename__ = "achievements"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, nullable=False)
    achievement_id = Column(String, nullable=False)
    title          = Column(String, nullable=False)
    description    = Column(Text, default="")
    emoji          = Column(String, default="🏆")
    unlocked_at    = Column(DateTime, default=datetime.utcnow)


class HeroUnlock(Base):
    __tablename__ = "hero_unlocks"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, nullable=False)
    hero_name   = Column(String, nullable=False)
    hero_level  = Column(Integer, nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)


class GameOverLog(Base):
    __tablename__ = "game_over_log"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    level_lost = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class RewardClaim(Base):
    __tablename__ = "reward_claims"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False, default=1)
    reward_id  = Column(String, nullable=False)
    cost       = Column(Integer, nullable=False)
    currency   = Column(String, nullable=False)
    notes      = Column(Text, default="")
    date       = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class RPGLog(Base):
    __tablename__ = "rpg_log"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, nullable=False, default=1)
    type        = Column(String, nullable=False)
    action      = Column(String, nullable=False)
    description = Column(Text, default="")
    xp_change   = Column(Integer, default=0)
    wyrd_change = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)
