"""
rpg.py - RPG Service (Sistema Caronte)
Actualizado 2026-03-07:
  - add_coins() acepta claves plural Y singular (obolos/obolo, etc.)
  - Fórmula de nivel usa tabla LEVEL_XP de constants (no fórmula sqrt)
  - log_bad_habit() aplica penalización Wyrd + monedas (COIN_PENALTIES)
  - Nuevos métodos: reward_habit, reward_task, reward_perfect_day,
    reward_weekly_streak, reward_monthly_streak, reward_level_up,
    penalize_streak_broken, penalize_task_overdue
  - grant_indulgencia() para añadir tokens al perfil
"""
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

from ..core.rpg_models import (
    UserProfile, XPLog, WyrdLog, CoinsLog,
    Artifact, UserArtifact, Achievement, BadHabitLog, DailyCheck,
    IndulgenciaLog,
)
from ..config.settings import settings

# ─────────────────────────────────────────────
# Constantes RPG (CARONTE-SPEC v1.0)
# ─────────────────────────────────────────────

# XP necesario para cada nivel (tabla discreta — no fórmula sqrt)
LEVEL_XP = {
    1: 0,    2: 100,   3: 200,   4: 350,   5: 500,
    6: 750,  7: 1000,  8: 1250,  9: 1500,  10: 2000,
    15: 3500, 20: 7000, 25: 15000, 30: 30000,
    35: 55000, 40: 80000, 45: 120000, 50: 200000,
}

XP_REWARDS = {
    "habit_completed":    10,
    "task_completed":     20,
    "all_tasks_done":     30,
    "perfect_day":        50,
    "weekly_streak":      100,
    "monthly_streak":     500,
    "boss_defeated":      100,
    "achievement":        50,
    "level_up":           0,
}

COIN_REWARDS = {
    "habit_completed":    {"obolos": 1},
    "all_tasks_completed":{"dracmas": 1},
    "perfect_day":        {"dracmas": 1, "obolos": 3},
    "weekly_streak":      {"tetradracmas": 1},
    "monthly_streak":     {"decadracmas": 1},
    "achievement":        {"tetradracmas": 1},
    "level_up":           {"tetradracmas": 2},
}

COIN_PENALTIES = {
    "smoking":            {"dracmas": 3},
    "drinking":           {"dracmas": 2, "obolos": 5},
    "habit_missed":       {"obolos": 2},
    "streak_broken":      {"dracmas": 1},
    "missed_appointment": {"dracmas": 1, "obolos": 2},
    "task_overdue":       {"obolos": 3},
}

WYRD_PENALTIES = {
    "smoking":         30,
    "drinking":        25,
    "party_no_sleep":  20,
    "netflix_binge":   15,
    "streak_broken":   25,
    "task_overdue":    12,
    "missed_appointment": 15,
}

WYRD_GAINS = {
    "exercise":       15,
    "study_session":  10,
    "sleep_8h":       10,
    "social_event":   12,
    "all_tasks_done": 15,
    "weekly_streak":  25,
}

# Héroes por nivel
HEROES = {
    1:  {"name": "Alma Errante",  "emoji": "🌱"},
    5:  {"name": "Psique",        "emoji": "👤"},
    10: {"name": "Orfeo",         "emoji": "🎵"},
    15: {"name": "Teseo",         "emoji": "⚔️"},
    20: {"name": "Ulises",        "emoji": "🌊"},
    25: {"name": "Aquiles",       "emoji": "🗡️"},
    30: {"name": "Heracles",      "emoji": "💪"},
    35: {"name": "Perseo",        "emoji": "🦅"},
    40: {"name": "Poseidón",      "emoji": "🔱"},
    45: {"name": "Atenea",        "emoji": "📚"},
    50: {"name": "Caronte",       "emoji": "👑"},
}

# Normalización plural → singular para columnas DB
_COIN_NORMALIZE = {
    "obolos":       "obolo",
    "dracmas":      "dracma",
    "tetradracmas": "tetradracma",
    "decadracmas":  "decadracma",
    # singular pasan tal cual
    "obolo":        "obolo",
    "dracma":       "dracma",
    "tetradracma":  "tetradracma",
    "decadracma":   "decadracma",
}


