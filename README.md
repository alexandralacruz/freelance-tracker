# Freelance Hours Tracker

Control de horas trabajadas por proyecto freelance.  
**Stack:** FastAPI · PostgreSQL · HTML/JS (sin frameworks, todo embebido)

---

## Arranque rápido con Docker (recomendado)

```bash
# 1. Clona / descomprime el proyecto
cd freelance-tracker

# 2. Levanta todo (PostgreSQL + app + seed de NixAI-Eval)
docker compose up --build

# 3. Abre el navegador
open http://localhost:8000
```

El seed de **NixAI-Eval** (284h, desde 2025-06-14) se importa automáticamente al arrancar.

---

## 🛠 Arranque manual (sin Docker)

### Requisitos
- Python 3.11+
- PostgreSQL 14+ corriendo localmente

### Pasos

```bash
# 1. Instala dependencias
pip install -r requirements.txt

# 2. Crea la base de datos en PostgreSQL
psql -U postgres -c "CREATE DATABASE freelance_tracker;"
psql -U postgres -c "CREATE USER freelance WITH PASSWORD 'freelance123';"
psql -U postgres -c "GRANT ALL ON DATABASE freelance_tracker TO freelance;"

# 3. Configura la conexión
cp .env.example .env
# Edita .env con tu DATABASE_URL si es necesario

# 4. Importa los datos de NixAI-Eval
python seed.py

# 5. Arranca el servidor
uvicorn main:app --reload --port 8000

# 6. Abre http://localhost:8000
```

---

## 📋 Funcionalidades

| Feature | Descripción |
|---|---|
| **Multi-proyecto** | Crea y gestiona varios proyectos freelance en paralelo |
| **Registro diario** | Ingresa horas para hoy o cualquier día pasado |
| **Edición inline** | Modifica horas directamente en la tabla de registros |
| **Bloqueo futuro** | No permite registrar horas en fechas futuras |
| **Dashboard por proyecto** | KPIs, gráfico mensual, barras por día de semana, historial diario |
| **Promedio mensual** | Tabla con total, días trabajados y promedio diario por mes |
| **Colores por proyecto** | Identifica visualmente cada proyecto con un color |

---

## 🔌 API REST (FastAPI)

Documentación interactiva en: **http://localhost:8000/docs**

### Proyectos
```
GET    /api/projects              Lista todos los proyectos
POST   /api/projects              Crea un nuevo proyecto
GET    /api/projects/{id}         Detalle de un proyecto
PUT    /api/projects/{id}         Edita nombre/descripción/color
DELETE /api/projects/{id}         Elimina proyecto y todos sus registros
```

### Registros de horas
```
POST   /api/logs                          Crea/actualiza registro (upsert por fecha)
GET    /api/projects/{id}/logs            Lista todos los registros del proyecto
GET    /api/projects/{id}/log/{fecha}     Registro de una fecha específica
PUT    /api/logs/{log_id}                 Actualiza horas de un registro
DELETE /api/logs/{log_id}                 Elimina un registro
```

### Dashboard
```
GET    /api/projects/{id}/dashboard       Dashboard completo con estadísticas
GET    /api/today                         Devuelve la fecha de hoy del servidor
```

### Ejemplo: crear proyecto
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"ClienteABC","start_date":"2026-01-01","color":"#22d3a0"}'
```

### Ejemplo: registrar horas hoy
```bash
curl -X POST http://localhost:8000/api/logs \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"log_date":"2026-05-19","hours":4.5,"notes":"Feature X"}'
```

---

## 🗃 Estructura del proyecto

```
freelance-tracker/
├── main.py              # FastAPI app + sirve el frontend
├── seed.py              # Importa datos históricos de NixAI-Eval
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env                 # DATABASE_URL
├── app/
│   ├── models.py        # SQLAlchemy models (Project, WorkLog)
│   ├── schemas.py       # Pydantic schemas + validaciones
│   ├── crud.py          # Lógica de negocio + estadísticas
│   ├── database.py      # Conexión SQLAlchemy
│   └── routes.py        # Endpoints FastAPI
└── frontend/
    └── index.html       # SPA completa (HTML + CSS + JS)
```

---

## 🗄 Modelo de datos

```sql
projects
  id, name, description, start_date, color, created_at

work_logs
  id, project_id → projects.id, log_date, hours (0-24), notes, created_at, updated_at
  UNIQUE(project_id, log_date)   -- un registro por proyecto por día
```

---

## ⚠️ Reglas de negocio

- **No se pueden registrar horas en fechas futuras** (validado en backend y frontend)
- **No se pueden registrar horas antes del inicio del proyecto**
- **Máximo 24h por día** por proyecto
- Un `POST /api/logs` con la misma fecha hace **upsert** (no duplica)
