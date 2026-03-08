"""
caronte_dice.py - Sistema de Dados CARONTE (tirada nocturna, estilo poker)
Actualizado 2026-03-07:
  - Integrado con RPGService (ORM) — sin dependencias a gamification.py
  - Renombrado de dice_system.py para no colisionar con src/core/dice_system.py (D&D)
  - grant_artifact() usa RPGService.grant_artifact() (ORM)
  - DiceRollLog persistido via modelo ORM DiceRollLog
"""
import random
import json
from collections import Counter
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session

from ..core.rpg_models import DiceRollLog, IndulgenciaLog
from ..config.settings import settings


# ═══════════════════════════════════════════════════════════
# CARAS DE LOS DADOS
# ═══════════════════════════════════════════════════════════

class DieFace(str, Enum):
    SKULL     = "💀"   # Neutro — sin valor
    OBOLO     = "⚙️"   # Óbolo (moneda pequeña)
    DRACMA    = "🪙"   # Dracma (moneda media)
    LIGHTNING = "⚡"   # XP bonus
    EYE       = "👁️"   # Indulgencia
    ARTIFACT  = "🏺"   # Artefacto (rarísimo)


# Distribución de caras por tier del dado (mejoran con nivel)
DIE_FACES_BY_TIER: Dict[int, List[DieFace]] = {
    1: [DieFace.SKULL, DieFace.SKULL, DieFace.SKULL,
        DieFace.OBOLO, DieFace.OBOLO, DieFace.LIGHTNING],
    2: [DieFace.SKULL, DieFace.SKULL,
        DieFace.OBOLO, DieFace.OBOLO, DieFace.DRACMA, DieFace.LIGHTNING],
    3: [DieFace.SKULL,
        DieFace.OBOLO, DieFace.OBOLO, DieFace.DRACMA,
        DieFace.LIGHTNING, DieFace.EYE],
    4: [DieFace.OBOLO, DieFace.DRACMA, DieFace.DRACMA,
        DieFace.LIGHTNING, DieFace.EYE, DieFace.ARTIFACT],
}


def get_die_tier(level: int) -> int:
    if level >= 30: return 4
    if level >= 15: return 3
    if level >= 5:  return 2
    return 1


# ═══════════════════════════════════════════════════════════
# COMBOS (estilo poker)
# ═══════════════════════════════════════════════════════════

class Combo(str, Enum):
    NOTHING       = "nothing"
    PAIR          = "pair"
    TWO_PAIR      = "two_pair"
    THREE_KIND    = "three_kind"
    STRAIGHT      = "straight"
    FULL_HOUSE    = "full_house"
    FOUR_KIND     = "four_kind"
    FIVE_KIND     = "five_kind"
    ARTIFACT_TRIO = "artifact_trio"


COMBO_INFO = {
    Combo.NOTHING:       ("Sin combo",     "🎲", "El río sigue igual."),
    Combo.PAIR:          ("Par",           "✌️", "Los dioses te notan."),
    Combo.TWO_PAIR:      ("Doble par",     "🤝", "Caronte asiente."),
    Combo.THREE_KIND:    ("Trío",          "🔱", "Poseidón te favorece."),
    Combo.STRAIGHT:      ("Escalera",      "⚡", "Los astros se alinean."),
    Combo.FULL_HOUSE:    ("Full House",    "🌊", "Las Moiras hilan tu destino."),
    Combo.FOUR_KIND:     ("Póker",         "💎", "Zeus te bendice."),
    Combo.FIVE_KIND:     ("Repóker",       "👑", "El Olimpo te aclama."),
    Combo.ARTIFACT_TRIO: ("Triple Ánfora", "🏺", "Un artefacto emerge del Érebo."),
}

