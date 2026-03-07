# 🔌 API Documentation - Life Assistant V4

## Base URL

```
http://localhost:8000
```

## Authentication

Actualmente no requiere autenticación (usuario único).
En futuras versiones se implementará JWT auth.

---

## 🎯 Hábitos (Habits)

### Obtener todos los hábitos

```http
GET /habits
```

**Response:**
```json
[
  {
    "id": "abc123",
    "name": "Leer 30 minutos",
    "description": "Leer antes de dormir",
    "frequency": "daily",
    "time": "22:00",
    "color": "#7c6ef5",
    "group_name": "general",
    "created_at": "2026-03-07T20:00:00"
  }
]
```

### Crear hábito

```http
POST /habits
Content-Type: application/json

{
  "name": "Meditación",
  "description": "10 minutos diarios",
  "frequency": "daily",
  "time": "08:00",
  "color": "#4CAF50"
}
```

### Marcar hábito como completado

```http
POST /habits/log
Content-Type: application/json

{
  "habit_id": "abc123",
  "date": "2026-03-07",
  "completed": true
}
```

---

## ✅ Tareas (Tasks)

### Obtener todas las tareas

```http
GET /tasks
GET /tasks?status=pending
GET /tasks?priority=high
```

### Crear tarea

```http
POST /tasks
Content-Type: application/json

{
  "title": "Comprar libros",
  "description": "Comprar en librería",
  "due_date": "2026-03-10",
  "priority": "medium",
  "category": "personal"
}
```

### Actualizar estado de tarea

```http
PATCH /tasks/{task_id}/status
Content-Type: application/json

{
  "status": "done"
}
```

---

## 📅 Eventos (Events)

### Obtener eventos

```http
GET /events
GET /events?day=2026-03-07
GET /events?week=2026-03-07
```

### Crear evento

```http
POST /events
Content-Type: application/json

{
  "title": "Reunión equipo",
  "date": "2026-03-08",
  "start_time": "10:00",
  "end_time": "11:30",
  "category": "trabajo",
  "recurring": "none"
}
```

---

## 🎮 Sistema RPG

### Obtener perfil RPG

```http
GET /rpg/profile
```

**Response:**
```json
{
  "user_id": 1,
  "level": 5,
  "xp": 1250,
  "wyrd": 85,
  "obolos": 45,
  "dracmas": 12,
  "tetradracmas": 3,
  "decadracmas": 0,
  "hero": "Aquiles",
  "streak": 7
}
```

### Obtener mercado de artefactos

```http
GET /rpg/market
```

### Comprar artefacto

```http
POST /rpg/buy-artifact
Content-Type: application/json

{
  "artifact_id": "lira_orfeo"
}
```

---

## 📋 Dashboard

### Obtener resumen completo

```http
GET /dashboard
```

**Response:**
```json
{
  "habits": [...],
  "tasks": [...],
  "events": [...],
  "rpg": {...},
  "stats": {...}
}
```

---

## 💬 Chat con IA

### Enviar mensaje

```http
POST /chat
Content-Type: application/json

{
  "message": "Cómo va mi día?"
}
```

**Response:**
```json
{
  "reply": "Hoy has completado 3 de 5 hábitos...",
  "actions": []
}
```

---

## Status Codes

- `200 OK`: Petición exitosa
- `201 Created`: Recurso creado
- `400 Bad Request`: Error en los datos enviados
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

---

## Próximos endpoints (En desarrollo)

- [ ] `POST /diary` - Crear entrada de diario
- [ ] `GET /diary/{date}` - Obtener entrada específica
- [ ] `POST /reminders` - Crear recordatorio
- [ ] `GET /stats/weekly` - Estadísticas semanales
- [ ] `GET /rpg/boat-status` - Estado de la barca de Caronte

---

**Documentación interactiva disponible en:**

📚 [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)  
📚 [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)