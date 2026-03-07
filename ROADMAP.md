# 🗯️ ROADMAP - Life Assistant V4

> Plan de desarrollo completo con 24 tareas priorizadas

## 📊 Estado General

- **Total tareas**: 24
- **🔴 Críticas**: 16
- **🟡 Medias**: 4  
- **🟢 Bajas**: 4
- **Estimación total**: 35-40 horas (5-7 días)

---

## 🎯 FASE 1: Estructura Base (Día 1) - 3 horas

### ✅ Completado

- [x] **Crear carpetas V4 completas** - 30 min
  - Estructura src/, docs/, static/, templates/, tests/
  - Archivos base: README, .gitignore, .env.example

### 🚧 Pendiente

- [ ] **Migrar database.py → separar en models.py** - 1 hora
  - `src/core/database.py`: Conexión y sesión
  - `src/core/models.py`: Modelos SQLAlchemy separados
  - `src/core/rpg_models.py`: Modelos RPG independientes

- [ ] **Crear config/settings.py centralizado** - 30 min  
  - Configuración desde .env
  - Settings compartidos (DB, API keys, etc.)

- [ ] **Migrar services/* desde V3** - 1 hora
  - habits.py, tasks.py, events.py, diary.py
  - Adaptarlos a nueva estructura

---

## 🎯 FASE 2: API Web Funcional (Días 2-3) - 6 horas

### 🔴 Crítico

- [ ] **Crear routers separados** - 2 horas
  - `src/api/routers/habits.py`: CRUD hábitos
  - `src/api/routers/tasks.py`: CRUD tareas
  - `src/api/routers/events.py`: CRUD eventos
  - `src/api/routers/diary.py`: CRUD diario

- [ ] **Migrar main.py → src/api/main.py limpio** - 1 hora
  - FastAPI app modular
  - Importar routers
  - Configuración CORS
  - Middleware de logging

- [ ] **Crear endpoint /dashboard completo** - 1 hora
  - `src/api/routers/dashboard.py`
  - Resumen: hábitos hoy, tareas pendientes, eventos, stats

- [ ] **Testing CRUD completo** - 2 horas
  - `tests/test_crud.py`
  - Tests para Habits, Tasks, Events
  - Pytest fixtures

---

## 🎯 FASE 3: Frontend Web (Días 4-5) - 12 horas

### 🔴 Crítico - La prioridad más alta

- [ ] **Crear index.html con dashboard visual** - 3 horas
  - `templates/index.html`
  - Dashboard cards: Hábitos, Tareas, Eventos, RPG
  - Navbar responsivo
  - Footer con links

- [ ] **Crear CSS moderno** - 2 horas
  - `static/css/style.css`
  - Usar Tailwind CSS o Bootstrap
  - Dark mode toggle
  - Animaciones suaves

- [ ] **JavaScript fetch API** - 3 horas
  - `static/js/app.js`: Core functions
  - Fetch data desde API
  - Renderizar dinámicamente
  - Manejo de errores

- [ ] **Vistas separadas** - 4 horas
  - `templates/habits.html`: Vista hábitos con CRUD
  - `templates/tasks.html`: Vista tareas con filtros
  - `templates/events.html`: Calendario visual
  - `static/js/habits.js`, `tasks.js`, `events.js`

---

## 🎯 FASE 4: Bot Telegram Refactorizado (Días 6-7) - 8 horas

### 🔴 Crítico

- [ ] **Separar handlers en módulos** - 2 horas
  - `src/bot/handlers/habits.py`
  - `src/bot/handlers/tasks.py`
  - `src/bot/handlers/events.py`
  - `src/bot/handlers/rpg.py`

- [ ] **Migrar telegram_bot.py → src/bot/main.py** - 1 hora
  - Bot principal limpio
  - Registro de handlers
  - Error handling global

- [ ] **Mejorar interfaz conversacional** - 3 horas
  - `src/bot/keyboards.py`: InlineKeyboards
  - Botones interactivos
  - Callbacks handlers
  - Menús contextuales

- [ ] **Testing comandos Telegram** - 2 horas
  - `tests/test_bot.py`
  - Mock de Telegram API
  - Tests de comandos principales

---

## 🎯 FASE 5: Sistema RPG (Días 8-10) - 11 horas

### 🟡 Medio

- [ ] **Refactorizar caronte_engine.py** - 2 horas
  - Migrar a `src/services/rpg.py`
  - Simplificar lógica de barco
  - Integrar con Services

- [ ] **Integrar dice_system.py con hábitos/tareas** - 3 horas
  - `src/core/dice_system.py` ya existe
  - Conectar con habit_service
  - Tiradas automáticas en desafíos
  - Sistema de recompensas por dados

- [ ] **Crear router /rpg completo** - 2 horas
  - `src/api/routers/rpg.py`
  - Endpoints: profile, boat, market, artifacts, tribute

- [ ] **Frontend RPG** - 4 horas
  - `templates/rpg.html`: Dashboard RPG
  - `static/js/rpg.js`: Lógica frontend
  - Visualización de stats (XP, Wyrd, coins)
  - Mercado de artefactos interactivo

---

## 🎯 FASE 6: Características Avanzadas (Días 11-14) - 9 horas

### 🟢 Bajo

- [ ] **Sistema de recordatorios automáticos** - 3 horas
  - `src/services/reminders.py`
  - Cron job para checks periódicos
  - Notificaciones Telegram
  - Email notifications (opcional)

- [ ] **Diario personal completo** - 2 horas
  - Ya existe diary_service.py
  - Crear `templates/diary.html`
  - Editor markdown
  - Búsqueda por tags

- [ ] **Mejorar ai_engine.py** - 2 horas
  - `src/services/ai.py`
  - Más intenciones detectables
  - Contexto mejorado
  - Respuestas personalizadas por rol

- [ ] **Documentación completa V4** - 2 horas
  - Actualizar README.md
  - API.md con todos los endpoints
  - Diagramas de arquitectura
  - Guía de deployment

---

## 📊 Progreso por Fase

| Fase | Tareas | Completadas | Pendientes | Progreso |
|------|--------|-------------|------------|----------|
| FASE 1 | 4 | 1 | 3 | 25% |
| FASE 2 | 4 | 0 | 4 | 0% |
| FASE 3 | 4 | 0 | 4 | 0% |
| FASE 4 | 4 | 0 | 4 | 0% |
| FASE 5 | 4 | 0 | 4 | 0% |
| FASE 6 | 4 | 0 | 4 | 0% |
| **TOTAL** | **24** | **1** | **23** | **4%** |

---

## 🏆 Criterios de Éxito

V4 estará completo cuando:

✅ **Frontend Web**
- [ ] Usuario puede crear/editar/eliminar hábitos desde web
- [ ] Usuario puede crear/editar/eliminar tareas desde web
- [ ] Usuario puede crear/editar/eliminar eventos desde web
- [ ] Dashboard visual con resumen del día
- [ ] Interfaz responsiva (mobile-friendly)

✅ **Bot Telegram**
- [ ] CRUD completo hábitos/tareas/eventos
- [ ] Interfaz con InlineKeyboards
- [ ] Recordatorios automáticos
- [ ] Sistema RPG integrado

✅ **Sistema RPG**
- [ ] Dados integrados con hábitos/tareas
- [ ] XP, Wyrd, monedas actualizándose automáticamente
- [ ] Mercado de artefactos funcional
- [ ] Barco de Caronte visible y funcional

✅ **Calidad Código**
- [ ] Tests unitarios >70% coverage
- [ ] Código modular y mantenible
- [ ] Documentación completa
- [ ] CI/CD configurado

---

## 📅 Timeline

```
Semana 1 (Días 1-7):
├── Día 1: FASE 1 (Estructura)
├── Días 2-3: FASE 2 (API)
├── Días 4-5: FASE 3 (Frontend) 🔴
└── Días 6-7: FASE 4 (Bot Telegram)

Semana 2 (Días 8-14):
├── Días 8-10: FASE 5 (RPG)
└── Días 11-14: FASE 6 (Extras)
```

---

## 📝 Notas

- **PRIORIDAD MÁXIMA**: Fase 3 (Frontend) - Sin esto la app no es usable
- **Fase 1-2 rápidas**: Ya tenemos mucho código de V3 para migrar
- **Testing continuo**: Probar después de cada fase
- **Deployment temprano**: Desplegar después de Fase 3 para testing real

---

**Última actualización**: 07/03/2026 20:42 CET