# Premios por combo: {obolos, dracmas, tetradracmas, xp, indulgencias, wyrd, artefacto_rarity}
COMBO_REWARDS: Dict[Combo, Dict[str, Any]] = {
    Combo.NOTHING:       {"obolos": 0,  "dracmas": 0, "tetradracmas": 0, "xp": 0,   "indulgencias": 0, "wyrd": 0,  "artefacto": None},
    Combo.PAIR:          {"obolos": 2,  "dracmas": 0, "tetradracmas": 0, "xp": 10,  "indulgencias": 0, "wyrd": 0,  "artefacto": None},
    Combo.TWO_PAIR:      {"obolos": 4,  "dracmas": 1, "tetradracmas": 0, "xp": 20,  "indulgencias": 0, "wyrd": 5,  "artefacto": None},
    Combo.THREE_KIND:    {"obolos": 0,  "dracmas": 3, "tetradracmas": 0, "xp": 40,  "indulgencias": 1, "wyrd": 10, "artefacto": None},
    Combo.STRAIGHT:      {"obolos": 0,  "dracmas": 5, "tetradracmas": 0, "xp": 60,  "indulgencias": 1, "wyrd": 15, "artefacto": None},
    Combo.FULL_HOUSE:    {"obolos": 0,  "dracmas": 0, "tetradracmas": 1, "xp": 100, "indulgencias": 2, "wyrd": 20, "artefacto": None},
    Combo.FOUR_KIND:     {"obolos": 0,  "dracmas": 0, "tetradracmas": 2, "xp": 200, "indulgencias": 3, "wyrd": 25, "artefacto": "common"},
    Combo.FIVE_KIND:     {"obolos": 0,  "dracmas": 0, "tetradracmas": 5, "xp": 500, "indulgencias": 5, "wyrd": 30, "artefacto": "legendary"},
    Combo.ARTIFACT_TRIO: {"obolos": 0,  "dracmas": 0, "tetradracmas": 3, "xp": 300, "indulgencias": 4, "wyrd": 20, "artefacto": "rare"},
}

# Catálogo de artefactos por rareza (IDs deben coincidir con seed de init_db.py)
ARTIFACT_POOL = {
    "common": [
        "sandalias_hermes", "arco_apolo", "laurel_apolo", "egida_atenea",
    ],
    "rare": [
        "lira_orfeo", "casco_hades", "tridente_poseidon",
    ],
    "legendary": [
        "rayo_zeus", "caduceo_hermes", "armadura_aquiles",
    ],
}


def _roll_artifact(rarity: str) -> Optional[str]:
    pool = ARTIFACT_POOL.get(rarity, [])
    return random.choice(pool) if pool else None


# ═══════════════════════════════════════════════════════════
# LÓGICA DE TIRADA
# ═══════════════════════════════════════════════════════════

def calculate_dice_count(
    habits_completed: bool,
    tasks_completed: bool,
    streak_days: int,
) -> Tuple[int, List[str]]:
    count, reasons = 3, ["3 dados base"]
    if habits_completed:
        count += 1
        reasons.append("+1 por todos los hábitos completados")
    if tasks_completed:
        count += 1
        reasons.append("+1 por todas las tareas completadas")
    if streak_days >= 7:
        count += 1
        reasons.append(f"+1 dado de racha ({streak_days} días consecutivos)")
    return count, reasons


def roll_dice(num_dice: int, die_tier: int) -> List[DieFace]:
    faces = DIE_FACES_BY_TIER[die_tier]
    return [random.choice(faces) for _ in range(num_dice)]


def detect_combo(roll: List[DieFace]) -> Combo:
    counts = Counter(roll)

    if counts.get(DieFace.ARTIFACT, 0) >= 3:
        return Combo.ARTIFACT_TRIO

    freq = sorted(counts.values(), reverse=True)

    if freq[0] >= 5:
        return Combo.FIVE_KIND
    if freq[0] >= 4:
        return Combo.FOUR_KIND
    if freq[0] >= 3 and len(freq) >= 2 and freq[1] >= 2:
        return Combo.FULL_HOUSE
    if freq[0] >= 3:
        return Combo.THREE_KIND

    non_skull = [f for f in roll if f != DieFace.SKULL]
    if len(set(non_skull)) >= 3 and len(non_skull) >= 3:
        return Combo.STRAIGHT

    pairs = sum(1 for v in counts.values() if v >= 2)
    if pairs >= 2:
        return Combo.TWO_PAIR
    if pairs >= 1:
        return Combo.PAIR

    return Combo.NOTHING


