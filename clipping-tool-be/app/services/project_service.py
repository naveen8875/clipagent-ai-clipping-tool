"""
Project Service

Handles all project-related business logic including CRUD operations,
file management, and data persistence.
"""

import json
import uuid
import shutil
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.models import Project, Clip, Collection, ProjectStatus
from app.core.exceptions import (
    ProjectNotFoundException,
    ProjectAlreadyExistsException
)

logger = logging.getLogger(__name__)

class ProjectService:
    """Service for managing projects"""
    
    def __init__(self, data_dir: Path = None, uploads_dir: Path = None):
        """
        Initialize project service
        
        Args:
            data_dir: Directory for storing project metadata (default: ./data)
            uploads_dir: Directory for storing uploaded files (default: ./uploads)
        """
        self.projects: Dict[str, Project] = {}
        self.processing_status: Dict[str, ProjectStatus] = {}
        self.data_dir = data_dir or Path("./data")
        self.uploads_dir = uploads_dir or Path("./uploads")
        self.data_dir.mkdir(exist_ok=True)
        self.uploads_dir.mkdir(exist_ok=True)
        self.processing_lock = asyncio.Lock()
        self.max_concurrent_processing = 1
        self.current_processing_count = 0
        self.load_projects()
    
    def load_projects(self):
        """Load projects from disk"""
        projects_file = self.data_dir / "projects.json"
        if not projects_file.exists():
            logger.info("No existing projects file found")
            return
        
        try:
            with open(projects_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Limit loaded projects to avoid memory issues
                if len(data) > 100:
                    logger.warning(f"Too many projects ({len(data)}), loading only the latest 100")
                    data = sorted(data, key=lambda x: x.get('updated_at', ''), reverse=True)[:100]
                
                for project_data in data:
                    try:
                        project = Project(**project_data)
                        self.projects[project.id] = project
                    except Exception as e:
                        logger.error(f"Failed to load project {project_data.get('id', 'unknown')}: {e}")
                        continue
                
                logger.info(f"Successfully loaded {len(self.projects)} projects")
        except Exception as e:
            logger.error(f"Failed to load projects: {e}")
    
    def save_projects(self):
        """Save projects to disk"""
        projects_file = self.data_dir / "projects.json"
        try:
            with open(projects_file, 'w', encoding='utf-8') as f:
                projects_data = [project.dict() for project in self.projects.values()]
                json.dump(projects_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved {len(self.projects)} projects to disk")
        except Exception as e:
            logger.error(f"Failed to save projects: {e}")
            raise
    
    def create_project(
        self, 
        name: str, 
        video_path: str, 
        project_id: str = None, 
        video_category: str = "default"
    ) -> Project:
        """
        Create a new project
        
        Args:
            name: Project name
            video_path: Path to video file
            project_id: Optional project ID (generated if not provided)
            video_category: Video category (default: "default")
            
        Returns:
            Created project
            
        Raises:
            ProjectAlreadyExistsException: If project ID already exists
        """
        if project_id is None:
            project_id = str(uuid.uuid4())
        
        if project_id in self.projects:
            raise ProjectAlreadyExistsException(project_id)
        
        now = datetime.now().isoformat()
        
        project = Project(
            id=project_id,
            name=name,
            video_path=video_path,
            status="uploading",
            created_at=now,
            updated_at=now,
            video_category=video_category
        )
        
        self.projects[project_id] = project
        self.save_projects()
        logger.info(f"Created project: {project_id} ({name})")
        return project
    
    def get_project(self, project_id: str) -> Project:
        """
        Get project by ID
        
        Args:
            project_id: Project ID
            
        Returns:
            Project
            
        Raises:
            ProjectNotFoundException: If project not found
        """
        project = self.projects.get(project_id)
        if not project:
            raise ProjectNotFoundException(project_id)
        
        # Dynamically load latest clips and collections data
        try:
            project_dir = self.uploads_dir / project_id
            metadata_dir = project_dir / "output" / "metadata"
            
            # Load clips data
            clips_file = metadata_dir / "clips_metadata.json"
            if clips_file.exists():
                with open(clips_file, 'r', encoding='utf-8') as f:
                    clips_data = json.load(f)
                    project.clips = [Clip(**clip) for clip in clips_data]
            
            # Load collections data
            collections_file = metadata_dir / "collections_metadata.json"
            if collections_file.exists():
                with open(collections_file, 'r', encoding='utf-8') as f:
                    collections_data = json.load(f)
                    project.collections = [Collection(**collection) for collection in collections_data]
        except Exception as e:
            logger.error(f"Failed to load latest data for project {project_id}: {e}")
        
        return project
    
    def list_projects(self) -> List[Project]:
        """
        List all projects
        
        Returns:
            List of projects
        """
        return list(self.projects.values())
    
    def update_project(self, project_id: str, **updates) -> Project:
        """
        Update project
        
        Args:
            project_id: Project ID
            **updates: Fields to update
            
        Returns:
            Updated project
            
        Raises:
            ProjectNotFoundException: If project not found
        """
        if project_id not in self.projects:
            raise ProjectNotFoundException(project_id)
        
        project = self.projects[project_id]
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        project.updated_at = datetime.now().isoformat()
        self.save_projects()
        logger.info(f"Updated project: {project_id}")
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            ProjectNotFoundException: If project not found
        """
        if project_id not in self.projects:
            raise ProjectNotFoundException(project_id)
        
        # Delete project directory
        try:
            project_dir = self.uploads_dir / project_id
            if project_dir.exists():
                shutil.rmtree(project_dir)
                logger.info(f"Deleted project directory: {project_dir}")
            else:
                logger.warning(f"Project directory not found: {project_dir}")
        except Exception as e:
            logger.error(f"Failed to delete project files: {e}")
            raise
        
        # Delete project record
        del self.projects[project_id]
        if project_id in self.processing_status:
            del self.processing_status[project_id]
        
        self.save_projects()
        logger.info(f"Deleted project: {project_id}")
        return True
    
    def get_processing_status(self, project_id: str) -> Optional[ProjectStatus]:
        """
        Get processing status for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            Processing status or None
        """
        return self.processing_status.get(project_id)
    
    def update_processing_status(self, project_id: str, status: ProjectStatus):
        """
        Update processing status for a project
        
        Args:
            project_id: Project ID
            status: New status
        """
        self.processing_status[project_id] = status
        logger.debug(f"Updated processing status for {project_id}: {status.status}")

# Global project service instance
project_service = ProjectService()
