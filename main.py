from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.database import create_tables
from app.routes import router
import os

app = FastAPI(
    title="Freelance Hours Tracker",
    description="Control de horas trabajadas por proyecto freelance",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    create_tables()


# All API routes live under /api
app.include_router(router, prefix="/api")

# Serve the single-page frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")


@app.get("/", include_in_schema=False)
def serve_root():
    index = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index):
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index)


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    index = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index):
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index)
