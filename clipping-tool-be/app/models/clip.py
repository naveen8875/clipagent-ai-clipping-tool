"""
Pydantic Models - Clip Models

Models related to video clips.
"""

from pydantic import BaseModel
from typing import List, Optional

class Clip(BaseModel):
    """Video clip model"""
    id: str
    title: Optional[str] = None
    start_time: str
    end_time: str
    final_score: float
    recommend_reason: str
    generated_title: Optional[str] = None
    outline: str
    content: List[str]
    chunk_index: Optional[int] = None

class ClipUpdate(BaseModel):
    """Clip update request model"""
    title: Optional[str] = None
    recommend_reason: Optional[str] = None
    generated_title: Optional[str] = None
