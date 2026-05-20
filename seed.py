"""
Seed script - imports NixAI-Eval project data from the Excel file.
Run once after creating the database:
  python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, create_tables
from app.models import Project, WorkLog
from datetime import date

NIXAI_LOGS = [
    ("2025-06-14", 3.0), ("2025-06-16", 2.0), ("2025-06-18", 2.0), ("2025-06-19", 2.0),
    ("2025-06-23", 4.0), ("2025-06-24", 4.0), ("2025-06-27", 4.0), ("2025-06-28", 4.0),
    ("2025-07-07", 4.0), ("2025-07-08", 4.0), ("2025-07-11", 4.0), ("2025-07-12", 4.0),
    ("2025-07-14", 4.0), ("2025-07-21", 4.0), ("2025-07-22", 4.0), ("2025-07-23", 4.0),
    ("2025-08-05", 4.0), ("2025-08-08", 4.0), ("2025-08-09", 4.0), ("2025-08-18", 3.0),
    ("2025-08-19", 4.0), ("2025-08-22", 6.0), ("2025-08-25", 4.0), ("2025-08-26", 4.0),
    ("2025-08-29", 4.0), ("2025-08-30", 4.0), ("2025-09-09", 4.0), ("2025-09-12", 4.0),
    ("2025-09-13", 6.0), ("2025-09-26", 4.0), ("2025-09-27", 5.0), ("2025-10-21", 6.0),
    ("2025-10-24", 6.0), ("2025-10-28", 6.0), ("2025-12-26", 4.0), ("2025-12-27", 3.0),
    ("2026-01-05", 4.0), ("2026-01-06", 4.0), ("2026-01-07", 3.0), ("2026-01-08", 3.0),
    ("2026-01-09", 4.0), ("2026-01-10", 3.0), ("2026-01-12", 4.0), ("2026-01-23", 3.0),
    ("2026-01-24", 2.0), ("2026-01-27", 3.0), ("2026-01-28", 3.0), ("2026-02-16", 3.0),
    ("2026-02-18", 3.0), ("2026-02-20", 5.0), ("2026-02-23", 3.0), ("2026-02-25", 3.0),
    ("2026-02-27", 5.0), ("2026-03-02", 3.0), ("2026-03-03", 1.0), ("2026-03-04", 2.0),
    ("2026-03-13", 4.0), ("2026-03-23", 6.0), ("2026-03-25", 6.0), ("2026-03-27", 6.0),
    ("2026-03-30", 6.0), ("2026-03-31", 6.0), ("2026-04-11", 6.0), ("2026-04-13", 4.0),
    ("2026-04-17", 4.0), ("2026-04-20", 6.0), ("2026-04-24", 4.0), ("2026-04-27", 6.0),
    ("2026-05-01", 4.0), ("2026-05-04", 6.0),
]


def seed():
    create_tables()
    db = SessionLocal()
    try:
        # Check if NixAI already exists
        existing = db.query(Project).filter(Project.name == "NixAI-Eval").first()
        if existing:
            print("NixAI-Eval project already exists, skipping seed.")
            return

        project = Project(
            name="NixAI-Eval",
            description="Evaluación de sistema multi-agente NixAI",
            start_date=date(2025, 6, 14),
            color="#6366f1"
        )
        db.add(project)
        db.flush()

        for date_str, hours in NIXAI_LOGS:
            log = WorkLog(
                project_id=project.id,
                log_date=date.fromisoformat(date_str),
                hours=hours
            )
            db.add(log)

        db.commit()
        print(f"✅ NixAI-Eval imported: {len(NIXAI_LOGS)} entries, 296h total")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