def _streak_multiplier(streak_days: int) -> Tuple[float, Optional[str]]:
    if streak_days >= 30:
        return 1.5, "⭐ Racha mítica (×1.5)"
    if streak_days >= 14:
        return 1.25, "🔥 Racha épica (×1.25)"
    if streak_days >= 7:
        return 1.1, "✨ Racha activa (×1.1)"
    return 1.0, None


# ═══════════════════════════════════════════════════════════
# TIRADA COMPLETA AL FINAL DEL DÍA
# ═══════════════════════════════════════════════════════════

def daily_dice_roll(
    db: Session,
    user_id: int,
    level: int,
    streak_days: int,
    habits_completed: bool,
    tasks_completed: bool,
) -> Dict[str, Any]:
    """
    Tirada completa de dados al final del día.
    Persiste el resultado en DiceRollLog y aplica recompensas via RPGService.

    Returns:
        Dict con roll, combo, rewards, artifact y narrative para el frontend.
    """
    from .rpg import RPGService
    rpg = RPGService(db, user_id)

    streak_mult, streak_label = _streak_multiplier(streak_days)
    dice_count, dice_reasons  = calculate_dice_count(habits_completed, tasks_completed, streak_days)
    die_tier                  = get_die_tier(level)
    roll                      = roll_dice(dice_count, die_tier)
    combo                     = detect_combo(roll)
    rewards_template          = COMBO_REWARDS[combo]

    applied: Dict[str, Any] = {}

    # Monedas (con multiplicador)
    for coin in ("obolos", "dracmas", "tetradracmas"):
        amount = int(rewards_template[coin] * streak_mult)
        if amount > 0:
            rpg.add_coins(coin, amount, f"Combo dados: {combo.value}")
            applied[coin] = amount

    # XP
    xp = int(rewards_template["xp"] * streak_mult)
    if xp > 0:
        xp_result = rpg.add_xp(xp, f"Combo dados: {combo.value}")
        applied["xp"] = xp
        applied["leveled_up"] = xp_result.get("leveled_up", False)

    # Wyrd
    if rewards_template["wyrd"] > 0:
        rpg.modify_wyrd(rewards_template["wyrd"], f"Combo dados: {combo.value}")
        applied["wyrd"] = rewards_template["wyrd"]

    # Indulgencias
    if rewards_template["indulgencias"] > 0:
        rpg.grant_indulgencias(rewards_template["indulgencias"], f"Combo: {combo.value}")
        applied["indulgencias"] = rewards_template["indulgencias"]

    # Artefacto
    artifact_id = None
    if rewards_template["artefacto"]:
        artifact_id = _roll_artifact(rewards_template["artefacto"])
        if artifact_id:
            rpg.grant_artifact(artifact_id, source="dice_combo")
            applied["artefacto"] = artifact_id

    # Persistir log
    roll_log = DiceRollLog(
        user_id=user_id,
        dice_count=dice_count,
        die_tier=die_tier,
        roll_result=json.dumps([f.value for f in roll]),
        combo=combo.value,
        rewards_json=json.dumps(applied),
        artifact_id=artifact_id,
        streak_mult=str(streak_mult),
    )
    db.add(roll_log)
    db.commit()

    name, emoji, narrative = COMBO_INFO[combo]

    return {
        "dice_count":   dice_count,
        "dice_reasons": dice_reasons,
        "die_tier":     die_tier,
        "roll":         [f.value for f in roll],
        "combo":        combo.value,
        "combo_name":   name,
        "combo_emoji":  emoji,
        "narrative":    narrative,
        "streak_mult":  streak_mult,
        "streak_label": streak_label,
        "rewards":      applied,
        "artifact_id":  artifact_id,
    }


