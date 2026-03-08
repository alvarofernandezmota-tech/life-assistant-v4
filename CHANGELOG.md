# 📜 CHANGELOG - Life Assistant V4

Todos los cambios importantes del proyecto se documentan aquí.

---

## [1.5.0] - 2026-03-08

### 🎉 FASE 1.5 COMPLETA - Bugs Fixed + Dashboard Funcional

#### Añadido

##### Frontend Web
- ✅ `frontend/index.html`: Dashboard HTML funcional completo
  - Lista de tareas con checkboxes
  - Lista de hábitos con botón completar
  - Lista de eventos del día
  - Stats RPG en tiempo real (nivel, XP, oro)
  - Conectado completamente a API
  - Diseño responsive con Tailwind CSS
  - Fetch API para comunicación con backend

##### Scripts & Tools
- ✅ `run.py`: Launcher unificado para Windows/Ubuntu
  - Configura PYTHONPATH automáticamente
  - Lanza uvicorn con reload
  - Compatible con WSL2

##### Documentación
- ✅ README.md actualizado con frontend info
- ✅ STATUS.md con estado completo 8 Mar 2026
- ✅ TODO.md actualizado con nuevas prioridades
- ✅ QUICKSTART.md con frontend instructions
- ✅ diary/2026-03-08.md: Sesión de hoy documentada

#### Corregido

##### Bugs Críticos
- ✅ **ImportError**: `attempted relative import beyond top-level package`
  - Solución: `run.py` con PYTHONPATH
  - Afectaba: init_db.py, uvicorn start
  
- ✅ **ModuleNotFoundError**: `No module named 'src'`
  - Solución: sys.path.insert en run.py
  - Permite ejecutar desde cualquier directorio

- ✅ **Conflicto dependencias**: httpx==0.26.0 vs python-telegram-bot
  - Solución: Usar httpx~=0.25.2 compatible
  - requirements.txt no necesario con instalación manual core

##### Bugs Menores
- ✅ init_db.py ahora importa correctamente desde src
- ✅ uvicorn command not found: usar python -m uvicorn o run.py
- ✅ Database path relativo arreglado

#### Cambiado

##### Estructura
- 🔄 `init_db.py`: Simplificado, imports desde src.core
- 🔄 Instalación: Ya no requiere requirements.txt completo
- 🔄 Dependencias core instaladas manualmente

##### Configuración
- 🔄 Entorno virtual opcional (puede usar Python global)
- 🔄 API accesible desde Windows en WSL2 (localhost:8000)

#### Desplegado

##### Producción
- 🚀 Backend desplegado en Ubuntu (WSL2)
- 🚀 Base de datos inicializada con 12 artefactos
- 🚀 API corriendo en http://localhost:8000
- 🚀 Frontend accesible vía navegador
- 🚀 Tests manuales: ✅ Todos los endpoints funcionan

---

## [4.0.0] - 2026-03-07

### 🚀 FASE 1 COMPLETA - Estructura Base (21:00 CET)

#### Añadido

##### Estructura y Documentación
- ✅ Estructura completa V4 profesional con 13 carpetas
- ✅ README.md (400+ líneas) con documentación completa
- ✅ ROADMAP.md con 24 tareas priorizadas en 6 fases
- ✅ CHANGELOG.md (este archivo)
- ✅ STATUS.md con estado del proyecto
- ✅ docs/API.md con documentación REST completa
- ✅ .gitignore (Python, DB, logs, .env)
- ✅ .env.example con template de variables
- ✅ requirements.txt con 25 dependencias

##### Core System
- ✅ `src/config/settings.py`: Configuración centralizada desde .env
- ✅ `src/core/database.py`: Conexión SQLite + SQLAlchemy limpia
- ✅ `src/core/models.py`: 8 modelos core refactorizados
  - Habit, HabitLog, Task, Event, Diary, Mood, Goal, Reminder, ChatMsg
- ✅ `src/core/rpg_models.py`: 13 modelos RPG separados
  - UserProfile, XPLog, WyrdLog, CoinsLog, Artifact, UserArtifact
  - Achievement, HeroUnlock, BadHabitLog, DailyCheck, GameOverLog, RewardClaim, RPGLog
- ✅ `src/core/dice_system.py`: Sistema completo de dados D&D
  - DiceType (D4, D6, D8, D10, D12, D20, D100)
  - RollResult con advantage/disadvantage
  - Parser de notación ("2d6+3")
