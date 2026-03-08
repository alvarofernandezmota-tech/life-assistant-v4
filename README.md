# 🌊 Life Assistant V4 - Sistema Caronte

> Sistema de gestión de vida gamificado con mecánicas RPG inspiradas en mitología griega.

**Versión:** 1.5.0  
**Estado:** ✅ Backend funcional | 🚧 Frontend básico | 🔜 Bot Telegram  
**Fecha:** 8 Marzo 2026

---

## 🎯 ¿Qué es Life Assistant V4?

Un asistente personal que gamifica tu productividad usando mecánicas RPG:

- 📝 **Gestión de tareas** con sistema de recompensas
- 🔄 **Tracking de hábitos** con rachas y logros
- 📅 **Calendario de eventos** integrado
- ⚡ **Sistema RPG Caronte** - Gana XP, sube de nivel, compra artefactos
- 🤖 **Chat IA** con contexto de tu vida (Groq LLM)
- 🚣 **Bot Telegram** (próximamente)

---

## ✅ Estado Actual

### Backend API ✅
- FastAPI REST API completamente funcional
- Base de datos SQLite con SQLAlchemy ORM
- Sistema RPG completo (niveles, XP, oro, artefactos)
- CRUD completo para tareas, hábitos y eventos
- Chat IA integrado con Groq
- Sistema de Indulgencias (perdones por malos hábitos)
- Caronte Dice System (dados mitológicos)

### Frontend 🚧
- Dashboard HTML básico funcional
- Interfaz conectada a API
- Vista de tareas, hábitos y eventos
- Stats RPG en tiempo real
- Próximamente: Calendario avanzado (FullCalendar)

### Bot Telegram 🔜
- En desarrollo
- Comandos básicos planificados
- Notificaciones automáticas

---

## 🚀 Quick Start

### Requisitos
- Python 3.10+
- SQLite (incluido)
- Git

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/alvarofernandezmota-tech/life-assistant-v4.git
cd life-assistant-v4

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instalar dependencias core
pip install sqlalchemy alembic fastapi uvicorn[standard] python-dotenv groq pydantic pydantic-settings httpx python-multipart

# 4. Crear archivo .env
cp .env.example .env
# Editar .env y añadir tu GROQ_API_KEY

# 5. Inicializar base de datos
python init_db.py

