"""
rpg_models.py - Modelos del sistema de gamificación RPG (Caronte)
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base

def uid():
    return uuid.uuid4().hex[:16]

# ============================================
# SISTEMA CARONTE - GAMIFICACIÓN RPG
# ============================================

class UserProfile(Base):
    """Perfil RPG del usuario - Nivel, XP, Wyrd y monedas"""
    __tablename__ = "user_profile"
    
    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, unique=True, nullable=False)
    level        = Column(Integer, default=1)
    xp           = Column(Integer, default=0)
    wyrd         = Column(Integer, default=100)       # 0-100, destino del alma
    obolos       = Column(Integer, default=0)         # Moneda base diaria
    dracmas      = Column(Integer, default=0)         # Día perfecto
    tetradracmas = Column(Integer, default=0)         # Rachas semanales
    decadracmas  = Column(Integer, default=0)         # Logros épicos
    hero         = Column(String, default="Alma Errante")
    streak       = Column(Integer, default=0)         # Días consecutivos
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at   = Column(DateTime, default=datetime.utcnow)

class XPLog(Base):
    """Historial de XP ganado/perdido"""
    __tablename__ = "xp_log"
    
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    amount     = Column(Integer, nullable=False)
    reason     = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class WyrdLog(Base):
    """Historial de cambios en el Wyrd (vida/destino)"""
    __tablename__ = "wyrd_log"
    
    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, nullable=False)
    amount       = Column(Integer, nullable=False)   # Positivo o negativo
    reason       = Column(String, default="")
    wyrd_before  = Column(Integer, nullable=False)
    wyrd_after   = Column(Integer, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

class CoinsLog(Base):
    """Historial de monedas ganadas/gastadas"""
    __tablename__ = "coins_log"
    
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    coin_type  = Column(String, nullable=False)    # obolo, dracma, tetradracma, decadracma
    amount     = Column(Integer, nullable=False)   # Positivo = ganado, negativo = gastado
    reason     = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class Artifact(Base):
    """Catálogo de artefactos míticos comprables"""
    __tablename__ = "artifacts"
    
    id           = Column(String, primary_key=True, default=uid)
    name         = Column(String, nullable=False)       # Lira de Orfeo
    hero_origin  = Column(String, default="")           # Orfeo
    emoji        = Column(String, default="⚔️")
    description  = Column(Text, default="")
    effect       = Column(Text, default="")             # Descripción del efecto
    effect_type  = Column(String, default="")           # shield_streak, double_xp, etc.
    effect_value = Column(Integer, default=1)           # Veces que aplica o % de efecto
    price_type   = Column(String, default="tetradracma")
    price        = Column(Integer, nullable=False)
    active       = Column(Boolean, default=True)

class UserArtifact(Base):
    """Artefactos comprados por el usuario"""
    __tablename__ = "user_artifacts"
    
    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, nullable=False)
    artifact_id  = Column(String, ForeignKey("artifacts.id"), nullable=False)
    equipped     = Column(Boolean, default=False)
    uses_left    = Column(Integer, default=1)          # Usos restantes
    purchased_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    artifact = relationship("Artifact")

class Achievement(Base):
    """Logros desbloqueados"""
    __tablename__ = "achievements"
    
    id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, nullable=False)
    achievement_id = Column(String, nullable=False)    # ej: "streak_7", "level_10"
    title          = Column(String, nullable=False)
    description    = Column(Text, default="")
    emoji          = Column(String, default="🏆")
    unlocked_at    = Column(DateTime, default=datetime.utcnow)

class HeroUnlock(Base):
    """Héroes desbloqueados por nivel"""
    __tablename__ = "hero_unlocks"
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, nullable=False)
    hero_name   = Column(String, nullable=False)
    hero_level  = Column(Integer, nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)

class BadHabitLog(Base):
    """Registro de malos hábitos (fumar, beber, etc.)"""
    __tablename__ = "bad_habits_log"
    
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    habit_type = Column(String, nullable=False)   # smoking, drinking, junk_food...
    wyrd_lost  = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class BadHabitLogExtra(Base):
    """Registro manual de recaídas desde la web"""
    __tablename__ = "bad_habit_logs"
    
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False, default=1)
    habit_name = Column(String, nullable=False)
    penalty    = Column(Integer, nullable=False, default=10)
    date       = Column(String, nullable=False)
    notes      = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyCheck(Base):
    """Check nocturno diario - Malos hábitos respondidos"""
    __tablename__ = "daily_checks"
    
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    check_date = Column(Date, nullable=False)
    smoked     = Column(Boolean, default=False)
    drank      = Column(Boolean, default=False)
    junk_food  = Column(Boolean, default=False)
    no_sleep   = Column(Boolean, default=False)
    party      = Column(Boolean, default=False)
    completed  = Column(Boolean, default=False)  # Si respondió el check
    created_at = Column(DateTime, default=datetime.utcnow)

class GameOverLog(Base):
    """Registro de Game Overs - El alma que vagó 100 años"""
    __tablename__ = "game_over_log"
    
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    level_lost = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class RewardClaim(Base):
    """Registro de recompensas canjeadas"""
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
    """Log general de eventos RPG"""
    __tablename__ = "rpg_log"
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, nullable=False, default=1)
    type        = Column(String, nullable=False)  # 'good', 'bad', 'reward', 'neutral'
    action      = Column(String, nullable=False)
    description = Column(Text, default="")
    xp_change   = Column(Integer, default=0)
    wyrd_change = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)