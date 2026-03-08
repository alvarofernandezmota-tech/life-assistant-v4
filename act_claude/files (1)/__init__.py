"""
Core module - Database, Models, Dice System, Utils
"""
from .database import get_db, get_db_connection, SessionLocal, Base, init_db

from .models import (
    Habit, HabitLog, Task, Event, Diary,
    Mood, Goal, Reminder, ChatMsg
)

from .rpg_models import (
    UserProfile, XPLog, WyrdLog, CoinsLog,
    Artifact, UserArtifact,
    Achievement, HeroUnlock,
    BadHabitLog, DailyCheck,
    GameOverLog, RewardClaim, RPGLog,
    DiceRollLog, IndulgenciaLog,       # ← nuevos
)

from .dice_system import (
    DiceType, DiceSystem, RollResult,
    roll_dice, roll_d20
)

from .utils import (
    to_dict, week_range, expand_events,
    calc_streak, format_weekday,
    get_daily_summary, format_daily_summary_text
)

__all__ = [
    # Database
    "get_db", "get_db_connection", "SessionLocal", "Base", "init_db",
    # Core Models
    "Habit", "HabitLog", "Task", "Event", "Diary",
    "Mood", "Goal", "Reminder", "ChatMsg",
    # RPG Models
    "UserProfile", "XPLog", "WyrdLog", "CoinsLog",
    "Artifact", "UserArtifact",
    "Achievement", "HeroUnlock",
    "BadHabitLog", "DailyCheck",
    "GameOverLog", "RewardClaim", "RPGLog",
    "DiceRollLog", "IndulgenciaLog",
    # D&D Dice System (distinto del sistema Caronte)
    "DiceType", "DiceSystem", "RollResult", "roll_dice", "roll_d20",
    # Utils
    "to_dict", "week_range", "expand_events",
    "calc_streak", "format_weekday",
    "get_daily_summary", "format_daily_summary_text",
]
