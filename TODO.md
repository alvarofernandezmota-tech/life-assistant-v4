# ✅ TODO - Life Assistant V4

**Última actualización:** 8 Marzo 2026, 16:45 CET

---

## 🔥 PRIORIDAD ALTA (Esta semana)

### Frontend
- [ ] **Calendario FullCalendar.js**
  - Instalar FullCalendar
  - Vista mensual interactiva
  - Click en día → Ver/crear eventos
  - Drag & drop de eventos
  - Colores por tipo (tareas/eventos)
  - **Estimado:** 2-3 horas

- [ ] **Mejorar Dashboard**
  - Añadir filtros (completadas/pendientes)
  - Formularios modales (crear tarea/hábito)
  - Validación de inputs
  - Mensajes de error/éxito
  - **Estimado:** 2 horas

### Bot Telegram
- [ ] **Crear bot en BotFather**
  - Obtener token
  - Configurar comandos
  - **Estimado:** 15 min

- [ ] **Comandos básicos**
  - `/start` - Bienvenida
  - `/tareas` - Listar tareas hoy
  - `/habitos` - Listar hábitos
  - `/completar <id>` - Completar tarea
  - `/perfil` - Ver stats RPG
  - **Estimado:** 3 horas

- [ ] **Notificaciones**
  - Recordatorio diario de hábitos
  - Alerta de tareas vencidas
  - **Estimado:** 2 horas

---

## 🟡 PRIORIDAD MEDIA (Próximas 2 semanas)

### Frontend Avanzado
- [ ] Gráficos de estadísticas
  - Chart.js o Recharts
  - XP ganado por día
  - Hábitos completados (últimos 30 días)
  - Productividad semanal

- [ ] Tema mitológico visual
  - Paleta de colores Caronte
  - Iconos personalizados
  - Animaciones de nivel up
  - Efectos de artefactos

- [ ] Modo oscuro/claro
  - Toggle en header
  - Persistir en localStorage

### Sistema RPG
- [ ] **Página RPG completa**
  - Vista de inventario visual
  - Marketplace de artefactos
  - Historial de XP
  - Sistema de achievements

- [ ] **Mecánicas avanzadas**
  - Sistema de logros
  - Títulos desbloqueables
  - Combates aleatorios (Caronte Dice)

### Integraciones
- [ ] **Google Calendar Sync**
  - OAuth2 setup
  - Import eventos
  - Export eventos
  - Sync bidireccional

---

## 🟢 PRIORIDAD BAJA (Backlog)

### Backend
- [ ] Sistema de tags para tareas
- [ ] Subtareas (checklist dentro de tarea)
- [ ] Notas en eventos
- [ ] Prioridad dinámica (urgente/importante)
- [ ] Estimación de tiempo por tarea

### Frontend
- [ ] Vista Kanban para tareas
- [ ] Vista semanal calendario
- [ ] Dashboard personalizable (widgets)
- [ ] Exportar datos (JSON/CSV)
- [ ] Importar desde Todoist/Notion

### Bot Telegram
- [ ] Inline queries
- [ ] Botones interactivos avanzados
- [ ] Grupos (gestión compartida)
- [ ] Comandos de voz

### Móvil
- [ ] PWA (Progressive Web App)
- [ ] App nativa React Native
- [ ] Notificaciones push
- [ ] Modo offline

---

## ✅ COMPLETADO (8 Mar 2026)

### Backend
- [x] API REST completa con FastAPI
- [x] Base de datos SQLite + SQLAlchemy
- [x] Modelos de datos (8 core + 13 RPG)
- [x] CRUD completo tareas/hábitos/eventos
- [x] Sistema RPG (XP, niveles, oro, artefactos)
- [x] Chat IA con Groq
- [x] Sistema de Indulgencias
- [x] Caronte Dice System
- [x] Todos los endpoints funcionando
- [x] `run.py` launcher
- [x] `init_db.py` con seed

### Frontend
- [x] Dashboard HTML básico
- [x] Tailwind CSS integrado
- [x] Conexión con API (Fetch)
- [x] Lista tareas con checkboxes
- [x] Lista hábitos con botón completar
- [x] Lista eventos del día
- [x] Stats RPG en tiempo real
- [x] Responsive básico

### Documentación
- [x] README.md completo
- [x] STATUS.md actualizado
- [x] CHANGELOG.md con v1.5.0
- [x] QUICKSTART.md
- [x] TODO.md (este archivo)
- [x] ROADMAP.md
- [x] BUGS.md
- [x] diary/2026-03-08.md

### Deploy
- [x] Desplegado en Ubuntu (WSL2)
- [x] API corriendo en localhost:8000
- [x] Tests manuales OK

---

## 🎯 HITOS (Milestones)

### v1.6.0 - Frontend Completo (Target: 15 Mar 2026)
- [ ] Calendario FullCalendar funcionando
- [ ] Dashboard mejorado con filtros
- [ ] Gráficos de stats
- [ ] Tema visual pulido

### v2.0.0 - Bot Telegram (Target: 22 Mar 2026)
- [ ] Bot completamente funcional
- [ ] Comandos completos
- [ ] Notificaciones automáticas
- [ ] Gestión completa desde móvil

### v2.5.0 - RPG Avanzado (Target: 5 Abr 2026)
- [ ] Sistema de logros
- [ ] Combates aleatorios
- [ ] Marketplace visual
- [ ] Historia épica Caronte

### v3.0.0 - Integraciones (Target: 20 Abr 2026)
- [ ] Google Calendar sync
- [ ] Importar/exportar datos
- [ ] Webhooks
- [ ] API pública

---

## 📋 TAREAS TÉCNICAS

### Testing
- [ ] Tests unitarios (pytest)
- [ ] Tests de integración
- [ ] Tests E2E (Playwright)
- [ ] Coverage > 80%

### DevOps
- [ ] CI/CD con GitHub Actions
- [ ] Deploy automático
- [ ] Docker containerization
- [ ] Monitoring (logs)

### Seguridad
- [ ] Rate limiting API
- [ ] Autenticación JWT
- [ ] Cifrado de datos sensibles
- [ ] Backup automático DB

### Performance
- [ ] Cacheo con Redis
- [ ] Optimización queries SQL
- [ ] Lazy loading frontend
- [ ] Compresión assets

---

## 💡 IDEAS FUTURAS

- Modo multijugador (competir con amigos)
- Integración con smartwatch
- Asistente de voz (Siri/Google)
- Gamificación avanzada (gremios, batallas)
- Marketplace de plugins
- Temas personalizables
- IA predictiva (sugerir tareas)
- Análisis de productividad con ML

---

**Última revisión:** 8 Marzo 2026
