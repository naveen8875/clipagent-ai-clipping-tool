"""
Grok (xAI) API Client - Wrapper for xAI Grok API calls
Uses the xai_sdk library for API communication.
"""
import json
import logging
import os
import re
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import xai_sdk, fall back to httpx if not available
try:
    from xai_sdk import Client as XAIClient
    XAI_SDK_AVAILABLE = True
except ImportError:
    XAI_SDK_AVAILABLE = False
    import httpx
    logger.warning("xai_sdk not installed, using httpx fallback for Grok API")


class GrokClient:
    """Grok (xAI) API Client"""
    
    def __init__(self, api_key: str = None, model: str = "grok-3-mini"):
        """
        Initialize Grok client
        
        Args:
            api_key: API key, if None will read from environment variable
            model: Model name (default: grok-3-mini)
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.model = model
        self.base_url = "https://api.x.ai/v1/chat/completions"
        self.max_tokens = 8000
        self.timeout = 120.0  # Grok can take longer for complex prompts
        
        if not self.api_key:
            raise ValueError("Please configure xAI API key via XAI_API_KEY environment variable.")
        
        # Initialize the appropriate client
        if XAI_SDK_AVAILABLE:
            self.xai_client = XAIClient(api_key=self.api_key)
            logger.info("Using xai_sdk for Grok API")
        else:
            self.xai_client = None
            logger.info("Using httpx for Grok API")
    
    def call(self, prompt: str, input_data: Any = None) -> str:
        """
        Call Grok API
        
        Args:
            prompt: Prompt text
            input_data: Input data
            
        Returns:
            Model response text
        """
        # Build complete input
        if input_data:
            if isinstance(input_data, dict):
                full_input = f"{prompt}\n\nInput:\n{json.dumps(input_data, ensure_ascii=False, indent=2)}"
            else:
                full_input = f"{prompt}\n\nInput:\n{input_data}"
        else:
            full_input = prompt
        
        if XAI_SDK_AVAILABLE and self.xai_client:
            return self._call_with_sdk(full_input)
        else:
            return self._call_with_httpx(full_input)
    
    def _call_with_sdk(self, full_input: str) -> str:
        """Call Grok using xai_sdk"""
        try:
            from xai_sdk.chat import user
            
            chat = self.xai_client.chat.create(
                model=self.model,
                messages=[user(full_input)],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            response = chat.sample()
            content = response.content
            
            if content:
                return content
            else:
                logger.warning("Grok API request successful but output is empty")
                return ""
                
        except Exception as e:
            logger.error(f"Grok SDK call exception: {str(e)}")
            raise
    
    def _call_with_httpx(self, full_input: str) -> str:
        """Call Grok using httpx (fallback)"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": full_input
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": 0.7
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.base_url,
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
            
            # Check response
            if result and "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"]
                if content:
                    return content
                else:
                    logger.warning("Grok API request successful but output is empty")
                    return ""
            else:
                error_msg = "Grok API call failed, no valid response returned"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Grok API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Grok API call exception: {str(e)}")
            raise
    
    def call_with_retry(self, prompt: str, input_data: Any = None, max_retries: int = 3) -> str:
        """
        API call with retry mechanism
        
        Args:
            prompt: Prompt text
            input_data: Input data
            max_retries: Maximum retry attempts
            
        Returns:
            Model response text
        """
        for attempt in range(max_retries):
            try:
                return self.call(prompt, input_data)
            except ValueError:  # Don't retry on API key or parameter errors
                raise
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Grok API call failed after {max_retries} retries.")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
        return ""  # Ensure all paths have a return value
    
    def parse_json_response(self, response: str) -> Any:
        """
        Parse JSON object from text that may contain Markdown formatting.
        This function has multiple fallback mechanisms.
        """
        
        def sanitize_string(s: str) -> str:
            """Enhanced sanitization function"""
            s = s.lstrip('\ufeff')
            s = s.strip()
            s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
            return s
        
        def fix_common_json_errors(json_str: str) -> str:
            """Fix common JSON format errors"""
            json_str = re.sub(r'}\s*{', '},{', json_str)
            json_str = re.sub(r']\s*\[', '],[', json_str)
            json_str = re.sub(r'}\s*\n\s*{', '},\n{', json_str)
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            open_braces = json_str.count('{')
            close_braces = json_str.count('}')
            open_brackets = json_str.count('[')
            close_brackets = json_str.count(']')
            
            if open_braces > close_braces:
                json_str += '}' * (open_braces - close_braces)
            if open_brackets > close_brackets:
                json_str += ']' * (open_brackets - close_brackets)
            
            return json_str

        def _preprocess_llm_response(response: str) -> str:
            """Preprocess LLM response, remove common non-JSON content"""
            lines = response.split('\n')
            json_start = -1
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('[') or stripped.startswith('{'):
                    json_start = i
                    break
            
            if json_start >= 0:
                response = '\n'.join(lines[json_start:])
            
            if '```' in response:
                parts = response.split('```')
                if len(parts) > 1:
                    response = parts[0]
            
            return response.strip()

        response = response.strip()
        response = _preprocess_llm_response(response)
        
        # 1. First try to extract from Markdown code block
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response, re.DOTALL)
        if match:
            json_str = sanitize_string(match.group(1))
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                try:
                    fixed_json = fix_common_json_errors(json_str)
                    return json.loads(fixed_json)
                except json.JSONDecodeError:
                    pass
        
        # 2. Try entire response
        try:
            sanitized_response = sanitize_string(response)
            return json.loads(sanitized_response)
        except json.JSONDecodeError:
            # 3. Try regex to find JSON
            json_match = re.search(r'\[[\s\S]*\]|\{[\s\S]*\}', response, re.DOTALL)
            if json_match:
                json_str = sanitize_string(json_match.group())
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    try:
                        fixed_json = fix_common_json_errors(json_str)
                        return json.loads(fixed_json)
                    except json.JSONDecodeError as final_e:
                        raise ValueError(f"Unable to parse valid JSON from response: {response[:200]}...") from final_e
            
            raise ValueError(f"Unable to parse valid JSON from response: {response[:200]}...")
    
    def _validate_json_structure(self, parsed_data: Any) -> bool:
        """
        Validate JSON structure
        
        Args:
            parsed_data: Parsed JSON data
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not isinstance(parsed_data, list):
                logger.error(f"Response is not an array, actual type: {type(parsed_data)}")
                return False
            
            for i, item in enumerate(parsed_data):
                if not isinstance(item, dict):
                    logger.error(f"Element {i} is not an object, actual type: {type(item)}")
                    return False
                    
                # Check basic fields (adjustable based on needs)
                if 'outline' in item or 'start_time' in item or 'end_time' in item:
                    required_fields = ['outline', 'start_time', 'end_time']
                    for field in required_fields:
                        if field not in item:
                            logger.error(f"Element {i} missing required field: {field}")
                            return False
        except Exception as e:
            logger.error(f"Error validating JSON structure: {e}")
            return False
        
        return True

