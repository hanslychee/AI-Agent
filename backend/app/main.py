"""RecruitAI — AI recruitment assistant API.

Run locally:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import ensure_admin_user
from .database import Base, SessionLocal, engine
from .routers import (
    analysis_router,
    auth_router,
    candidates_router,
    dashboard_router,
    jobs_router,
)

app = FastAPI(
    title="RecruitAI",
    description=(
        "AI recruitment assistant for HR teams: CV screening, scoring, interview "
        "preparation, structured evaluation and final reports. "
        "Final hiring decisions must be reviewed and approved by a human "
        "recruiter or hiring manager."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(jobs_router.router)
app.include_router(candidates_router.router)
app.include_router(analysis_router.router)
app.include_router(dashboard_router.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_admin_user(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}
