"""
caronte_dice.py - Sistema de dados de Caronte (fin del día)
Autor: alvarofernandezmota-tech
Fecha: 2026-03-07

Tiradas de dados al final del día según
  - Nivel del usuario
  - Racha activa
  - Comportamiento (malos hábitos ese día)

3 Combos:
  1. Póker       (3 iguales + 1 comodín) → XP + monedas + artefacto common
  2. Triple Ánfora (3 ánforas)            → XP + monedas + artefacto rare
  3. Repóker      (4 iguales)             → XP + indulgencias + artefacto legendary

Indulgencias:
  - Prevención: compra ANTES de cometer mal hábito (coste base)
  - Absolución: compra DESPUÉS (150% coste, recupera Wyrd)
  - Racha 7 días activa → 50% desc
"""
import json
import random
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..core.rpg_models import DiceRollLog, UserProfile, Artifact
from ..config.settings import settings

# ─────────────────────────────────────────────
# DEFINICIÓN DE DADOS
# ─────────────────────────────────────────────

DIE_POOL_BY_LEVEL = {
    "1-4":   {"pool": ["⚙️", "⚙️", "🏺", "🏺", "💀", "🪙"], "dice_count": 2},  # Tier 1
    "5-9":   {"pool": ["⚙️", "⚙️", "🏺", "🏺", "💀", "🪙"], "dice_count": 3},  # Tier 1
    "10-14": {"pool": ["⚙️", "🏺", "🏺", "🏺", "💀", "🪙"], "dice_count": 3},  # Tier 2
    "15-19": {"pool": ["⚙️", "🏺", "🏺", "🏺", "💀", "🪙"], "dice_count": 4},  # Tier 2
    "20-29": {"pool": ["🏺", "🏺", "🏺", "🏺", "💀", "🪙"], "dice_count": 4},  # Tier 3
    "30+":   {"pool": ["🏺", "🏺", "🏺", "🏺", "💀", "🪙"], "dice_count": 5},  # Tier 3
}

COMBO_REWARDS = {
    "Poker": {
        "xp": 70, "obolos": 4, "dracmas": 1,
        "artifact_rarity": "common", "narrative": "¡Caronte sonríe! Pequeño triunfo.",
    },
    "Triple Anfora": {
        "xp": 120, "obolos": 6, "dracmas": 2, "tetradracmas": 1,
        "artifact_rarity": "rare", "narrative": "🏺 Triple Ánfora. Las almas se inclinan ante ti.",
    },
    "Repoker": {
        "xp": 200, "dracmas": 3, "tetradracmas": 2, "indulgencias": 1,
        "artifact_rarity": "legendary", "narrative": "🪙 REPÓKER. La Laguna Estigia retrocede.",
    },
}

# Recompensas base (si no hay combo)
BASE_REWARDS = {
    "no_combo_low":   {"obolos": 2, "xp": 5},
    "no_combo_med":   {"obolos": 3, "xp": 10},
    "no_combo_high":  {"obolos": 5, "xp": 20, "dracmas": 1},
}

STREAK_MULTIPLIERS = {
    "0-6":   1.0,
    "7-13":  1.2,
    "14-20": 1.5,
    "21-29": 1.75,
    "30+":   2.0,
}

INDULGENCE_BASE_COST = {
    "smoking":            {"dracmas": 4},
    "drinking":           {"dracmas": 3, "obolos": 5},
    "party_no_sleep":     {"dracmas": 3},
    "netflix_binge":      {"dracmas": 2},
    "missed_appointment": {"dracmas": 2, "obolos": 2},
    "task_overdue":       {"obolos": 5},
}


# ─────────────────────────────────────────────
# TIRADA DIARIA DE DADOS
# ─────────────────────────────────────────────

