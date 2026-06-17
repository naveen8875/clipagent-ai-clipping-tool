"""
Projects API Endpoints

Handles project CRUD operations, file uploads, and file serving.
"""

import uuid
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

from app.models import Project
from app.services import project_service
from app.core.exceptions import ProjectNotFoundException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=List[Project])
async def list_projects():
    """
    List all projects
    
    Returns:
        List of all projects
    """
    try:
        projects = project_service.list_projects()
        return projects
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        return []

@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """
    Get project by ID
    
    Args:
        project_id: Project ID
        
    Returns:
        Project details
        
    Raises:
        HTTPException: 404 if project not found
    """
    try:
        project = project_service.get_project(project_id)
        return project
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("", response_model=Project)
async def upload_files(
    video_file: UploadFile = File(...),
    srt_file: Optional[UploadFile] = File(None),
    project_name: str = Form(...),
    video_category: str = Form("default")
):
    """
    Upload video and subtitle files to create a new project
    
    Args:
        video_file: Video file (mp4, avi, mov, mkv)
        srt_file: Optional SRT subtitle file
        project_name: Project name
        video_category: Video category (default: "default")
        
    Returns:
        Created project
        
    Raises:
        HTTPException: 400 if file format is invalid
    """
    # Validate video file type
    if not video_file.filename or not video_file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Unsupported video format")
    
    # Create project ID and directories
    project_id = str(uuid.uuid4())
    project_dir = Path("./uploads") / project_id
    input_dir = project_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    
    # Save video file
    video_extension = video_file.filename.split('.')[-1]
    video_path = input_dir / f"input.{video_extension}"
    with open(video_path, "wb") as f:
        content = await video_file.read()
        f.write(content)
    
    # Save subtitle file if provided
    if srt_file:
        srt_path = input_dir / "input.srt"
        with open(srt_path, "wb") as f:
            content = await srt_file.read()
            f.write(content)
    
    # Create project record
    relative_video_path = f"uploads/{project_id}/input/input.{video_extension}"
    project = project_service.create_project(
        name=project_name,
        video_path=relative_video_path,
        project_id=project_id,
        video_category=video_category
    )
    
    logger.info(f"Created project {project_id} with video upload")
    return project

@router.put("/{project_id}/category")
async def update_project_category(
    project_id: str,
    video_category: str = Form(...)
):
    """
    Update project video category
    
    Args:
        project_id: Project ID
        video_category: New video category
        
    Returns:
        Success message with updated category
        
    Raises:
        HTTPException: 404 if project not found
    """
    try:
        # Note: Category validation should be added here if needed
        # For now, accepting any string value
        
        project_service.update_project(project_id, video_category=video_category)
        
        return {
            "message": "Project category updated successfully",
            "video_category": video_category
        }
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update category for {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """
    Delete project and all associated files
    
    Args:
        project_id: Project ID
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if project not found
    """
    try:
        project_service.delete_project(project_id)
        return {"message": "Project deleted successfully"}
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{project_id}/files/{file_path:path}")
async def get_project_file(project_id: str, file_path: str):
    """
    Get a file from the project directory
    
    Args:
        project_id: Project ID
        file_path: Relative file path within project directory
        
    Returns:
        File response
        
    Raises:
        HTTPException: 404 if project or file not found, 403 if access denied
    """
    try:
        project = project_service.get_project(project_id)
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Build file path
    full_file_path = Path("./uploads") / project_id / file_path
    
    if not full_file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security check: ensure file is within project directory
    try:
        full_file_path.resolve().relative_to(Path("./uploads").resolve() / project_id)
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(path=full_file_path)

@router.get("/{project_id}/clips/{clip_id}")
async def get_clip_video(project_id: str, clip_id: str):
    """
    Get clip video file by clip ID
    
    Args:
        project_id: Project ID
        clip_id: Clip ID
        
    Returns:
        Video file response
        
    Raises:
        HTTPException: 404 if project, clips directory, or video file not found
    """
    try:
        project = project_service.get_project(project_id)
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Find clip video file
    clips_dir = Path("./uploads") / project_id / "output" / "clips"
    if not clips_dir.exists():
        raise HTTPException(status_code=404, detail="Clips directory not found")
    
    # Find matching file (clip files are named: {clip_id}_*.mp4)
    matching_files = list(clips_dir.glob(f"{clip_id}_*.mp4"))
    if not matching_files:
        raise HTTPException(status_code=404, detail="Clip video file not found")
    
    # Return first matching file
    video_file = matching_files[0]
    return FileResponse(
        path=video_file,
        media_type='video/mp4',
        headers={
            'Accept-Ranges': 'bytes',
            'Cache-Control': 'no-cache'
        }
    )
