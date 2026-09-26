from fastapi import FastAPI

from app.core.config import settings
from app.features.incident.router import router as incident_router
from app.features.evidence.router import router as evidence_router
from app.features.investigation.router import router as investigation_router
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel
from app.db.session import get_db
from app.features.incident.model import Incident
from app.features.investigation.model import Investigation

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(
    incident_router,
    prefix="/api/v1",
)

app.include_router(
    evidence_router,
    prefix="/api/v1",
)

app.include_router(
    investigation_router,
    prefix="/api/v1",
)

class DashboardStats(BaseModel):
    total_incidents: int
    open_incidents: int
    investigations_running: int
    investigations_completed: int

@app.get("/api/v1/dashboard/stats", response_model=DashboardStats, tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_incidents = db.scalar(select(func.count(Incident.id))) or 0
    # SQLilke lowercase check or just case-insensitive
    open_incidents = db.scalar(select(func.count(Incident.id)).where(func.lower(Incident.status) == "open")) or 0
    investigations_running = db.scalar(select(func.count(Investigation.id)).where(Investigation.status == "RUNNING")) or 0
    investigations_completed = db.scalar(select(func.count(Investigation.id)).where(Investigation.status == "COMPLETED")) or 0
    
    return DashboardStats(
        total_incidents=total_incidents,
        open_incidents=open_incidents,
        investigations_running=investigations_running,
        investigations_completed=investigations_completed
    )

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}