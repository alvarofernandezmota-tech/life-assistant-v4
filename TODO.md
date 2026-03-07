# ✅ TODO - Life Assistant V4

**Última actualización:** 07/03/2026 22:15 CET

---

## 🔴 PRIORIDAD 1: Bugs Críticos (1-2h)

**Estado:** ⏳ PENDIENTE  
**Debe completarse antes de:** FASE 2 (API)

### Tareas

- [ ] **BUG-V4-003:** Normalizar monedas plural→singular (15 min)
  - Archivo: `src/services/rpg.py`
  - Añadir diccionario `_NORMALIZE`
  - Modificar método `add_coins()`

- [ ] **BUG-V4-004:** Crear modelos ORM logs (20 min)
  - Archivo: `src/core/rpg_models.py`
  - Añadir `IndulgenciaLog`
  - Añadir `DiceRollLog`
  - Regenerar DB con `python init_db.py`

- [ ] **BUG-V4-001:** Unificar tabla `user_artifacts` (30 min)
  - Eliminar SQL raw de archivos generados
  - Usar modelo ORM `UserArtifact`
  - Verificar `init_db.py` funciona

- [ ] **BUG-V4-002:** Reescribir imports `gamification` (45 min)
  - Archivo: `dice_system.py` (si existe)
  - Reemplazar por `RPGService`
  - Actualizar todas las llamadas
  - Testear sistema de dados

**Tiempo total estimado:** 1h 50min

---

## 🟡 PRIORIDAD 2: Issues Medios (2-3h)

**Estado:** ⏳ PENDIENTE  
**Puede hacerse después de:** Bugs críticos

### Tareas

- [ ] **ISSUE-V4-005:** Añadir columna `indulgencias` (10 min)
  - Archivo: `src/core/rpg_models.py`
  - Añadir: `indulgencias = Column(Integer, default=0)`
  - Configurar Alembic para migración

- [ ] **ISSUE-V4-004:** Renombrar `dice_system.py` Caronte (10 min)
  - Mover a: `src/services/caronte_dice.py`
  - Actualizar imports

- [ ] **ISSUE-V4-002:** Alinear fórmula de nivel (20 min)
  - Archivo: `src/services/rpg.py`
  - Usar tabla `LEVEL_XP` en vez de sqrt
  - Testear subidas de nivel

- [ ] **ISSUE-V4-003:** Unificar `BadHabitLog` (30 min)
  - Decidir tabla única
  - Añadir columna `source` (web/telegram/auto)
  - Migrar datos existentes

- [ ] **ISSUE-V4-001:** Consolidar RPG Services (1h)
  - Decidir: usar solo `src/services/rpg.py`
  - Migrar métodos útiles de `rpg_service_new.py`
  - Eliminar archivos duplicados
  - Actualizar imports en todo el proyecto

**Tiempo total estimado:** 2h 10min

---

## 🚀 PRIORIDAD 3: FASE 2 - API REST (3-4h)

**Estado:** ⏳ PENDIENTE  
**Debe completarse antes de:** FASE 3 (Frontend)

### Estructura Base

- [ ] Crear `src/api/main.py` con FastAPI app (30 min)
  - Inicializar FastAPI
  - Configurar CORS
  - Configurar Swagger UI
  - Dependency injection DB

### Routers

- [ ] `src/api/routers/habits.py` (45 min)
  - GET `/habits` - Lista
  - GET `/habits/{id}` - Detalle
  - POST `/habits` - Crear
  - PUT `/habits/{id}` - Actualizar
  - DELETE `/habits/{id}` - Eliminar
  - POST `/habits/{id}/complete` - Marcar completado
  - GET `/habits/stats` - Estadísticas

- [ ] `src/api/routers/tasks.py` (45 min)
  - GET `/tasks` - Lista con filtros
  - GET `/tasks/{id}` - Detalle
  - POST `/tasks` - Crear
  - PUT `/tasks/{id}` - Actualizar
  - DELETE `/tasks/{id}` - Eliminar
  - POST `/tasks/{id}/complete` - Completar
  - GET `/tasks/overdue` - Vencidas
  - GET `/tasks/stats` - Estadísticas

- [ ] `src/api/routers/events.py` (30 min)
  - GET `/events` - Lista con filtros
  - GET `/events/{id}` - Detalle
  - POST `/events` - Crear
  - PUT `/events/{id}` - Actualizar
  - DELETE `/events/{id}` - Eliminar
  - GET `/events/today` - De hoy

- [ ] `src/api/routers/rpg.py` (1h)
  - GET `/rpg/profile` - Perfil usuario
  - POST `/rpg/xp` - Añadir XP
  - POST `/rpg/wyrd` - Modificar Wyrd
  - POST `/rpg/coins` - Añadir monedas
  - GET `/rpg/market` - Artefactos disponibles
  - POST `/rpg/market/{id}/buy` - Comprar artefacto
  - GET `/rpg/artifacts` - Artefactos usuario
  - POST `/rpg/dice-roll` - Tirada dados nocturna

