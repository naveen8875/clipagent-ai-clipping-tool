"""
OpenRouter API Client - Wrapper for OpenRouter API calls
"""
import json
import logging
import os
import re
import time
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """OpenRouter API Client"""
    
    def __init__(self, api_key: str = None, model: str = "tngtech/deepseek-r1t2-chimera:free"):
        """
        Initialize OpenRouter client
        
        Args:
            api_key: API key, if None will read from environment variable
            model: Model name
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.max_tokens = 8000
        self.timeout = 60.0
        
        if not self.api_key:
            raise ValueError("Please configure OpenRouter API key via OPENROUTER_API_KEY environment variable.")
    
    def call(self, prompt: str, input_data: Any = None) -> str:
        """
        Call OpenRouter API
        
        Args:
            prompt: Prompt text
            input_data: Input data
            
        Returns:
            Model response text
        """
        try:
            # Build complete input
            if input_data:
                if isinstance(input_data, dict):
                    full_input = f"{prompt}\n\nInput:\n{json.dumps(input_data, ensure_ascii=False, indent=2)}"
                else:
                    full_input = f"{prompt}\n\nInput:\n{input_data}"
            else:
                full_input = prompt
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://clipagent.app",
                "X-Title": "ClipAgent Video Processor"
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
            
            # Use synchronous httpx client
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
                    logger.warning("API request successful but output is empty")
                    return ""
            else:
                error_msg = "API call failed, no valid response returned"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"OpenRouter API call exception: {str(e)}")
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
                    logger.error(f"OpenRouter API call failed after {max_retries} retries.")
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
            """Enhanced sanitization function to remove characters that may cause JSON parsing failures"""
            s = s.lstrip('\ufeff')
            s = s.strip()
            s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
            return s
        
        def fix_common_json_errors(json_str: str) -> str:
            """Fix common JSON format errors"""
            original_str = json_str
            json_str = re.sub(r'}\s*{', '},{', json_str)
            json_str = re.sub(r']\s*\[', '],[', json_str)
            json_str = re.sub(r'}\s*\n\s*{', '},\n{', json_str)
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            json_str = re.sub(r"'([^']*?)'\s*:", r'"\1":', json_str)
            json_str = re.sub(r":\s*'([^']*?)'", r': "\1"', json_str)
            json_str = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":', json_str)
            json_str = re.sub(r'\n\s*\n', '\n', json_str)
            
            open_braces = json_str.count('{')
            close_braces = json_str.count('}')
            open_brackets = json_str.count('[')
            close_brackets = json_str.count(']')
            
            if open_braces > close_braces:
                json_str += '}' * (open_braces - close_braces)
            if open_brackets > close_brackets:
                json_str += ']' * (open_brackets - close_brackets)
            
            if json_str != original_str:
                logger.debug(f"JSON before fix: {original_str[:100]}...")
                logger.debug(f"JSON after fix: {json_str[:100]}...")
            
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
        logger.debug(f"Preprocessed response: {response[:200]}...")
        
        # 1. First try to extract from Markdown code block
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response, re.DOTALL)
        if match:
            json_str = sanitize_string(match.group(1))
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse content from Markdown: {e}. Will try to fix and parse.")
                try:
                    fixed_json = fix_common_json_errors(json_str)
                    return json.loads(fixed_json)
                except json.JSONDecodeError:
                    logger.warning("Still failed after fix, will try to parse entire response.")
        
        # 2. If no Markdown or Markdown parsing failed, try entire response
        try:
            sanitized_response = sanitize_string(response)
            return json.loads(sanitized_response)
        except json.JSONDecodeError:
            # 3. If direct parsing also failed, try regex to find JSON
            logger.warning("Direct parsing failed, trying regex to find JSON...")
            json_match = re.search(r'\[[\s\S]*\]|\{[\s\S]*\}', response, re.DOTALL)
            if json_match:
                json_str = sanitize_string(json_match.group())
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    # 4. Final attempt: fix common errors
                    try:
                        fixed_json = fix_common_json_errors(json_str)
                        return json.loads(fixed_json)
                    except json.JSONDecodeError as final_e:
                        logger.error(f"Final parsing attempt failed: {final_e}")
                        raise ValueError(f"Unable to parse valid JSON from response: {response[:200]}...") from final_e
            
            raise ValueError(f"Unable to parse valid JSON from response: {response[:200]}...")