# ═══════════════════════════════════════════════════════════
# SISTEMA DE INDULGENCIAS (compra con monedas)
# ═══════════════════════════════════════════════════════════

# Coste base en dracmas por tipo de mal hábito
INDULGENCE_COSTS: Dict[str, Dict[str, int]] = {
    "smoking":       {"dracmas": 5},
    "drinking":      {"dracmas": 4},
    "junk_food":     {"dracmas": 2},
    "party_nodream": {"dracmas": 3},
    "no_sleep":      {"dracmas": 2},
    "netflix_binge": {"dracmas": 2},
}

INDULGENCE_STREAK_DISCOUNT = {7: 0.10, 14: 0.20, 30: 0.35}


def get_indulgence_cost(habit_type: str, streak_days: int) -> Dict[str, int]:
    base = INDULGENCE_COSTS.get(habit_type, {"dracmas": 3})
    discount = 0.0
    for min_streak, pct in sorted(INDULGENCE_STREAK_DISCOUNT.items(), reverse=True):
        if streak_days >= min_streak:
            discount = pct
            break
    return {coin: max(1, int(amount * (1 - discount))) for coin, amount in base.items()}


def buy_indulgence_before(
    db: Session,
    user_id: int,
    habit_type: str,
    streak_days: int,
) -> Dict[str, Any]:
    """
    PREVENCIÓN: paga con monedas para que el próximo mal hábito no quite Wyrd.
    Añade 1 token de indulgencia al perfil (gestionado por RPGService.use_indulgencia).
    """
    from .rpg import RPGService
    rpg = RPGService(db, user_id)

    cost = get_indulgence_cost(habit_type, streak_days)
    for coin, amount in cost.items():
        rpg.add_coins(coin, -amount, f"Indulgencia previa: {habit_type}")

    rpg.grant_indulgencias(1, f"Prevención: {habit_type}")

    log = IndulgenciaLog(
        user_id=user_id, habit_type=habit_type,
        type="prevention", cost_json=json.dumps(cost), wyrd_recovered=0,
    )
    db.add(log)
    db.commit()

    return {
        "type":    "prevention",
        "habit":   habit_type,
        "cost":    cost,
        "message": "Indulgencia concedida. Caronte mirará hacia otro lado... esta vez.",
    }


def buy_indulgence_after(
    db: Session,
    user_id: int,
    habit_type: str,
    streak_days: int,
    wyrd_lost: int,
) -> Dict[str, Any]:
    """
    ABSOLUCIÓN: paga (50% más caro) para recuperar el Wyrd perdido por un mal hábito.
    """
    from .rpg import RPGService
    rpg = RPGService(db, user_id)

    base = get_indulgence_cost(habit_type, streak_days)
    cost = {coin: max(1, int(amount * 1.5)) for coin, amount in base.items()}
    for coin, amount in cost.items():
        rpg.add_coins(coin, -amount, f"Absolución: {habit_type}")

    wyrd_result = rpg.modify_wyrd(wyrd_lost, f"Absolución pagada: {habit_type}")

    log = IndulgenciaLog(
        user_id=user_id, habit_type=habit_type,
        type="absolution", cost_json=json.dumps(cost), wyrd_recovered=wyrd_lost,
    )
    db.add(log)
    db.commit()

    return {
        "type":           "absolution",
        "habit":          habit_type,
        "cost":           cost,
        "wyrd_recovered": wyrd_lost,
        "wyrd_result":    wyrd_result,
        "message":        f"Los dioses aceptan tu ofrenda. +{wyrd_lost} Wyrd recuperado.",
    }
