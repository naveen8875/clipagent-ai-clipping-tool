"""
Pydantic Models - Base Models

Base models used across the application.
"""

from pydantic import BaseModel
from typing import Optional

class ProjectStatus(BaseModel):
    """Project processing status"""
    status: str  # 'uploading', 'processing', 'completed', 'error'
    current_step: Optional[int] = None
    total_steps: Optional[int] = 6
    step_name: Optional[str] = None
    progress: Optional[float] = 0.0
    error_message: Optional[str] = None
