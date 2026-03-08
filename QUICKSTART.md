# 🚀 Life Assistant V4 - Quickstart Guide

**Tiempo estimado:** 10 minutos  
**Nivel:** Principiante

---

## 📝 Prerequisitos

- **Python 3.10+** instalado
- **Git** instalado
- **Editor de texto** (VS Code recomendado)
- **Navegador web** moderno

---

## ⚡ Instalación Rápida

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/alvarofernandezmota-tech/life-assistant-v4.git
cd life-assistant-v4
```

### Paso 2: Crear entorno virtual (Opcional pero recomendado)

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Paso 3: Instalar dependencias core

```bash
pip install sqlalchemy alembic fastapi uvicorn[standard] python-dotenv groq pydantic pydantic-settings httpx python-multipart
```

### Paso 4: Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y añade tu API key de Groq:

```env
GROQ_API_KEY=gsk_tu_api_key_aqui
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=sqlite:///./data/life.db
```

**¿Cómo obtener Groq API Key?**
1. Visita https://console.groq.com
2. Crea cuenta gratis
3. Ve a API Keys → Create API Key
4. Copia la key y pégala en `.env`

### Paso 5: Inicializar base de datos

```bash
python init_db.py
```

Debes ver:
```
🚀 Life Assistant V4 — Inicialización de Base de Datos
✅ Tablas creadas correctamente
✅ 12 artefactos insertados
✅ Base de datos inicializada correctamente
```

### Paso 6: Lanzar la aplicación
```bash
python run.py
```

Debes ver:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.
```

---

## 🌐 Acceder a la aplicación

### Backend API

**Swagger Docs (Recomendado para probar):**
```
http://localhost:8000/docs
```

**Health Check:**
```
http://localhost:8000/health
```

**Endpoints principales:**
- `GET /rpg/profile` - Ver tu perfil RPG
- `GET /tasks/` - Listar tareas
- `GET /habits/` - Listar hábitos
- `GET /events/` - Listar eventos

### Frontend Dashboard

**Opción 1: Abrir directamente**
```
Abrir frontend/index.html en tu navegador
```

**Opción 2: Con servidor local**
```bash
cd frontend
python -m http.server 3000
```

Luego abre: http://localhost:3000

---

## ✅ Verificar que funciona

### 1. Probar API desde Swagger

1. Ve a http://localhost:8000/docs
2. Click en `GET /rpg/profile`
3. Click en "Try it out" → "Execute"
4. Deberías ver tu perfil inicial:

```json
{
  "user_id": 1,
  "level": 1,
  "xp": 0,
  "gold": 0,
  "health": 100,
  "indulgencias": 0
}
```

### 2. Crear tu primera tarea

1. En Swagger, busca `POST /tasks/`
2. Click "Try it out"
3. Body:
```json
{
  "title": "Mi primera tarea",
  "description": "Probar Life Assistant",
  "priority": "high",
  "difficulty": "easy"
}
```
4. Click "Execute"
5. Deberías recibir la tarea creada

### 3. Completar la tarea y ganar XP

1. Busca `POST /tasks/{id}/complete`
2. Pon `task_id: 1`
3. Execute
4. Verifica tu perfil de nuevo → ¡Deberías tener +10 XP!

### 4. Probar Frontend

1. Abre `frontend/index.html`
2. Deberías ver:
   - Tu tarea creada
   - Stats RPG actualizados (Nivel 1, 10 XP)
   - Checkbox para completar/descompletar

---

## 📚 Próximos Pasos

### Explorar Funcionalidades

1. **Crear hábitos**
   - `POST /habits/` en Swagger
   - Completa con `POST /habits/{id}/complete`

2. **Añadir eventos**
   - `POST /events/`
   - Ver calendario mensual con `GET /events/calendar/month`

3. **Sistema RPG**
   - Ver mercado: `GET /rpg/market`
   - Comprar artefactos cuando tengas suficiente oro
   - Sistema de indulgencias: `GET /rpg/indulgencia/coste`

4. **Chat IA**
   - `POST /chat/message`
   - Body: `{"message": "Hola, cómo estoy de productividad?"}`

### Personalizar

1. **Cambiar configuración RPG**
   - Edita `src/services/rpg.py`
   - Ajusta recompensas de XP/oro

2. **Modificar Frontend**
   - Edita `frontend/index.html`
   - Cambia colores, textos, layout

3. **Añadir tus propios artefactos**
   - Edita `init_db.py`
   - Añade más artefactos al seed

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'src'"

**Solución:**
```bash
# Usar run.py en lugar de uvicorn directo
python run.py
```

### Error: "uvicorn command not found"

**Solución:**
```bash
# Instalar uvicorn
pip install uvicorn[standard]

# O usar python -m
python -m uvicorn src.api.main:app --reload
```

### Error: "Database locked"

**Solución:**
```bash
# Cerrar todas las conexiones
# Eliminar database
rm data/life.db

# Reinicializar
python init_db.py
```

### Frontend no se conecta a API

**Solución:**
1. Verificar que API esté corriendo (http://localhost:8000/health)
2. Verificar CORS en `src/api/main.py`
3. Abrir consola del navegador (F12) para ver errores

### Error: "ImportError: attempted relative import"

**Solución:**
```bash
# Usar run.py que configura PYTHONPATH correctamente
python run.py
```

---

## 💻 Comandos Útiles

### Backend

```bash
# Lanzar API
python run.py

# Lanzar con hot-reload
python run.py  # (reload habilitado por defecto)

# Ver logs
tail -f api.log  # Si usas nohup

# Parar servidor
Ctrl + C
```

### Base de Datos

```bash
# Reinicializar DB
rm data/life.db
python init_db.py

# Ver DB con sqlite3
sqlite3 data/life.db
.tables
.schema tasks
SELECT * FROM tasks;
.quit
```

### Frontend

```bash
# Servidor local
cd frontend
python -m http.server 3000

# O abrir directamente
open frontend/index.html  # Mac
xdg-open frontend/index.html  # Linux
start frontend/index.html  # Windows
```

---

## 🚀 Modo Producción

### Con tmux (Linux/Mac)

```bash
# Crear sesión
tmux new -s life-api

# Dentro de tmux
python run.py

# Detach (mantener corriendo)
Ctrl + B, luego D

# Volver a la sesión
tmux attach -t life-api
```

### Con nohup

```bash
# Lanzar en background
nohup python run.py > api.log 2>&1 &

# Ver logs
tail -f api.log

# Ver proceso
ps aux | grep python

# Matar proceso
kill <PID>
```

---

## 📚 Documentación Adicional

- **[README.md](README.md)** - Descripción completa del proyecto
- **[STATUS.md](STATUS.md)** - Estado actual y métricas
- **[TODO.md](TODO.md)** - Roadmap y tareas pendientes
- **[BUGS.md](BUGS.md)** - Bugs conocidos y soluciones
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de versiones
- **API Docs:** http://localhost:8000/docs

---

## ❓ Ayuda

¿Problemas? ¿Sugerencias?

- Abre un issue en GitHub
- Consulta la documentación
- Revisa [BUGS.md](BUGS.md) para problemas comunes

---

**¡Disfruta usando Life Assistant V4! 🌊⚡**
