# 🌊 Life Assistant V4 - La Barca de Caronte

> Sistema de productividad gamificado con mecánicas RPG inspiradas en la mitología griega

## 📋 Descripción

Life Assistant V4 es un asistente personal completo que combina gestión de hábitos, tareas y eventos con un sistema de gamificación basado en el mito de Caronte, el barquero del río Estigia.

### ✨ Características principales

- 📱 **Interfaz Web Completa**: Dashboard visual con gestión CRUD de hábitos, tareas y eventos
- 🤖 **Bot de Telegram**: Control total desde tu móvil con interfaz conversacional
- 🎮 **Sistema RPG**: XP, niveles, Wyrd (vida), monedas y artefactos míticos
- 🎲 **Sistema de Dados**: Mecánicas D&D integradas con tareas y hábitos
- 🗄️ **Base de Datos Robusta**: SQLite con SQLAlchemy (20+ tablas)
- 🔔 **Recordatorios Automáticos**: Notificaciones inteligentes
- 🤖 **IA Integrada**: Chat con Caronte usando OpenAI

## 🏗️ Arquitectura

```
life-assistant-v4/
├── src/                    # Código fuente
│   ├── core/              # Core: Database, Models, Dice System
│   ├── services/          # Lógica de negocio (CRUD)
│   ├── api/               # FastAPI REST API
│   ├── bot/               # Telegram Bot
│   └── config/            # Configuración centralizada
├── static/                # Frontend: CSS, JS
├── templates/             # HTML Templates
├── tests/                 # Tests unitarios
└── docs/                  # Documentación
```

## 🚀 Quick Start

### Requisitos

- Python 3.10+
- SQLite3
- Cuenta OpenAI API (opcional)
- Bot Token Telegram (opcional)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/alvarofernandezmota-tech/personal.git
cd personal/03_proyectos/life-assistant-v4

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Iniciar base de datos
python -c "from src.core.database import Base, engine; Base.metadata.create_all(engine)"

# Iniciar aplicación web
cd src/api && python main.py
# Abrir: http://localhost:8000

# Iniciar bot Telegram (terminal separada)
cd src/bot && python main.py
```

## 📊 Estado del Proyecto

### ✅ Completado (V3 migrado)

- [x] Base de datos completa (20+ tablas)
- [x] CRUD Hábitos (9/10)
- [x] CRUD Tareas (9/10)
- [x] CRUD Eventos (9/10)
- [x] Services layer bien estructurado
- [x] Sistema de dados completo
- [x] Documentación técnica

### 🚧 En desarrollo (V4)

- [ ] Frontend web completo (HTML + CSS + JS)
- [ ] API REST con routers modulares
- [ ] Bot Telegram refactorizado
- [ ] Sistema RPG integrado
- [ ] Tests unitarios
- [ ] CI/CD con GitHub Actions

### 📅 Roadmap

Ver [ROADMAP.md](ROADMAP.md) para el plan detallado de desarrollo.

## 🎮 Sistema RPG - La Barca de Caronte

### Concepto

Cada día eres Caronte, el barquero que transporta almas por el río Estigia. Tus hábitos y tareas son almas que debes embarcar antes del anochecer.

### Mecánicas principales

- **XP y Niveles**: Gana experiencia completando hábitos y tareas
- **Wyrd (0-100)**: Tu destino/vida. Pierde Wyrd con malos hábitos
- **Monedas**: 4 tipos (óbolos, dracmas, tetradracmas, decadracmas)
- **La Barca**: Tiene integridad que debes mantener
- **Artefactos**: 10 ítems míticos comprables (Lira de Orfeo, Égida de Atenea, etc.)
- **Tributo a Hades**: Pago semanal obligatorio
- **Sistema de Dados**: Tiradas para desafíos y eventos especiales

Ver [docs/CARONTE-SPEC.md](docs/CARONTE-SPEC.md) para detalles completos.

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con coverage
pytest --cov=src tests/

# Tests específicos
pytest tests/test_crud.py
```

## 📚 Documentación

- [CARONTE-SPEC.md](docs/CARONTE-SPEC.md) - Especificación completa sistema RPG
- [DICE-SYSTEM-SPEC.md](docs/DICE-SYSTEM-SPEC.md) - Sistema de dados
- [API.md](docs/API.md) - Documentación API REST
- [ROADMAP.md](ROADMAP.md) - Plan de desarrollo

## 🤝 Contribuir

Este es un proyecto personal, pero las sugerencias son bienvenidas.

## 📝 Licencia

MIT License - Álvaro Fernández Mota © 2026

## 🔗 Links

- **Portfolio**: [alvarofernandezmota.dev](https://alvarofernandezmota.dev)
- **GitHub**: [@alvarofernandezmota-tech](https://github.com/alvarofernandezmota-tech)
- **LinkedIn**: [Álvaro Fernández Mota](https://linkedin.com/in/alvarofernandezmota)

---

**Hecho con ❤️ y ☕ en Madrid, España 🇪🇸**