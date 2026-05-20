from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Project, WorkLog
from app.schemas import (
    ProjectCreate, ProjectUpdate,
    WorkLogCreate, WorkLogUpdate,
    ProjectDashboard, DailyHours, WeekdayStats, MonthlyAvg, ProjectResponse
)
from datetime import date
from typing import List, Optional
import calendar

WEEKDAY_NAMES_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

MONTH_NAMES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


# ── Projects ──────────────────────────────────────────────────────────────────

def get_projects(db: Session) -> List[Project]:
    projects = db.query(Project).order_by(Project.start_date.desc()).all()
    for p in projects:
        p.total_hours = db.query(func.sum(WorkLog.hours)).filter(WorkLog.project_id == p.id).scalar() or 0.0
    return projects


def get_project(db: Session, project_id: int) -> Optional[Project]:
    p = db.query(Project).filter(Project.id == project_id).first()
    if p:
        p.total_hours = db.query(func.sum(WorkLog.hours)).filter(WorkLog.project_id == p.id).scalar() or 0.0
    return p


def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    project.total_hours = 0.0
    return project


def update_project(db: Session, project_id: int, data: ProjectUpdate) -> Optional[Project]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    project.total_hours = db.query(func.sum(WorkLog.hours)).filter(WorkLog.project_id == project_id).scalar() or 0.0
    return project


def delete_project(db: Session, project_id: int) -> bool:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True


# ── WorkLogs ──────────────────────────────────────────────────────────────────

def get_work_logs(db: Session, project_id: int) -> List[WorkLog]:
    return db.query(WorkLog).filter(WorkLog.project_id == project_id).order_by(WorkLog.log_date.desc()).all()


def get_work_log_by_date(db: Session, project_id: int, log_date: date) -> Optional[WorkLog]:
    return db.query(WorkLog).filter(
        WorkLog.project_id == project_id,
        WorkLog.log_date == log_date
    ).first()


def upsert_work_log(db: Session, data: WorkLogCreate) -> WorkLog:
    existing = get_work_log_by_date(db, data.project_id, data.log_date)
    if existing:
        existing.hours = data.hours
        existing.notes = data.notes
        db.commit()
        db.refresh(existing)
        return existing
    log = WorkLog(**data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_work_log(db: Session, log_id: int, data: WorkLogUpdate) -> Optional[WorkLog]:
    log = db.query(WorkLog).filter(WorkLog.id == log_id).first()
    if not log:
        return None
    if log.log_date > date.today():
        return None
    log.hours = data.hours
    log.notes = data.notes
    db.commit()
    db.refresh(log)
    return log


def delete_work_log(db: Session, log_id: int) -> bool:
    log = db.query(WorkLog).filter(WorkLog.id == log_id).first()
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True


# ── Dashboard ─────────────────────────────────────────────────────────────────

def get_project_dashboard(db: Session, project_id: int) -> Optional[ProjectDashboard]:
    project = get_project(db, project_id)
    if not project:
        return None

    logs = db.query(WorkLog).filter(
        WorkLog.project_id == project_id,
        WorkLog.hours > 0
    ).order_by(WorkLog.log_date).all()

    daily_logs = [
        DailyHours(log_date=l.log_date, hours=l.hours, notes=l.notes)
        for l in logs
    ]

    # Weekday stats
    weekday_data: dict = {}
    for l in logs:
        wd = l.log_date.weekday()
        if wd not in weekday_data:
            weekday_data[wd] = {"total": 0.0, "count": 0}
        weekday_data[wd]["total"] += l.hours
        weekday_data[wd]["count"] += 1

    weekday_stats = []
    for wd in range(7):
        d = weekday_data.get(wd, {"total": 0.0, "count": 0})
        weekday_stats.append(WeekdayStats(
            weekday=WEEKDAY_NAMES_ES[wd],
            weekday_num=wd,
            total_hours=round(d["total"], 2),
            avg_hours=round(d["total"] / d["count"], 2) if d["count"] > 0 else 0.0,
            count=d["count"]
        ))

    # Monthly averages
    monthly_data: dict = {}
    for l in logs:
        key = (l.log_date.year, l.log_date.month)
        if key not in monthly_data:
            monthly_data[key] = {"total": 0.0, "days": set()}
        monthly_data[key]["total"] += l.hours
        monthly_data[key]["days"].add(l.log_date)

    monthly_averages = []
    for (year, month), data in sorted(monthly_data.items()):
        days_count = len(data["days"])
        monthly_averages.append(MonthlyAvg(
            year=year,
            month=month,
            month_name=MONTH_NAMES_ES[month],
            total_hours=round(data["total"], 2),
            avg_daily_hours=round(data["total"] / days_count, 2) if days_count > 0 else 0.0,
            working_days=days_count
        ))

    total_hours = sum(l.hours for l in logs)
    total_days = len(set(l.log_date for l in logs))

    proj_resp = ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        color=project.color,
        total_hours=round(total_hours, 2)
    )

    return ProjectDashboard(
        project=proj_resp,
        daily_logs=daily_logs,
        weekday_stats=weekday_stats,
        monthly_averages=monthly_averages,
        total_hours=round(total_hours, 2),
        total_days_worked=total_days,
        avg_hours_per_day=round(total_hours / total_days, 2) if total_days > 0 else 0.0
    )
