"""
API Router Aggregation

Combines all API routers with /api/v1 prefix.
"""

from fastapi import APIRouter
from app.api import health, projects, settings, processing

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health.router)
api_router.include_router(projects.router)
api_router.include_router(settings.router)
api_router.include_router(processing.router)
