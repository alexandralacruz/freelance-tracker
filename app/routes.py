from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from typing import List
from datetime import date

router = APIRouter()


# ── Projects ──────────────────────────────────────────────────────────────────

@router.get("/projects", response_model=List[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)


@router.post("/projects", response_model=schemas.ProjectResponse, status_code=201)
def create_project(data: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, data)


@router.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = crud.get_project(db, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return p


@router.put("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, data: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    p = crud.update_project(db, project_id, data)
    if not p:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return p


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    if not crud.delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")


# ── Work Logs ─────────────────────────────────────────────────────────────────

@router.get("/projects/{project_id}/logs", response_model=List[schemas.WorkLogResponse])
def get_logs(project_id: int, db: Session = Depends(get_db)):
    if not crud.get_project(db, project_id):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return crud.get_work_logs(db, project_id)


@router.post("/logs", response_model=schemas.WorkLogResponse, status_code=201)
def upsert_log(data: schemas.WorkLogCreate, db: Session = Depends(get_db)):
    if data.log_date > date.today():
        raise HTTPException(status_code=400, detail="No se pueden registrar horas para fechas futuras")
    p = crud.get_project(db, data.project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if data.log_date < p.start_date:
        raise HTTPException(status_code=400, detail="La fecha no puede ser anterior al inicio del proyecto")
    return crud.upsert_work_log(db, data)


@router.put("/logs/{log_id}", response_model=schemas.WorkLogResponse)
def update_log(log_id: int, data: schemas.WorkLogUpdate, db: Session = Depends(get_db)):
    log = crud.update_work_log(db, log_id, data)
    if not log:
        raise HTTPException(status_code=404, detail="Registro no encontrado o fecha inválida")
    return log


@router.delete("/logs/{log_id}", status_code=204)
def delete_log(log_id: int, db: Session = Depends(get_db)):
    if not crud.delete_work_log(db, log_id):
        raise HTTPException(status_code=404, detail="Registro no encontrado")


@router.get("/projects/{project_id}/log/{log_date}", response_model=schemas.WorkLogResponse)
def get_log_by_date(project_id: int, log_date: date, db: Session = Depends(get_db)):
    log = crud.get_work_log_by_date(db, project_id, log_date)
    if not log:
        raise HTTPException(status_code=404, detail="Sin registro para esa fecha")
    return log


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/projects/{project_id}/dashboard", response_model=schemas.ProjectDashboard)
def get_dashboard(project_id: int, db: Session = Depends(get_db)):
    dashboard = crud.get_project_dashboard(db, project_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return dashboard


@router.get("/today")
def get_today():
    return {"today": date.today().isoformat()}
