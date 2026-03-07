"""
rpg.py - RPG Service (Sistema Caronte)
Migrado y refactorizado desde V3
"""
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.rpg_models import (
    UserProfile, XPLog, WyrdLog, CoinsLog,
    Artifact, UserArtifact, Achievement, BadHabitLog, DailyCheck
)
from ..config.settings import settings

class RPGService:
    """
    Service para el sistema de gamificación RPG (Caronte)
    
    Métodos:
    - Gestión de perfil (nivel, XP, Wyrd)
    - Sistema de monedas (Obolos, Dracmas, Tetradracmas, Decadracmas)
    - Artefactos míticos
    - Logros y héroes
    - Penalizaciones por malos hábitos
    """
    
    def __init__(self, db: Session, user_id: int = None):
        self.db = db
        self.user_id = user_id or settings.DEFAULT_USER_ID
    
    # ═══════════════════════════════════════════════════════════════
    # PROFILE
    # ═══════════════════════════════════════════════════════════════
    
    def get_or_create_profile(self) -> UserProfile:
        """
        Obtiene el perfil RPG del usuario o lo crea si no existe
        
        Returns:
            UserProfile del usuario
        """
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == self.user_id
        ).first()
        
        if not profile:
            profile = UserProfile(
                user_id=self.user_id,
                level=settings.STARTING_LEVEL,
                xp=settings.STARTING_XP,
                wyrd=settings.STARTING_WYRD,
                hero="Alma Errante"
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        
        return profile
    
    def get_profile_dict(self) -> Dict[str, Any]:
        """Obtiene perfil como diccionario"""
        profile = self.get_or_create_profile()
        return {
            "user_id": profile.user_id,
            "level": profile.level,
            "xp": profile.xp,
            "wyrd": profile.wyrd,
            "obolos": profile.obolos,
            "dracmas": profile.dracmas,
            "tetradracmas": profile.tetradracmas,
            "decadracmas": profile.decadracmas,
            "hero": profile.hero,
            "streak": profile.streak
        }
    
    # ═══════════════════════════════════════════════════════════════
    # XP & LEVELING
    # ═══════════════════════════════════════════════════════════════
    
    def add_xp(self, amount: int, reason: str = "") -> Dict[str, Any]:
        """
        Añade XP al usuario y verifica si subió de nivel
        
        Args:
            amount: Cantidad de XP a añadir
            reason: Razón del XP ganado
        
        Returns:
            Dict con nivel_anterior, nivel_nuevo, xp_total, leveled_up
        """
        profile = self.get_or_create_profile()
        old_level = profile.level
        
        profile.xp += amount
        
        # Fórmula de nivel: nivel = floor(sqrt(xp / 100))
        new_level = int((profile.xp / 100) ** 0.5)
        if new_level < 1:
            new_level = 1
        
        leveled_up = new_level > old_level
        profile.level = new_level
        
        # Log XP
        log = XPLog(
            user_id=self.user_id,
            amount=amount,
            reason=reason
        )
        self.db.add(log)
        
        self.db.commit()
        self.db.refresh(profile)
        
        return {
            "old_level": old_level,
            "new_level": new_level,
            "xp_total": profile.xp,
            "leveled_up": leveled_up
        }
    
    # ═══════════════════════════════════════════════════════════════
    # WYRD (VIDA/DESTINO)
    # ═══════════════════════════════════════════════════════════════
    
    def modify_wyrd(self, amount: int, reason: str = "") -> Dict[str, Any]:
        """
        Modifica el Wyrd (puede ser positivo o negativo)
        
        Args:
            amount: Cantidad a modificar (positivo = aumentar, negativo = reducir)
            reason: Razón del cambio
        
        Returns:
            Dict con wyrd_before, wyrd_after, game_over
        """
        profile = self.get_or_create_profile()
        wyrd_before = profile.wyrd
        
        profile.wyrd += amount
        
        # Limitar entre 0 y 100
        if profile.wyrd > 100:
            profile.wyrd = 100
        elif profile.wyrd < 0:
            profile.wyrd = 0
        
        wyrd_after = profile.wyrd
        game_over = (wyrd_after == 0)
        
        # Log Wyrd
        log = WyrdLog(
            user_id=self.user_id,
            amount=amount,
            reason=reason,
            wyrd_before=wyrd_before,
            wyrd_after=wyrd_after
        )
        self.db.add(log)
        
        self.db.commit()
        self.db.refresh(profile)
        
        return {
            "wyrd_before": wyrd_before,
            "wyrd_after": wyrd_after,
            "game_over": game_over
        }
    
    # ═══════════════════════════════════════════════════════════════
    # COINS
    # ═══════════════════════════════════════════════════════════════
    
    def add_coins(
        self,
        coin_type: str,
        amount: int,
        reason: str = ""
    ) -> bool:
        """
        Añade monedas al usuario
        
        Args:
            coin_type: obolo, dracma, tetradracma, decadracma
            amount: Cantidad a añadir
            reason: Razón
        
        Returns:
            True si exitoso
        """
        profile = self.get_or_create_profile()
        
        if coin_type == "obolo":
            profile.obolos += amount
        elif coin_type == "dracma":
            profile.dracmas += amount
        elif coin_type == "tetradracma":
            profile.tetradracmas += amount
        elif coin_type == "decadracma":
            profile.decadracmas += amount
        else:
            return False
        
        # Log monedas
        log = CoinsLog(
            user_id=self.user_id,
            coin_type=coin_type,
            amount=amount,
            reason=reason
        )
        self.db.add(log)
        
        self.db.commit()
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # ARTIFACTS
    # ═══════════════════════════════════════════════════════════════
    
    def get_market_artifacts(self) -> List[Artifact]:
        """Obtiene todos los artefactos disponibles en el mercado"""
        return self.db.query(Artifact).filter(Artifact.active == True).all()
    
    def get_user_artifacts(self) -> List[UserArtifact]:
        """Obtiene artefactos comprados por el usuario"""
        return self.db.query(UserArtifact).filter(
            UserArtifact.user_id == self.user_id
        ).all()
    
    # ═══════════════════════════════════════════════════════════════
    # BAD HABITS
    # ═══════════════════════════════════════════════════════════════
    
    def log_bad_habit(
        self,
        habit_type: str,
        wyrd_penalty: int = 10
    ) -> Dict[str, Any]:
        """
        Registra un mal hábito y aplica penalización de Wyrd
        
        Args:
            habit_type: smoking, drinking, junk_food, etc.
            wyrd_penalty: Cantidad de Wyrd a perder
        
        Returns:
            Dict con resultado de la penalización
        """
        # Registrar mal hábito
        log = BadHabitLog(
            user_id=self.user_id,
            habit_type=habit_type,
            wyrd_lost=wyrd_penalty
        )
        self.db.add(log)
        
        # Aplicar penalización de Wyrd
        result = self.modify_wyrd(-wyrd_penalty, f"Mal hábito: {habit_type}")
        
        self.db.commit()
        return result