class RPGService:
    """
    Service para el sistema de gamificación RPG (Caronte).
    Única fuente de verdad para XP, Wyrd, monedas y artefactos.
    """

    def __init__(self, db: Session, user_id: int = None):
        self.db = db
        self.user_id = user_id or settings.DEFAULT_USER_ID

    # ═══════════════════════════════════════════════════════════
    # PERFIL
    # ═══════════════════════════════════════════════════════════

    def get_or_create_profile(self) -> UserProfile:
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == self.user_id
        ).first()

        if not profile:
            profile = UserProfile(
                user_id=self.user_id,
                level=settings.STARTING_LEVEL,
                xp=settings.STARTING_XP,
                wyrd=settings.STARTING_WYRD,
                hero="Alma Errante",
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)

        return profile

    def get_profile_dict(self) -> Dict[str, Any]:
        p = self.get_or_create_profile()
        wyrd_state = self._wyrd_state(p.wyrd)
        hero = self._hero_for_level(p.level)
        return {
            "user_id":      p.user_id,
            "level":        p.level,
            "xp":           p.xp,
            "xp_next_level":self._xp_for_next_level(p.level, p.xp),
            "wyrd":         p.wyrd,
            "wyrd_state":   wyrd_state,
            "obolos":       p.obolos,
            "dracmas":      p.dracmas,
            "tetradracmas": p.tetradracmas,
            "decadracmas":  p.decadracmas,
            "indulgencias": p.indulgencias,
            "hero":         hero,
            "streak":       p.streak,
        }

    # ═══════════════════════════════════════════════════════════
    # XP & NIVEL
    # ═══════════════════════════════════════════════════════════

    def add_xp(self, amount: int, reason: str = "") -> Dict[str, Any]:
        """Añade XP y recalcula nivel usando tabla LEVEL_XP."""
        profile = self.get_or_create_profile()
        old_level = profile.level
        profile.xp += amount

        # Recalcular nivel con tabla discreta
        new_level = 1
        for lvl in sorted(LEVEL_XP.keys()):
            if profile.xp >= LEVEL_XP[lvl]:
                new_level = lvl

        leveled_up = new_level > old_level
        profile.level = new_level
        profile.hero = self._hero_for_level(new_level)["name"]

        self.db.add(XPLog(user_id=self.user_id, amount=amount, reason=reason))
        self.db.commit()
        self.db.refresh(profile)

        return {
            "old_level":  old_level,
            "new_level":  new_level,
            "xp_total":   profile.xp,
            "leveled_up": leveled_up,
            "hero":       self._hero_for_level(new_level),
        }

    # ═══════════════════════════════════════════════════════════
    # WYRD
    # ═══════════════════════════════════════════════════════════

    def modify_wyrd(self, amount: int, reason: str = "") -> Dict[str, Any]:
        """Modifica Wyrd (positivo o negativo), clampea 0-100."""
        profile = self.get_or_create_profile()
        before = profile.wyrd
        profile.wyrd = max(0, min(100, profile.wyrd + amount))
        after = profile.wyrd

        self.db.add(WyrdLog(
            user_id=self.user_id, amount=amount, reason=reason,
            wyrd_before=before, wyrd_after=after,
        ))
        self.db.commit()
        self.db.refresh(profile)

        return {
            "wyrd_before": before,
            "wyrd_after":  after,
            "game_over":   after == 0,
            "state":       self._wyrd_state(after),
        }

    # ═══════════════════════════════════════════════════════════
    # MONEDAS — acepta singular Y plural
    # ═══════════════════════════════════════════════════════════

    def add_coins(self, coin_type: str, amount: int, reason: str = "") -> bool:
        """
        Añade (o resta si amount < 0) monedas al perfil.
        Acepta claves en plural (obolos, dracmas, tetradracmas, decadracmas)
        y en singular (obolo, dracma, tetradracma, decadracma).
        """
        singular = _COIN_NORMALIZE.get(coin_type)
        if not singular:
            return False

        profile = self.get_or_create_profile()

        if singular == "obolo":
            profile.obolos       = max(0, profile.obolos + amount)
        elif singular == "dracma":
            profile.dracmas      = max(0, profile.dracmas + amount)
        elif singular == "tetradracma":
            profile.tetradracmas = max(0, profile.tetradracmas + amount)
        elif singular == "decadracma":
            profile.decadracmas  = max(0, profile.decadracmas + amount)

        self.db.add(CoinsLog(
            user_id=self.user_id, coin_type=singular,
            amount=amount, reason=reason,
        ))
        self.db.commit()
        return True

    def apply_coin_dict(self, coin_dict: Dict[str, int], reason: str, subtract: bool = False):
        """Aplica un dict de monedas {plural_key: amount}. Si subtract=True, las resta."""
        for key, amount in coin_dict.items():
            self.add_coins(key, -amount if subtract else amount, reason)

    # ═══════════════════════════════════════════════════════════
    # RECOMPENSAS DIARIAS
    # ═══════════════════════════════════════════════════════════

    def reward_habit_completed(self, habit_name: str = "") -> Dict[str, Any]:
        xp = self.add_xp(XP_REWARDS["habit_completed"], f"Hábito: {habit_name}")
        self.apply_coin_dict(COIN_REWARDS["habit_completed"], f"Hábito: {habit_name}")
        return xp

    def reward_all_tasks_completed(self) -> Dict[str, Any]:
        xp = self.add_xp(XP_REWARDS["all_tasks_done"], "Todas las tareas completadas")
        self.apply_coin_dict(COIN_REWARDS["all_tasks_completed"], "Todas las tareas completadas")
        self.modify_wyrd(WYRD_GAINS["all_tasks_done"], "Día de tareas 100%")
        return xp

    def reward_perfect_day(self) -> Dict[str, Any]:
        xp = self.add_xp(XP_REWARDS["perfect_day"], "Día perfecto")
        self.apply_coin_dict(COIN_REWARDS["perfect_day"], "Día perfecto")
        return xp

    def reward_weekly_streak(self) -> Dict[str, Any]:
        xp = self.add_xp(XP_REWARDS["weekly_streak"], "Racha 7 días")
        self.apply_coin_dict(COIN_REWARDS["weekly_streak"], "Racha 7 días")
        self.modify_wyrd(WYRD_GAINS["weekly_streak"], "Racha semanal activa")
        return xp

    def reward_monthly_streak(self) -> Dict[str, Any]:
        xp = self.add_xp(XP_REWARDS["monthly_streak"], "Racha 30 días")
        self.apply_coin_dict(COIN_REWARDS["monthly_streak"], "Racha 30 días")
        return xp

    def reward_level_up(self) -> Dict[str, Any]:
        self.apply_coin_dict(COIN_REWARDS["level_up"], "Subida de nivel")
        return {"message": "Nivel subido", "coins": COIN_REWARDS["level_up"]}

    def reward_achievement(self, name: str = "") -> Dict[str, Any]:
        xp = self.add_xp(XP_REWARDS["achievement"], f"Logro: {name}")
        self.apply_coin_dict(COIN_REWARDS["achievement"], f"Logro: {name}")
        return xp

    # ═══════════════════════════════════════════════════════════
    # PENALIZACIONES
    # ═══════════════════════════════════════════════════════════

    def penalize_streak_broken(self) -> Dict[str, Any]:
        wyrd = self.modify_wyrd(-WYRD_PENALTIES["streak_broken"], "Racha rota")
        self.apply_coin_dict(COIN_PENALTIES["streak_broken"], "Racha rota", subtract=True)
        return wyrd

    def penalize_task_overdue(self) -> Dict[str, Any]:
        wyrd = self.modify_wyrd(-WYRD_PENALTIES["task_overdue"], "Tarea vencida")
        self.apply_coin_dict(COIN_PENALTIES["task_overdue"], "Tarea vencida", subtract=True)
        return wyrd

    def penalize_habit_missed(self) -> Dict[str, Any]:
        self.apply_coin_dict(COIN_PENALTIES["habit_missed"], "Hábito fallado", subtract=True)
        return {"penalized": True}

    # ═══════════════════════════════════════════════════════════
    # MALOS HÁBITOS
    # ═══════════════════════════════════════════════════════════

    def log_bad_habit(
        self,
        habit_type: str,
        covered: bool = False,
        source: str = "auto",
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Registra un mal hábito. Si covered=True (indulgencia activa), no aplica penalizaciones.
        Aplica penalización Wyrd + monedas según WYRD_PENALTIES y COIN_PENALTIES.
        """
        wyrd_penalty = WYRD_PENALTIES.get(habit_type, 10)
        coin_penalty = COIN_PENALTIES.get(habit_type, {})

        wyrd_result = None
        if not covered:
            wyrd_result = self.modify_wyrd(-wyrd_penalty, f"Mal hábito: {habit_type}")
            if coin_penalty:
                self.apply_coin_dict(coin_penalty, f"Penalización: {habit_type}", subtract=True)

        log = BadHabitLog(
            user_id=self.user_id,
            habit_type=habit_type,
            wyrd_lost=0 if covered else wyrd_penalty,
            coin_penalty_json=json.dumps(coin_penalty),
            covered_by_indulgencia=covered,
            notes=notes,
            source=source,
        )
        self.db.add(log)
        self.db.commit()

        return {
            "habit_type":  habit_type,
            "covered":     covered,
            "wyrd_lost":   0 if covered else wyrd_penalty,
            "wyrd_result": wyrd_result,
            "coins_lost":  {} if covered else coin_penalty,
        }

    # ═══════════════════════════════════════════════════════════
    # INDULGENCIAS
    # ═══════════════════════════════════════════════════════════

    def grant_indulgencias(self, count: int, reason: str = "") -> bool:
        """Añade tokens de indulgencia al perfil."""
        profile = self.get_or_create_profile()
        profile.indulgencias = max(0, profile.indulgencias + count)
        self.db.commit()
        return True

    def use_indulgencia(self, habit_type: str, ind_type: str, wyrd_to_recover: int = 0) -> Dict[str, Any]:
        """
        Consume una indulgencia del perfil para prevenir o absolver un mal hábito.
        ind_type: 'prevention' | 'absolution'
        """
        profile = self.get_or_create_profile()
        if profile.indulgencias <= 0:
            return {"success": False, "reason": "Sin indulgencias disponibles"}

        profile.indulgencias -= 1

        wyrd_result = None
        if ind_type == "absolution" and wyrd_to_recover > 0:
            wyrd_result = self.modify_wyrd(wyrd_to_recover, f"Absolución: {habit_type}")

        log = IndulgenciaLog(
            user_id=self.user_id,
            habit_type=habit_type,
            type=ind_type,
            cost_json=json.dumps({"indulgencias": 1}),
            wyrd_recovered=wyrd_to_recover if ind_type == "absolution" else 0,
        )
        self.db.add(log)
        self.db.commit()

        return {
            "success":       True,
            "indulgencias_left": profile.indulgencias,
            "wyrd_result":   wyrd_result,
        }

    # ═══════════════════════════════════════════════════════════
    # ARTEFACTOS
    # ═══════════════════════════════════════════════════════════

    def get_market_artifacts(self) -> List[Artifact]:
        return self.db.query(Artifact).filter(Artifact.active == True).all()

    def get_user_artifacts(self) -> List[UserArtifact]:
        return self.db.query(UserArtifact).filter(
            UserArtifact.user_id == self.user_id
        ).all()

    def grant_artifact(self, artifact_id: str, source: str = "dice_combo") -> UserArtifact:
        """Añade un artefacto al inventario del usuario (obtenido por combo de dados)."""
        ua = UserArtifact(
            user_id=self.user_id,
            artifact_id=artifact_id,
            source=source,
            uses_left=1,
        )
        self.db.add(ua)
        self.db.commit()
        self.db.refresh(ua)
        return ua

    # ═══════════════════════════════════════════════════════════
    # HELPERS INTERNOS
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _hero_for_level(level: int) -> Dict[str, str]:
        hero_level = 1
        for lvl in sorted(HEROES.keys()):
            if level >= lvl:
                hero_level = lvl
        return HEROES[hero_level]

    @staticmethod
    def _wyrd_state(wyrd: int) -> Dict[str, str]:
        states = [
            (80, 100, "CRUZANDO",    "🟢", "Caronte te abre paso."),
            (50,  79, "A FLOTE",     "🟡", "Navegas, pero la corriente tira."),
            (30,  49, "A LA DERIVA", "🟠", "El río te arrastra hacia las sombras."),
            (10,  29, "HUNDIÉNDOTE", "🔴", "Las aguas te reclaman. Actúa ya."),
            (0,    9, "VAGANDO",     "💀", "100 años sin cruzar. El Lete te espera."),
        ]
        for mn, mx, name, emoji, desc in states:
            if mn <= wyrd <= mx:
                return {"name": name, "emoji": emoji, "desc": desc}
        return {"name": "VAGANDO", "emoji": "💀", "desc": "El Lete te espera."}

    @staticmethod
    def _xp_for_next_level(level: int, current_xp: int) -> int:
        levels = sorted(LEVEL_XP.keys())
        for lvl in levels:
            if lvl > level:
                return LEVEL_XP[lvl] - current_xp
        return 0  # nivel máximo