def daily_dice_roll(
    db: Session,
    user_id: int,
    level: int,
    streak_days: int,
    habits_completed: bool,
    tasks_completed: bool,
) -> Dict[str, Any]:
    """
    Ejecuta la tirada diaria de dados al final del día.
    Devuelve combo/recompensas/narrativa.
    """
    # 1) Determinar pool y número de dados
    dice_cfg = _get_dice_config(level)
    pool = dice_cfg["pool"]
    dice_count = dice_cfg["dice_count"]

    # 2) Tirada
    roll = [random.choice(pool) for _ in range(dice_count)]

    # 3) Detectar combo
    combo = _detect_combo(roll)

    # 4) Recompensas base o combo
    if combo:
        rewards = COMBO_REWARDS[combo].copy()
    else:
        # Recompensas proporcionales a nivel/racha
        if level < 5:
            rewards = BASE_REWARDS["no_combo_low"].copy()
        elif level < 15:
            rewards = BASE_REWARDS["no_combo_med"].copy()
        else:
            rewards = BASE_REWARDS["no_combo_high"].copy()

    # 5) Aplicar multiplicador de racha
    mult = _get_streak_multiplier(streak_days)
    for key in ["xp", "obolos", "dracmas", "tetradracmas"]:
        if key in rewards:
            rewards[key] = int(rewards[key] * mult)

    # 6) Recompensa de artefacto (si combo)
    artifact = None
    if combo and "artifact_rarity" in rewards:
        artifact = _grant_artifact_by_rarity(db, user_id, rewards["artifact_rarity"])
        rewards["artifact"] = artifact.name if artifact else "Sin artefactos disponibles"

    # 7) Actualizar perfil del usuario
    from .rpg import RPGService
    rpg = RPGService(db, user_id)

    rpg.add_xp(rewards.get("xp", 0), "Dados Caronte")
    for coin in ["obolos", "dracmas", "tetradracmas"]:
        if coin in rewards:
            rpg.add_coins(coin, rewards[coin], "Dados Caronte")

    if "indulgencias" in rewards:
        rpg.grant_indulgencias(rewards["indulgencias"], "Repóker Caronte")

    # 8) Log de la tirada
    log = DiceRollLog(
        user_id=user_id,
        dice_count=dice_count,
        die_tier=_tier_for_level(level),
        roll_result=json.dumps(roll),
        combo=combo or "Sin combo",
        rewards_json=json.dumps(rewards),
        artifact_id=artifact.id if artifact else None,
        streak_mult=str(mult),
    )
    db.add(log)
    db.commit()

    return {
        "roll":          roll,
        "dice_count":    dice_count,
        "combo":         combo,
        "narrative":     rewards.get("narrative", "Las monedas tintinean en el río."),
        "rewards":       rewards,
        "streak_mult":   mult,
        "profile":       rpg.get_profile_dict(),
    }


# ─────────────────────────────────────────────
# INDULGENCIAS
# ─────────────────────────────────────────────

def get_indulgence_cost(habit_type: str, streak: int) -> Dict[str, int]:
    """
    Calcula el coste de una indulgencia de prevención con descuento por racha activa.
    """
    base = INDULGENCE_BASE_COST.get(habit_type, {"dracmas": 3})
    discount = 0.5 if streak >= 7 else 1.0
    return {k: max(1, int(v * discount)) for k, v in base.items()}


def buy_indulgence_before(db: Session, user_id: int, habit_type: str, streak: int) -> Dict[str, Any]:
    """
    Compra una indulgencia de PREVENCIÓN (ANTES de cometer el mal hábito).
    Coste base, con 50% desc si racha ≥ 7.
    """
    from .rpg import RPGService
    rpg = RPGService(db, user_id)

    cost = get_indulgence_cost(habit_type, streak)
    if not _can_afford(rpg, cost):
        return {"success": False, "reason": "Monedas insuficientes"}

    rpg.apply_coin_dict(cost, f"Indulgencia prevención: {habit_type}", subtract=True)
    rpg.grant_indulgencias(1, f"Indulgencia prevención: {habit_type}")
    db.commit()

    return {
        "success":     True,
        "type":        "prevention",
        "cost":        cost,
        "indulgences": rpg.get_or_create_profile().indulgencias,
    }


