# 🐛 BUGS TRACKING - Life Assistant V4

**Última actualización:** 07/03/2026 22:15 CET

---

## 🔴 BUGS CRÍTICOS (Bloquean funcionalidad)

### BUG-V4-001: Conflicto tabla `user_artifacts`

**Estado:** 🔴 ABIERTO  
**Prioridad:** CRÍTICA  
**Detectado:** 07/03/2026  
**Afecta a:** Sistema RPG, Artefactos, Dados

**Descripción:**
- `src/core/rpg_models.py` define `UserArtifact` con `__tablename__ = "user_artifacts"`
- Código generado crea tabla con SQL raw y esquema diferente
- Conflicto de schema causa `OperationalError` en runtime

**Solución:**
```python
# Reemplazar INSERT raw SQL por:
from src.core.rpg_models import UserArtifact

artifact_record = UserArtifact(
    user_id=user_id,
    artifact_id=artifact["id"],
    uses_left=1
)
db.add(artifact_record)
```

**Archivos afectados:**
- `src/core/rpg_models.py`
- `dice_system.py` (si existe en raíz)
- Cualquier código que use SQL raw para `user_artifacts`

**Tiempo estimado:** 30 minutos

---

### BUG-V4-002: Import inexistente `gamification.py`

**Estado:** 🔴 ABIERTO  
**Prioridad:** CRÍTICA  
**Detectado:** 07/03/2026  
**Afecta a:** Sistema de dados, Indulgencias, Recompensas

**Descripción:**
```python
from gamification import add_coins, add_wyrd, add_xp
# ModuleNotFoundError: No module named 'gamification'
```

En V4, estas funciones son métodos de `RPGService` en `src/services/rpg.py`.

**Solución:**
```python
from src.services.rpg import RPGService

def apply_combo_rewards(db: Session, user_id: int, combo, streak_multiplier=1.0):
    rpg = RPGService(db, user_id)
    
    if rewards["xp"] > 0:
        rpg.add_xp(rewards["xp"], f"Combo: {combo.value}")
    
    if rewards["obolos"] > 0:
        rpg.add_coins("obolo", rewards["obolos"], f"Combo: {combo.value}")
```

**Archivos afectados:**
- `dice_system.py`
- `gamification_updated.py` (si existe)
- Cualquier código que importe de `gamification`

**Tiempo estimado:** 45 minutos

---

### BUG-V4-003: Monedas singular vs plural

**Estado:** 🔴 ABIERTO  
**Prioridad:** CRÍTICA  
**Detectado:** 07/03/2026  
**Afecta a:** Sistema de recompensas, Monedas

**Descripción:**
- `RPGService.add_coins()` espera: `"obolo"`, `"dracma"` (singular)
- `COIN_REWARDS` usa: `"obolos"`, `"dracmas"` (plural)
- Resultado: Monedas no se añaden silenciosamente (sin error visible)

**Solución:**
Añadir normalización en `src/services/rpg.py`:

```python
_NORMALIZE = {
    "obolos": "obolo",
    "dracmas": "dracma",
    "tetradracmas": "tetradracma",
    "decadracmas": "decadracma"
}

def add_coins(self, coin_type: str, amount: int, reason: str = "") -> bool:
    coin_type = _NORMALIZE.get(coin_type, coin_type)  # ← añadir
    # ... resto del código
```

**Archivos afectados:**
- `src/services/rpg.py`
- Cualquier código que llame a `add_coins()` con plural

**Tiempo estimado:** 15 minutos

---

### BUG-V4-004: Tablas sin modelo ORM

**Estado:** 🔴 ABIERTO  
**Prioridad:** CRÍTICA  
**Detectado:** 07/03/2026  
**Afecta a:** Sistema de dados, Indulgencias, Logs

**Descripción:**
- Tablas `indulgencias_log` y `dice_roll_log` se usan en código
- No están definidas como modelos ORM
- `init_db.py` no las crea → `OperationalError: no such table`

**Solución:**
Añadir a `src/core/rpg_models.py`:

```python
class IndulgenciaLog(Base):
    __tablename__ = "indulgencias_log"
    
    id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, nullable=False)
    habit_type     = Column(String, nullable=False)
    type           = Column(String, nullable=False)   # prevention | absolution
    cost_json      = Column(Text)
    wyrd_recovered = Column(Integer, default=0)
    created_at     = Column(DateTime, default=datetime.utcnow)

class DiceRollLog(Base):
    __tablename__ = "dice_roll_log"
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, nullable=False)
    dice_count  = Column(Integer)
    roll_result = Column(Text)    # JSON
    combo       = Column(String)
    rewards_json= Column(Text)    # JSON
    artifact_id = Column(String)
    created_at  = Column(DateTime, default=datetime.utcnow)
```