- ✅ `src/core/utils.py`: 7 funciones auxiliares
  - to_dict, week_range, expand_events, calc_streak
  - format_weekday, get_daily_summary, format_daily_summary_text
- ✅ `src/core/__init__.py`: Exports completos de core

##### Services (Migrados desde V3)
- ✅ `src/services/habits.py`: Service completo de hábitos
  - CRUD completo (create, read, update, delete)
  - mark_completed con soporte de fechas
  - Estadísticas y rachas
  - Filtros por grupo
- ✅ `src/services/tasks.py`: Service completo de tareas
  - CRUD completo
  - Filtros por estado, prioridad, categoría, fecha
  - Tareas vencidas
  - Operaciones de postpone
  - Estadísticas
- ✅ `src/services/events.py`: Service completo de eventos
  - CRUD completo
  - Soporte de eventos recurrentes (daily, weekly, weekdays)
  - Expansión de recurrencias
  - Filtros por rango de fechas
- ✅ `src/services/rpg.py`: Service completo sistema Caronte
  - Gestión de perfil (get_or_create_profile)
  - Sistema XP y leveling
  - Sistema Wyrd (vida/destino 0-100)
  - Sistema monedas (obolos, dracmas, tetradracmas, decadracmas)
  - Artefactos míticos
  - Log de malos hábitos con penalizaciones
- ✅ `src/services/__init__.py`: Exports de servicios

##### Scripts y Tests
- ✅ `init_db.py`: Script de inicialización con seed de artefactos
  - Crea todas las tablas
  - Inserta 10 artefactos míticos iniciales
- ✅ `tests/test_database.py`: Tests básicos de conexión
  - test_connection
  - test_create_habit
  - test_create_task
  - test_user_profile
  - test_get_db_dependency

#### Mejoras sobre V3

- 🔧 **Modularización total**: Database, models, services separados
- 🔧 **Configuración**: Settings.py centralizado con .env
- 🔧 **Services refactorizados**: Sin dependencias de constants.py
- 🔧 **RPG separado**: Modelos y service independientes
- 🔧 **Utilidades**: Funciones auxiliares en utils.py
- 🔧 **Documentación**: 5 archivos de docs completos
- 🔧 **Tests**: Suite básica de pytest

#### Cambios Técnicos

- Eliminadas dependencias circulares
- Imports relativos (..core, ..config)
- Type hints en todos los services
- Docstrings completos
- Compatibilidad Python 3.11+

---

## [3.0.0] - 2026-02 (Referencia V3)

### Lo que funcionaba en V3
- ✅ CRUD Hábitos completo (9/10)
- ✅ CRUD Tareas completo (9/10)
- ✅ CRUD Eventos completo (9/10)
- ✅ Base de datos robusta (20+ tablas)
- ✅ API FastAPI funcional (40+ endpoints)
- ✅ Bot Telegram básico
- ✅ Sistema RPG Caronte parcial
- ✅ Documentación excelente

### Problemas identificados en V3
- ❌ Frontend web muy básico (2/10)
- ❌ Sin CSS ni JavaScript
- ❌ Código monolítico (main.py 500+ líneas)
- ❌ Bot Telegram básico (6/10)
- ❌ Diario no implementado
- ❌ Dados no integrados

---

## 📅 Próximas Versiones

### [1.6.0] - Próximamente
- [ ] Calendario FullCalendar.js integrado
- [ ] Gráficos de estadísticas
- [ ] Tema mitológico visual completo

### [2.0.0] - Bot Telegram
- [ ] Bot completo con comandos
- [ ] Notificaciones push
- [ ] Gestión desde móvil

---

## Formato

Este CHANGELOG sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto usa [Semantic Versioning](https://semver.org/lang/es/).

### Tipos de cambios

- **Añadido** (`Added`): Nuevas funcionalidades
- **Cambiado** (`Changed`): Cambios en funcionalidades existentes
- **Obsoleto** (`Deprecated`): Funcionalidades que se eliminarán pronto
- **Eliminado** (`Removed`): Funcionalidades eliminadas
- **Corregido** (`Fixed`): Corrección de bugs
- **Seguridad** (`Security`): Vulnerabilidades corregidas
- **Desplegado** (`Deployed`): Cambios en producción
