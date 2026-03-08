# 🚀 Quick Start - Life Assistant V4

**Phase 1.5 Backend + API Completo**

---

## 🛠️ Requisitos

- Python 3.10+
- pip
- Windows PowerShell / Linux Terminal

---

## 📚 Instalación

### **1. Clonar e instalar dependencias**

```powershell
# Si aún no has clonado
git clone https://github.com/alvarofernandezmota-tech/life-assistant-v4.git
cd life-assistant-v4

# Pull últimos cambios
git pull origin main

# Crear entorno virtual
python -m venv .venv

# Activar entorno
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### **2. Configurar variables de entorno**

```powershell
# Copiar ejemplo
cp .env.example .env

# Editar .env con tu editor favorito
notepad .env  # Windows
nano .env     # Linux
```

**Variables críticas:**
```env
GROQ_API_KEY=gsk_tu_clave_aqui  # Obligatorio para chat
DEFAULT_USER_ID=1
DATABASE_URL=sqlite:///./data/life.db
```

**🔑 Obtener Groq API Key (gratis):**
1. Ir a [https://console.groq.com/keys](https://console.groq.com/keys)
2. Crear cuenta (gratis)
3. Crear nueva API key
4. Copiar a `.env`

### **3. Inicializar base de datos**

```powershell
# Crear carpeta data si no existe
mkdir data -ErrorAction SilentlyContinue

# Inicializar DB + artefactos
python init_db.py
```

**Output esperado:**
```
============================================================
🚀 Life Assistant V4 — Inicialización de Base de Datos
============================================================
🛠️  Creando tablas...
✅ Tablas creadas correctamente
🎮 Insertando artefactos míticos...
✅ 12 artefactos insertados (4 common / 4 rare / 4 legendary)

✅ Base de datos inicializada correctamente
🌊 Ya puedes iniciar la aplicación!
============================================================
```

### **4. Lanzar API**

```powershell
uvicorn src.api.main:app --reload
```

**Output esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## ✅ Verificar Instalación

### **1. Abrir documentación interactiva**

Navegador: **http://localhost:8000/docs**

Deberías ver:
- Swagger UI con todos los endpoints
- 5 secciones: Habits, Tasks, Events, RPG, Chat

### **2. Probar endpoint de salud**

```powershell
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "message": "API funcionando correctamente",
  "routers": ["habits", "tasks", "events", "rpg", "chat"]
}
```

### **3. Probar crear un hábito**

En http://localhost:8000/docs:

1. Ir a **POST /habits**
2. Click en "Try it out"
3. Pegar JSON:
   ```json
   {
     "name": "Ejercicio matutino",
     "frequency": "daily",
     "icon": "💪"
   }
   ```
4. Click en "Execute"
5. Ver respuesta:
   ```json
   {
     "id": 1,
     "name": "Ejercicio matutino",
     "message": "Hábito creado exitosamente"
   }
   ```

### **4. Probar chat con Caronte**

En http://localhost:8000/docs:

1. Ir a **POST /chat/message**
2. Click en "Try it out"
3. Pegar JSON:
   ```json
   {
     "message": "¿Cómo puedo mejorar mi productividad?"
   }
   ```
4. Ver respuesta con mensaje de Caronte

---

## 📦 Endpoints Disponibles

### **Hábitos** (`/habits`)
- `GET /habits` - Listar todos
- `GET /habits/{id}` - Ver uno
- `POST /habits` - Crear
- `PUT /habits/{id}` - Actualizar
- `DELETE /habits/{id}` - Eliminar
- `POST /habits/{id}/complete` - Marcar completado
- `GET /habits/{id}/logs` - Historial
- `GET /habits/stats/today` - Estadísticas

### **Tareas** (`/tasks`)
- `GET /tasks` - Listar (filtros: completed, priority)
- `GET /tasks/{id}` - Ver una
- `POST /tasks` - Crear
- `PUT /tasks/{id}` - Actualizar
- `DELETE /tasks/{id}` - Eliminar
- `POST /tasks/{id}/complete` - Completar
- `GET /tasks/stats/today` - Estadísticas
- `GET /tasks/overdue` - Vencidas

### **Eventos** (`/events`)
- `GET /events` - Listar (filtros: start_date, end_date, category)
- `GET /events/{id}` - Ver uno
- `POST /events` - Crear
- `PUT /events/{id}` - Actualizar
- `DELETE /events/{id}` - Eliminar
- `GET /events/calendar/month` - Calendario mensual
- `GET /events/upcoming` - Próximos eventos

### **RPG** (`/rpg`)
- `GET /rpg/profile` - Perfil completo
- `POST /rpg/end-of-day` - Tirada dados (fin día)
- `POST /rpg/bad-habit` - Registrar mal hábito
- `GET /rpg/market` - Artefactos disponibles
- `GET /rpg/artifacts` - Inventario usuario
- `POST /rpg/indulgencia/prevencion` - Comprar prevención
- `POST /rpg/indulgencia/absolucion` - Comprar absolución

### **Chat** (`/chat`)
- `POST /chat/message` - Hablar con Caronte
- `GET /chat/history` - Ver historial
- `DELETE /chat/history` - Borrar historial
- `GET /chat/status` - Estado Groq API

---

## 🐛 Troubleshooting

### **Error: `uvicorn: El término 'uvicorn' no se reconoce`**

```powershell
# Asegurarte de tener el entorno virtual activado
.venv\Scripts\Activate.ps1

# Reinstalar uvicorn
pip install uvicorn[standard]
```

### **Error: `ImportError: attempted relative import beyond top-level package`**

```powershell
# Pull últimos cambios (ya corregido)
git pull origin main

# Verificar que init_db.py tiene imports correctos:
# from src.core.database import ...
```

### **Error: `GROQ_API_KEY no configurada`**

1. Verificar que `.env` existe en la raíz
2. Verificar que `GROQ_API_KEY=gsk_...` está configurado
3. Reiniciar API

### **Error: `sqlite3.OperationalError: table X already exists`**

```powershell
# Borrar DB y recrear
rm data/life.db
python init_db.py
```

---

## 📚 Próximos Pasos

1. ✅ Backend funcionando
2. ⏳ Crear frontend (calendario web)
3. ⏳ Crear bot Telegram
4. ⏳ Tests unitarios

Ver [ROADMAP.md](ROADMAP.md) para plan completo.

---

## 💬 Soporte

- **GitHub Issues:** [life-assistant-v4/issues](https://github.com/alvarofernandezmota-tech/life-assistant-v4/issues)
- **Documentación:** Ver carpeta `docs/`
- **Diary:** Ver carpeta `diary/` para historial de desarrollo

---

**🌊 Que Caronte guíe tu barca!**