**Archivos afectados:**
- `src/core/rpg_models.py`
- `init_db.py` (regenerar con `python init_db.py`)

**Tiempo estimado:** 20 minutos

---

## 🟡 ISSUES MEDIOS (No bloquean pero causan inconsistencias)

### ISSUE-V4-001: Dos RPG Services distintos

**Estado:** 🟡 ABIERTO  
**Prioridad:** MEDIA  
**Detectado:** 07/03/2026

**Descripción:**
Existen dos implementaciones:
1. `src/services/rpg.py` (ORM, V4)
2. `rpg_service_new.py` (raw SQL, V3)

**Decisión:**
Usar solo `src/services/rpg.py`. Migrar métodos nuevos y descartar `rpg_service_new.py`.

**Tiempo estimado:** 1 hora

---

### ISSUE-V4-002: Fórmula de nivel inconsistente

**Estado:** 🟡 ABIERTO  
**Prioridad:** MEDIA-ALTA  
**Detectado:** 07/03/2026

**Descripción:**
- `rpg.py` usa fórmula sqrt: nivel 10 = 10.000 XP
- `constants.py` usa tabla: nivel 10 = 1.500 XP

**Solución:**
Usar tabla `LEVEL_XP` en lugar de fórmula.

**Tiempo estimado:** 20 minutos

---

### ISSUE-V4-003: `BadHabitLog` duplicado

**Estado:** 🟡 ABIERTO  
**Prioridad:** MEDIA  
**Detectado:** 07/03/2026

**Descripción:**
- `bad_habits_log` (motor automático)
- `bad_habit_logs` (registro manual web)

**Solución:**
Unificar en una tabla con columna `source`.

**Tiempo estimado:** 30 minutos

---

### ISSUE-V4-004: Dos `dice_system.py` distintos

**Estado:** 🟡 ABIERTO  
**Prioridad:** MEDIA  
**Detectado:** 07/03/2026

**Descripción:**
- `src/core/dice_system.py` → D&D (D4, D6, D20)
- `dice_system.py` (raíz) → Caronte (combos poker)

**Solución:**
Renombrar nuevo como `src/services/caronte_dice.py`.

**Tiempo estimado:** 10 minutos

---

### ISSUE-V4-005: Falta columna `indulgencias` en `UserProfile`

**Estado:** 🟡 ABIERTO  
**Prioridad:** MEDIA-ALTA  
**Detectado:** 07/03/2026

**Descripción:**
Código hace `UPDATE user_profile SET indulgencias = ...` pero la columna no existe.

**Solución:**
Añadir a modelo:
```python
indulgencias = Column(Integer, default=0)
```

**Tiempo estimado:** 10 minutos + migración Alembic

---

## 🟢 BUGS RESUELTOS

_(Vacío - ningún bug resuelto todavía)_

---

## 📊 RESUMEN

| Prioridad | Abiertos | Resueltos | Total |
|-----------|----------|-----------|-------|
| 🔴 CRÍTICA | 4 | 0 | 4 |
| 🟡 MEDIA | 5 | 0 | 5 |
| 🟢 BAJA | 0 | 0 | 0 |
| **TOTAL** | **9** | **0** | **9** |

**Tiempo estimado total bugs críticos:** ~2 horas  
**Tiempo estimado total issues medios:** ~2.5 horas

---

## 🎯 PLAN DE ACCIÓN RECOMENDADO

### Sesión 1 (1-2h): Bugs críticos
1. BUG-V4-003 (15 min) - Más rápido
2. BUG-V4-004 (20 min) - Modelos ORM
3. BUG-V4-001 (30 min) - user_artifacts
4. BUG-V4-002 (45 min) - Imports

### Sesión 2 (2-3h): Issues medios
1. ISSUE-V4-005 (10 min)
2. ISSUE-V4-004 (10 min)
3. ISSUE-V4-002 (20 min)
4. ISSUE-V4-003 (30 min)
5. ISSUE-V4-001 (1h)

---

**Próxima revisión:** Tras arreglar bugs críticos
