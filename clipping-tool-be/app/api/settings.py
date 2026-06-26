"""
Settings API Endpoints

Handles application settings management and API key testing.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.config import config_manager
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
        return ApiSettings(**config_manager.settings.model_dump())
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
        config_manager.update_settings(**settings.model_dump())
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