# 6. Lanzar API
python run.py
```

**API disponible en:** http://localhost:8000/docs  
**Frontend:** Abrir `frontend/index.html` en navegador

---

## 📚 Documentación

- **[QUICKSTART.md](QUICKSTART.md)** - Guía de inicio rápido detallada
- **[STATUS.md](STATUS.md)** - Estado actual del proyecto
- **[TODO.md](TODO.md)** - Tareas pendientes
- **[ROADMAP.md](ROADMAP.md)** - Hoja de ruta
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de versiones
- **[BUGS.md](BUGS.md)** - Bugs conocidos
- **[diary/](diary/)** - Diario de desarrollo

---

## 🎮 Sistema RPG Caronte

### Mecánicas Principales

**XP & Niveles:**
- Completa tareas → Gana XP
- Completa hábitos → Gana XP
- Acumula XP → Sube de nivel
- Nivel = sqrt(XP / 100)

**Oro (Óbolos):**
- Moneda del sistema
- Ganar: Completar tareas/hábitos
- Gastar: Comprar artefactos, indulgencias

**Artefactos:**
- 12 artefactos míticos disponibles
- 3 raridades: Common, Rare, Legendary
- Bonus: XP, Oro, Protección

**Penalizaciones:**
- Malos hábitos → Pierde HP y XP
- HP = 0 → Penalización mayor

**Indulgencias:**
- Sistema de perdones
- Prevención: Antes del mal hábito (25 óbolos)
- Absolución: Después del mal hábito (50 óbolos)

### Recompensas por Dificultad

| Acción | XP | Oro |
|--------|-----|------|
| Tarea fácil | +10 | +5 |
| Tarea media | +20 | +10 |
| Tarea difícil | +30 | +15 |
| Hábito fácil | +10 | +5 |
| Hábito medio | +15 | +8 |
| Hábito difícil | +25 | +12 |

---

## 🛠️ Stack Tecnológico

**Backend:**
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos embebida
- **Groq** - LLM para chat IA (llama-3.3-70b-versatile)
- **Pydantic** - Validación de datos
- **Alembic** - Migraciones de BD

**Frontend:**
- **HTML5 + Vanilla JS** - Sin frameworks pesados
- **Tailwind CSS** - Diseño responsive
- **Fetch API** - Comunicación con backend

**DevOps:**
- **Git/GitHub** - Control de versiones
- **WSL2** - Desarrollo en Ubuntu sobre Windows

---

## 📁 Estructura del Proyecto

```
life-assistant-v4/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # Entry point
│   │   └── routers/           # Endpoints
│   │       ├── tasks.py       # CRUD tareas
│   │       ├── habits.py      # CRUD hábitos
│   │       ├── events.py      # CRUD eventos
│   │       ├── rpg.py         # Sistema RPG
│   │       └── chat.py        # Chat IA
│   ├── core/                   # Core logic
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── models.py          # DB models
│   │   └── rpg_models.py      # RPG specific models
│   ├── services/               # Business logic
│   │   ├── rpg.py             # RPG calculations
│   │   └── caronte_dice.py    # Dice system
│   └── config/
│       └── settings.py        # Configuration
├── frontend/
│   └── index.html             # Dashboard web
├── data/
│   └── life.db                # SQLite database
├── init_db.py                 # Database initializer
├── run.py                     # Application launcher
├── requirements.txt
└── docs/                      # Documentation
```

---

## 🌐 API Endpoints

### Tareas
- `GET /tasks/` - Listar tareas
- `POST /tasks/` - Crear tarea
- `GET /tasks/{id}` - Ver tarea
- `PUT /tasks/{id}` - Actualizar tarea
- `DELETE /tasks/{id}` - Eliminar tarea
- `POST /tasks/{id}/complete` - Completar tarea
- `POST /tasks/{id}/uncomplete` - Descompletar tarea
- `GET /tasks/stats/today` - Estadísticas del día
- `GET /tasks/overdue` - Tareas vencidas

### Hábitos
- `GET /habits/` - Listar hábitos
- `POST /habits/` - Crear hábito
- `GET /habits/{id}` - Ver hábito
- `PUT /habits/{id}` - Actualizar hábito
- `DELETE /habits/{id}` - Eliminar hábito
- `POST /habits/{id}/complete` - Completar hábito
- `GET /habits/{id}/logs` - Historial de completados
- `GET /habits/stats/today` - Estadísticas del día

### Eventos
- `GET /events/` - Listar eventos
- `POST /events/` - Crear evento
- `GET /events/{id}` - Ver evento
- `PUT /events/{id}` - Actualizar evento
- `DELETE /events/{id}` - Eliminar evento
- `GET /events/calendar/month` - Vista mensual
- `GET /events/upcoming` - Próximos eventos

### RPG
- `GET /rpg/profile` - Ver perfil completo
- `POST /rpg/end-of-day` - Calcular día
- `POST /rpg/bad-habit` - Registrar mal hábito
- `GET /rpg/indulgencia/coste` - Ver costes
- `POST /rpg/indulgencia/prevencion` - Comprar prevención
- `POST /rpg/indulgencia/absolucion` - Comprar absolución
- `POST /rpg/indulgencia/usar` - Usar indulgencia
- `GET /rpg/market` - Ver artefactos disponibles
- `GET /rpg/artifacts` - Ver inventario

### Chat
- `POST /chat/message` - Enviar mensaje
- `GET /chat/history` - Ver historial
- `DELETE /chat/history` - Limpiar historial
- `GET /chat/status` - Estado del sistema

**Documentación completa:** http://localhost:8000/docs

---

## 🎯 Roadmap

### ✅ Fase 1: Backend Core (COMPLETADO)
- [x] API REST con FastAPI
- [x] Base de datos SQLite
- [x] Modelos de datos
- [x] CRUD completo
- [x] Sistema RPG básico

### ✅ Fase 1.5: Fixes & Mejoras (COMPLETADO - 8 Mar 2026)
- [x] Fix bugs críticos
- [x] Sistema Caronte Dice
- [x] Indulgencias
- [x] Artefactos míticos
- [x] Chat IA integrado
- [x] Dashboard HTML funcional

### 🚧 Fase 2: Frontend (EN CURSO)
- [x] Dashboard HTML básico
- [ ] Calendario avanzado (FullCalendar)
- [ ] Gráficos de estadísticas
- [ ] Tema mitológico completo
- [ ] Animaciones y transiciones

### 🔜 Fase 3: Bot Telegram
- [ ] Comandos básicos
- [ ] Notificaciones automáticas
- [ ] Gestión desde móvil

### 🔜 Fase 4: Avanzado
- [ ] Sincronización Google Calendar
- [ ] Sistema de logros
- [ ] Modo multijugador
- [ ] App móvil nativa

---

## 🌊 Mitología Caronte

El sistema está inspirado en la mitología griega del barquero Caronte:

- **🚣 Caronte** - Barquero del Estigio (Bot Telegram)
- **🪙 Óbolos** - Monedas para pagar el pasaje
- **⚡ Olimpo** - Sistema de niveles divinos
- **⚔️ Trabajos de Hércules** - Tareas épicas
- **🔄 Rituales Divinos** - Hábitos diarios
- **🏺 Río Estigio** - Eventos temporales
- **⚡ Ira de Zeus** - Penalizaciones
- **🔱 Indulgencias de Poseidón** - Sistema de perdones

---

## 🐛 Bugs Conocidos

Ver [BUGS.md](BUGS.md) para lista completa.

---

## 📄 Licencia

MIT License - Proyecto personal

---

## 👤 Autor

**Álvaro Fernández Mota**  
🐙 GitHub: [@alvarofernandezmota-tech](https://github.com/alvarofernandezmota-tech)

---

**Hecho con ⚡ y mucha mitología griega**
