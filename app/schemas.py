from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, List
from datetime import date as date_type


# ── Project schemas ────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_date: date
    color: Optional[str] = "#6366f1"

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if v and not (v.startswith("#") and len(v) == 7):
            raise ValueError("Color must be a hex color like #6366f1")
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: date
    color: str
    total_hours: Optional[float] = 0.0

    model_config = {"from_attributes": True}


# ── WorkLog schemas ────────────────────────────────────────────────────────────

class WorkLogCreate(BaseModel):
    project_id: int
    log_date: date
    hours: float = Field(..., ge=0, le=24)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("log_date")
    @classmethod
    def validate_date_not_future(cls, v):
        today = date_type.today()
        if v > today:
            raise ValueError("No se pueden registrar horas para fechas futuras")
        return v


class WorkLogUpdate(BaseModel):
    hours: float = Field(..., ge=0, le=24)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("hours")
    @classmethod
    def validate_hours(cls, v):
        if v < 0 or v > 24:
            raise ValueError("Las horas deben estar entre 0 y 24")
        return v


class WorkLogResponse(BaseModel):
    id: int
    project_id: int
    log_date: date
    hours: float
    notes: Optional[str]

    model_config = {"from_attributes": True}


# ── Dashboard schemas ──────────────────────────────────────────────────────────

class DailyHours(BaseModel):
    log_date: date
    hours: float
    notes: Optional[str] = None


class WeekdayStats(BaseModel):
    weekday: str
    weekday_num: int
    total_hours: float
    avg_hours: float
    count: int


class MonthlyAvg(BaseModel):
    year: int
    month: int
    month_name: str
    total_hours: float
    avg_daily_hours: float
    working_days: int


class ProjectDashboard(BaseModel):
    project: ProjectResponse
    daily_logs: List[DailyHours]
    weekday_stats: List[WeekdayStats]
    monthly_averages: List[MonthlyAvg]
    total_hours: float
    total_days_worked: int
    avg_hours_per_day: float
