"""
Pydantic Models - Project Models

Models related to projects.
"""

from pydantic import BaseModel
from typing import List, Optional
from app.models.clip import Clip
from app.models.collection import Collection

class Project(BaseModel):
    """Project model"""
    id: str
    name: str
    video_path: str
    status: str
    created_at: str
    updated_at: str
    video_category: str = "default"
    clips: List[Clip] = []
    collections: List[Collection] = []
    current_step: Optional[int] = None
    total_steps: Optional[int] = 6
    error_message: Optional[str] = None
