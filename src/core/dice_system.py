"""
dice_system.py - Sistema de dados completo (D&D style)
Migrado desde V3 sin cambios
"""
import random
from typing import List, Tuple, Optional
from enum import Enum

class DiceType(Enum):
    """Tipos de dados disponibles"""
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20
    D100 = 100

class RollResult:
    """Resultado de una tirada de dados"""
    
    def __init__(self, rolls: List[int], total: int, dice_type: DiceType, num_dice: int, 
                 modifier: int = 0, advantage: bool = False, disadvantage: bool = False):
        self.rolls = rolls
        self.total = total
        self.dice_type = dice_type
        self.num_dice = num_dice
        self.modifier = modifier
        self.advantage = advantage
        self.disadvantage = disadvantage
    
    def __str__(self) -> str:
        mod_str = f" + {self.modifier}" if self.modifier > 0 else f" - {abs(self.modifier)}" if self.modifier < 0 else ""
        adv_str = " (Ventaja)" if self.advantage else " (Desventaja)" if self.disadvantage else ""
        return f"{self.num_dice}d{self.dice_type.value}{mod_str}{adv_str} = {self.rolls} → Total: {self.total}"
    
    def to_dict(self) -> dict:
        return {
            "rolls": self.rolls,
            "total": self.total,
            "dice_type": self.dice_type.value,
            "num_dice": self.num_dice,
            "modifier": self.modifier,
            "advantage": self.advantage,
            "disadvantage": self.disadvantage,
            "formatted": str(self)
        }

class DiceSystem:
    """Sistema completo de dados"""
    
    @staticmethod
    def roll(dice_type: DiceType, num_dice: int = 1, modifier: int = 0, 
             advantage: bool = False, disadvantage: bool = False) -> RollResult:
        """
        Tira dados con modificadores opcionales
        
        Args:
            dice_type: Tipo de dado (D4, D6, D8, D10, D12, D20, D100)
            num_dice: Número de dados a tirar
            modifier: Modificador a añadir al resultado
            advantage: Si True, tira 2 dados y toma el mayor
            disadvantage: Si True, tira 2 dados y toma el menor
        
        Returns:
            RollResult con los detalles de la tirada
        """
        if advantage and disadvantage:
            raise ValueError("No puedes tener ventaja y desventaja a la vez")
        
        rolls = []
        
        if advantage or disadvantage:
            # Tirar 2 veces para ventaja/desventaja
            roll1 = random.randint(1, dice_type.value)
            roll2 = random.randint(1, dice_type.value)
            
            if advantage:
                result = max(roll1, roll2)
            else:  # disadvantage
                result = min(roll1, roll2)
            
            rolls = [roll1, roll2]
            total = result + modifier
        else:
            # Tirada normal
            rolls = [random.randint(1, dice_type.value) for _ in range(num_dice)]
            total = sum(rolls) + modifier
        
        return RollResult(rolls, total, dice_type, num_dice, modifier, advantage, disadvantage)
    
    @staticmethod
    def roll_d20(modifier: int = 0, advantage: bool = False, disadvantage: bool = False) -> RollResult:
        """Atajo para tirar 1d20 (más común en D&D)"""
        return DiceSystem.roll(DiceType.D20, 1, modifier, advantage, disadvantage)
    
    @staticmethod
    def check_success(dc: int, result: RollResult) -> Tuple[bool, int]:
        """
        Comprueba si una tirada supera una DC (Difficulty Class)
        
        Args:
            dc: Dificultad a superar
            result: Resultado de la tirada
        
        Returns:
            (success: bool, margin: int) - Éxito y margen (positivo si supera, negativo si falla)
        """
        success = result.total >= dc
        margin = result.total - dc
        return success, margin
    
    @staticmethod
    def parse_dice_notation(notation: str) -> Tuple[DiceType, int, int]:
        """
        Parsea notación de dados estándar (ej: "2d6+3", "1d20-2", "3d8")
        
        Returns:
            (dice_type, num_dice, modifier)
        """
        import re
        
        # Pattern: XdY+Z o XdY-Z o XdY
        pattern = r"(\d+)d(\d+)([+-]\d+)?"
        match = re.match(pattern, notation.lower().strip())
        
        if not match:
            raise ValueError(f"Notación inválida: {notation}")
        
        num_dice = int(match.group(1))
        dice_value = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        # Mapear valor a DiceType
        dice_map = {4: DiceType.D4, 6: DiceType.D6, 8: DiceType.D8, 
                    10: DiceType.D10, 12: DiceType.D12, 20: DiceType.D20, 100: DiceType.D100}
        
        if dice_value not in dice_map:
            raise ValueError(f"Tipo de dado no soportado: d{dice_value}")
        
        return dice_map[dice_value], num_dice, modifier

# Funciones de conveniencia
def roll_dice(notation: str, advantage: bool = False, disadvantage: bool = False) -> RollResult:
    """Tira dados usando notación estándar (ej: '2d6+3')"""
    dice_type, num_dice, modifier = DiceSystem.parse_dice_notation(notation)
    return DiceSystem.roll(dice_type, num_dice, modifier, advantage, disadvantage)

def roll_d20(modifier: int = 0, advantage: bool = False, disadvantage: bool = False) -> RollResult:
    """Atajo para 1d20"""
    return DiceSystem.roll_d20(modifier, advantage, disadvantage)