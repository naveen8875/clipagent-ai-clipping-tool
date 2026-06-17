"""
ClipAgent Backend - Main FastAPI Application

This is the main entry point for the ClipAgent backend API server.
It provides RESTful endpoints for video processing, project management,
and local clipping workflows.
"""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.logging import setup_logging
from app.core.exceptions import ClipAgentException
from app.api import api_router
from app.config import config_manager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="ClipAgent Backend API",
    description="AI-powered video clipping and collection recommendation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware (disabled for now, can be enabled later)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include API router with /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")

# Global exception handler
@app.exception_handler(ClipAgentException)
async def clipagent_exception_handler(request, exc: ClipAgentException):
    """Handle custom ClipAgent exceptions"""
    logger.error(f"ClipAgent error: {exc.message}", exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "details": exc.details}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting ClipAgent Backend API...")
    
    # Ensure required directories exist
    config_manager.get_path_config().data_dir.mkdir(parents=True, exist_ok=True)
    config_manager.get_path_config().uploads_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("ClipAgent Backend API started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down ClipAgent Backend API...")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "ClipAgent Backend API",
        "version": "1.0.0",
        "description": "AI-powered video clipping system",
        "docs": "/api/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
