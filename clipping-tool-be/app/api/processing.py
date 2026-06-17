"""
Processing API Endpoints

Handles video processing operations, status tracking, and logs.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from app.models import ProjectStatus
from app.services import project_service
from app.core.exceptions import ProjectNotFoundException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["processing"])

# TODO: Processing logic will be implemented when we create processing_service.py
# For now, creating the API structure

@router.post("/{project_id}/process")
async def start_processing(project_id: str, background_tasks: BackgroundTasks):
    """
    Start processing a project
    
    Args:
        project_id: Project ID
        background_tasks: FastAPI background tasks
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if project not found, 400 if status invalid
    """
    try:
        project = project_service.get_project(project_id)
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    if project.status not in ["uploading", "error", "completed"]: # Allow re-run if completed or error
        raise HTTPException(status_code=400, detail=f"Project status '{project.status}' does not allow processing")
    
    # Start processing via service
    from app.services.processing_service import processing_service
    await processing_service.start_processing(project_id, background_tasks)
    
    logger.info(f"Started processing for project: {project_id}")
    return {"message": "Processing started"}

@router.post("/{project_id}/retry")
async def retry_project_processing(project_id: str, background_tasks: BackgroundTasks):
    """
    Retry processing a failed project
    
    Args:
        project_id: Project ID
        background_tasks: FastAPI background tasks
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if project not found, 400 if status not error
    """
    try:
        project = project_service.get_project(project_id)
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    if project.status != "error":
        raise HTTPException(status_code=400, detail="Only failed projects can be retried")
    
    # For now, retry restarts the pipeline. 
    # Future improvement: Retry from specific step.
    
    # Start processing via service
    from app.services.processing_service import processing_service
    await processing_service.start_processing(project_id, background_tasks)
    
    logger.info(f"Retrying project {project_id}")
    return {"message": "Retry started"}

@router.get("/{project_id}/status", response_model=ProjectStatus)
async def get_processing_status(project_id: str):
    """
    Get project processing status
    
    Args:
        project_id: Project ID
        
    Returns:
        Processing status
        
    Raises:
        HTTPException: 404 if project not found
    """
    try:
        project = project_service.get_project(project_id)
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Check if there's a processing status record
    status = project_service.get_processing_status(project_id)
    if status:
        return status
    
    # Return default status based on project status
    if project.status == "completed":
        return ProjectStatus(
            status="completed",
            current_step=6,
            total_steps=6,
            step_name="Processing completed",
            progress=100.0
        )
    elif project.status == "error":
        return ProjectStatus(
            status="error",
            current_step=0,
            total_steps=6,
            step_name="Processing failed",
            progress=0,
            error_message=project.error_message or "Error occurred during processing"
        )
    else:
        return ProjectStatus(
            status="processing",
            current_step=0,
            total_steps=6,
            step_name="Preparing to process",
            progress=0
        )

@router.get("/{project_id}/logs")
async def get_project_logs(project_id: str):
    """
    Get project processing logs
    
    Args:
        project_id: Project ID
        
    Returns:
        Log file content
        
    Raises:
        HTTPException: 404 if project or logs not found
    """
    try:
        project = project_service.get_project(project_id)
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Find log file
    log_file = Path("./uploads") / project_id / "logs" / "processing.log"
    
    if not log_file.exists():
        raise HTTPException(status_code=404, detail="Log file not found")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.read()
        return {"logs": logs}
    except Exception as e:
        logger.error(f"Failed to read logs for {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read log file")
