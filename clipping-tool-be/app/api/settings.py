"""
Settings API Endpoints

Handles application settings management and API key testing.
"""

import os
import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models.settings import ApiSettings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=ApiSettings)
async def get_settings():
    """
    Get application settings
    
    Returns:
        Current settings
        
    Raises:
        HTTPException: 500 if failed to load settings
    """
    try:
        settings_file = Path("./data/settings.json")
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
                return ApiSettings(**settings_data)
        else:
            # Return default settings
            return ApiSettings(
                openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
                xai_api_key=os.getenv("XAI_API_KEY", ""),
                api_provider=os.getenv("API_PROVIDER", "openrouter"),
                openrouter_model="tngtech/deepseek-r1t2-chimera:free",
                grok_model="grok-3-mini",
                chunk_size=5000,
                min_score_threshold=0.7,
                max_clips_per_collection=5,
                default_browser="chrome"
            )
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get settings")

@router.post("")
async def update_settings(settings: ApiSettings):
    """
    Update application settings
    
    Args:
        settings: New settings
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 500 if failed to save settings
    """
    try:
        settings_file = Path("./data/settings.json")
        settings_file.parent.mkdir(exist_ok=True)
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings.dict(), f, ensure_ascii=False, indent=2)
        
        # Update environment variables
        os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key
        os.environ["XAI_API_KEY"] = settings.xai_api_key
        os.environ["API_PROVIDER"] = settings.api_provider
        os.environ["OPENROUTER_MODEL"] = settings.openrouter_model
        os.environ["GROK_MODEL"] = settings.grok_model
        
        logger.info("Settings updated successfully")
        return {"message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")

@router.post("/test-api-key")
async def test_api_key(request: dict):
    """
    Test API key connection
    
    Args:
        request: Dict with api_key, provider, and model
        
    Returns:
        Test result with success status
    """
    try:
        api_key = request.get("api_key")
        provider = request.get("provider", "openrouter")
        model = request.get("model")
        
        logger.info(f"Testing API key: provider={provider}, model={model}")
        
        if not api_key:
            return {"success": False, "error": "API key cannot be empty"}
        
        # TODO: Implement actual API key testing when LLMFactory is updated
        # For now, return a placeholder response
        try:
            # from app.utils.llm import LLMFactory
            # success = LLMFactory.test_connection(provider=provider, api_key=api_key, model=model)
            
            logger.info("API key test - implementation pending")
            return {
                "success": True,
                "message": "API key test endpoint - implementation pending"
            }
        except Exception as e:
            logger.error(f"API key test failed: {e}")
            return {"success": False, "error": f"API key test failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Failed to test API key: {e}")
        return {"success": False, "error": "Error occurred during test"}
