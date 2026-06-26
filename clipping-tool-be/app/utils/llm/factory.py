"""
LLM Client Factory - Select OpenRouter or Grok based on configuration
"""
import logging
from typing import Optional, Union
from .openrouter_client import OpenRouterClient
from .grok_client import GrokClient
from app.config import config_manager

logger = logging.getLogger(__name__)

class LLMFactory:
    """LLM Client Factory"""
    
    @staticmethod
    def create_client(provider: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None) -> Union[OpenRouterClient, GrokClient]:
        """
        Create LLM client
        
        Args:
            provider: API provider, options: openrouter, grok
            api_key: API key
            model: Model name
            
        Returns:
            LLM client instance
        """
        # If provider not specified, get from config
        if provider is None:
            provider = config_manager.settings.api_provider

        if provider == "openrouter":
            # Use OpenRouter API
            if api_key is None:
                api_key = config_manager.settings.openrouter_api_key
            if model is None:
                model = config_manager.settings.openrouter_model
            
            logger.info(f"Creating OpenRouter client, model: {model}")
            return OpenRouterClient(api_key=api_key, model=model)
        
        elif provider == "grok":
            # Use Grok (xAI) API
            if api_key is None:
                api_key = config_manager.settings.xai_api_key
            if model is None:
                model = config_manager.settings.grok_model
            
            logger.info(f"Creating Grok client, model: {model}")
            return GrokClient(api_key=api_key, model=model)
            
        else:
            raise ValueError(f"Unsupported API provider: {provider}, supported values: openrouter, grok")
    
    @staticmethod
    def get_default_client() -> Union[OpenRouterClient, GrokClient]:
        """
        Get default LLM client
        
        Returns:
            Default LLM client instance
        """
        return LLMFactory.create_client()
    
    @staticmethod
    def test_connection(provider: str, api_key: str, model: Optional[str] = None) -> bool:
        """
        Test API connection
        
        Args:
            provider: API provider
            api_key: API key
            model: Model name
            
        Returns:
            Whether connection is successful
        """
        try:
            logger.info(f"Testing API connection: provider={provider}, model={model}")
            client = LLMFactory.create_client(provider=provider, api_key=api_key, model=model)
            # Send a simple test request
            test_response = client.call("Please reply with 'test successful'", "This is a connection test")
            logger.info(f"API test response: {test_response[:100]}...")
            
            # Consider connection successful if API returns a response
            if test_response and len(test_response.strip()) > 0:
                logger.info("API connection test successful")
                return True
            else:
                logger.warning("API returned empty response")
                return False
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
 
