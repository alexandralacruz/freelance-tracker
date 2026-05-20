from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    start_date = Column(Date, nullable=False)
    color = Column(String(7), default="#6366f1")  # hex color
    created_at = Column(DateTime, default=datetime.utcnow)

    work_logs = relationship("WorkLog", back_populates="project", cascade="all, delete-orphan")


class WorkLog(Base):
    __tablename__ = "work_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    log_date = Column(Date, nullable=False)
    hours = Column(Float, nullable=False, default=0.0)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="work_logs")

    __table_args__ = (
        UniqueConstraint("project_id", "log_date", name="uq_project_date"),
    )