- [ ] `src/api/routers/dashboard.py` (30 min)
  - GET `/dashboard` - Resumen completo
  - GET `/dashboard/today` - Resumen hoy
  - GET `/dashboard/week` - Resumen semana

### Tests

- [ ] Tests de endpoints (30 min)
  - Test CRUD básico cada router
  - Test errores comunes
  - Test autenticación (si aplica)

**Tiempo total estimado:** 4h 30min

---

## 🎲 PRIORIDAD 4: Sistema de Dados (2h)

**Estado:** ⏳ PENDIENTE  
**Requiere:** Bugs críticos arreglados + API funcionando

### Tareas

- [ ] Integrar `caronte_dice.py` en API (1h)
  - Endpoint `POST /rpg/end-of-day`
  - Calcular hábitos completados
  - Calcular tareas completadas
  - Llamar `daily_dice_roll()`
  - Devolver resultado con animación

- [ ] Sistema de indulgencias (1h)
  - Endpoint `POST /rpg/indulgencia/prevention`
  - Endpoint `POST /rpg/indulgencia/absolution`
  - Validar costes
  - Registrar en logs
  - Actualizar Wyrd

**Tiempo total estimado:** 2h

---

## 🎨 PRIORIDAD 5: FASE 3 - Frontend (8-12h)

**Estado:** ⏳ PENDIENTE  
**Requiere:** API completamente funcional

### Componentes

- [ ] Dashboard principal (2h)
  - Resumen diario
  - Hábitos pendientes
  - Tareas de hoy
  - Eventos próximos
  - Perfil RPG

- [ ] Gestión hábitos (2h)
  - Lista con filtros
  - Formulario crear/editar
  - Marcar completado
  - Ver estadísticas

- [ ] Gestión tareas (2h)
  - Lista con filtros
  - Formulario crear/editar
  - Cambiar estado
  - Ver vencidas

- [ ] Gestión eventos (1h)
  - Calendario
  - Lista eventos
  - Formulario crear/editar

- [ ] Mercado RPG (2h)
  - Lista artefactos disponibles
  - Comprar artefactos
  - Ver artefactos usuario
  - Equipar/desequipar

- [ ] Animación dados (2h)
  - Interfaz tirada nocturna
  - Animación dados 3D
  - Mostrar combos
  - Mostrar recompensas

- [ ] Sistema indulgencias (1h)
  - Botones prevención/absolución
  - Confirmación costes
  - Animación efectos

**Tiempo total estimado:** 12h

---

## 🤖 PRIORIDAD 6: Bot Telegram (4-6h)

**Estado:** ⏳ PENDIENTE  
**Requiere:** API funcionando

### Comandos

- [ ] `/start` - Bienvenida
- [ ] `/habits` - Ver hábitos pendientes
- [ ] `/tasks` - Ver tareas de hoy
- [ ] `/events` - Ver eventos de hoy
- [ ] `/profile` - Ver perfil RPG
- [ ] `/market` - Ver mercado
- [ ] `/roll` - Tirada dados manual

### Notificaciones

- [ ] Recordatorios tareas
- [ ] Recordatorios eventos
- [ ] Notificación game over
- [ ] Notificación level up

**Tiempo total estimado:** 5h

---

## 📊 RESUMEN DE PRIORIDADES

| Prioridad | Nombre | Tiempo | Estado |
|-----------|--------|--------|--------|
| 🔴 P1 | Bugs Críticos | 1-2h | ⏳ Pendiente |
| 🟡 P2 | Issues Medios | 2-3h | ⏳ Pendiente |
| 🚀 P3 | API REST | 3-4h | ⏳ Pendiente |
| 🎲 P4 | Dados | 2h | ⏳ Pendiente |
| 🎨 P5 | Frontend | 8-12h | ⏳ Pendiente |
| 🤖 P6 | Bot Telegram | 4-6h | ⏳ Pendiente |
| **TOTAL** | | **20-30h** | |

---

## 🎯 PLAN DE EJECUCIÓN RECOMENDADO

### Semana 1
- **Día 1:** P1 - Bugs críticos (1-2h)
- **Día 2:** P2 - Issues medios (2-3h)
- **Día 3-4:** P3 - API REST (3-4h)
- **Día 5:** P4 - Dados (2h)

### Semana 2
- **Día 1-3:** P5 - Frontend (8-12h)
- **Día 4-5:** P6 - Bot Telegram (4-6h)
- **Día 6:** Testing e integración
- **Día 7:** Documentación final

---

## 📝 NOTAS

- Prioridades pueden cambiar según necesidades
- Tiempos son estimaciones, pueden variar
- Cada tarea debe tener tests asociados
- Documentar cambios en CHANGELOG.md
- Actualizar STATUS.md tras cada sesión

---

**Última actualización:** 07/03/2026 22:15 CET  
**Próxima revisión:** Tras completar P1 (Bugs críticos)
