"""
Pydantic Models - Settings Models

Models related to application settings.
"""

from pydantic import BaseModel
from typing import Optional

class ApiSettings(BaseModel):
    """API settings model"""
    openrouter_api_key: str = ""
    xai_api_key: str = ""  # xAI (Grok) API key
    api_provider: str = "openrouter"  # openrouter or grok
    openrouter_model: str = "tngtech/deepseek-r1t2-chimera:free"
    grok_model: str = "grok-3-mini"
    chunk_size: int = 5000
    min_score_threshold: float = 0.7
    max_clips_per_collection: int = 5
    default_browser: Optional[str] = None