def buy_indulgence_after(db: Session, user_id: int, habit_type: str, streak: int, wyrd_lost: int) -> Dict[str, Any]:
    """
    Compra una ABSOLUCIÓN (DESPUÉS de cometer el mal hábito).
    Coste = 1.5x base, recupera Wyrd perdido.
    """
    from .rpg import RPGService
    rpg = RPGService(db, user_id)

    base_cost = get_indulgence_cost(habit_type, streak)
    cost = {k: int(v * 1.5) for k, v in base_cost.items()}

    if not _can_afford(rpg, cost):
        return {"success": False, "reason": "Monedas insuficientes"}

    rpg.apply_coin_dict(cost, f"Absolución: {habit_type}", subtract=True)
    rpg.grant_indulgencias(1, f"Absolución: {habit_type}")
    rpg.modify_wyrd(wyrd_lost, f"Absolución recupera Wyrd: {habit_type}")
    db.commit()

    return {
        "success":       True,
        "type":          "absolution",
        "cost":          cost,
        "wyrd_recovered": wyrd_lost,
        "indulgences":   rpg.get_or_create_profile().indulgencias,
    }


# ─────────────────────────────────────────────
# HELPERS INTERNOS
# ─────────────────────────────────────────────

def _get_dice_config(level: int) -> Dict[str, Any]:
    if level < 5:
        return DIE_POOL_BY_LEVEL["1-4"]
    elif level < 10:
        return DIE_POOL_BY_LEVEL["5-9"]
    elif level < 15:
        return DIE_POOL_BY_LEVEL["10-14"]
    elif level < 20:
        return DIE_POOL_BY_LEVEL["15-19"]
    elif level < 30:
        return DIE_POOL_BY_LEVEL["20-29"]
    else:
        return DIE_POOL_BY_LEVEL["30+"]


def _tier_for_level(level: int) -> int:
    if level < 10:
        return 1
    elif level < 20:
        return 2
    return 3


def _get_streak_multiplier(streak: int) -> float:
    if streak < 7:
        return STREAK_MULTIPLIERS["0-6"]
    elif streak < 14:
        return STREAK_MULTIPLIERS["7-13"]
    elif streak < 21:
        return STREAK_MULTIPLIERS["14-20"]
    elif streak < 30:
        return STREAK_MULTIPLIERS["21-29"]
    return STREAK_MULTIPLIERS["30+"]


def _detect_combo(roll: List[str]) -> str | None:
    """
    Detecta combos:
      1. Repóker       → 4 iguales
      2. Triple Ánfora → 3 ánforas
      3. Póker         → 3 iguales + 1 comodín
    """
    from collections import Counter
    counts = Counter(roll)

    # 1) Repóker (4 iguales)
    for symbol, c in counts.items():
        if c >= 4:
            return "Repoker"

    # 2) Triple Ánfora (3 ánforas)
    if counts.get("🏺", 0) >= 3:
        return "Triple Anfora"

    # 3) Póker (3 iguales + 1 comodín)
    has_wildcard = "🪙" in roll
    for symbol, c in counts.items():
        if symbol != "🪙" and c >= 3 and has_wildcard:
            return "Poker"

    return None


def _grant_artifact_by_rarity(db: Session, user_id: int, rarity: str) -> Artifact | None:
    """Otorga un artefacto aleatorio de la rareza especificada."""
    artifacts = db.query(Artifact).filter(
        Artifact.rarity == rarity,
        Artifact.active == True,
    ).all()

    if not artifacts:
        return None

    artifact = random.choice(artifacts)

    from .rpg import RPGService
    rpg = RPGService(db, user_id)
    rpg.grant_artifact(artifact.id, source="dice_combo")

    return artifact


def _can_afford(rpg, cost: Dict[str, int]) -> bool:
    """Verifica si el usuario tiene suficientes monedas."""
    profile = rpg.get_or_create_profile()
    for coin_type, amount in cost.items():
        actual = getattr(profile, coin_type, 0)
        if actual < amount:
            return False
    return True
