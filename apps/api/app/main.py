from fastapi import FastAPI

from app.core.config import settings
from app.features.incident.router import router as incident_router
from app.features.evidence.router import router as evidence_router
from app.features.investigation.router import router as investigation_router

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

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}