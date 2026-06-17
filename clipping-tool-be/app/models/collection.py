"""
Pydantic Models - Collection Models

Models related to clip collections.
"""

from pydantic import BaseModel
from typing import List, Optional

class Collection(BaseModel):
    """Clip collection model"""
    id: str
    collection_title: str
    collection_summary: str
    clip_ids: List[str]
    collection_type: str = "ai_recommended"  # "ai_recommended" or "manual"
    created_at: Optional[str] = None

class CollectionUpdate(BaseModel):
    """Collection update request model"""
    collection_title: Optional[str] = None
    collection_summary: Optional[str] = None
    clip_ids: Optional[List[str]] = None
