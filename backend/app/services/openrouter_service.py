"""
OpenRouter API Service
Handles API calls to OpenRouter for free Llama models
"""

import httpx
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.services.embedding_service import multilingual_embedding_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom exceptions for better error handling
class APIError(Exception):
    """Base exception for API errors"""
    pass

class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded"""
    pass

class AuthenticationError(APIError):
    """Exception raised when API authentication fails"""
    pass

class OpenRouterService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.site_url = settings.SITE_URL
        self.site_name = settings.SITE_NAME
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Send chat completion request to OpenRouter"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.site_name,
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit exceeded
                    error_data = response.json() if response.text else {}
                    error_message = error_data.get("error", {}).get("message", "Rate limit exceeded")
                    print(f"OpenRouter rate limit exceeded: {error_message}")
                    raise RateLimitError(f"API rate limit exceeded. {error_message}")
                elif response.status_code == 401:
                    # Unauthorized
                    print("OpenRouter API key invalid or expired")
                    raise AuthenticationError("Invalid API key. Please check your OpenRouter configuration.")
                elif response.status_code == 400:
                    # Bad request
                    error_data = response.json() if response.text else {}
                    error_message = error_data.get("error", {}).get("message", "Bad request")
                    print(f"OpenRouter bad request: {error_message}")
                    raise APIError(f"Bad request: {error_message}")
                else:
                    # Other errors
                    print(f"OpenRouter API error: {response.status_code} - {response.text}")
                    raise APIError(f"OpenRouter API error: {response.status_code} - {response.text}")
                    
        except httpx.TimeoutException:
            print("OpenRouter API request timed out")
            raise APIError("Request timed out. Please try again.")
        except httpx.RequestError as e:
            print(f"OpenRouter network error: {e}")
            raise APIError(f"Network error: {str(e)}")
        except (RateLimitError, AuthenticationError, APIError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            print(f"Unexpected error in OpenRouter chat completion: {e}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    async def translate_text(self, text: str, target_lang: str) -> str:
        """Translate given text to target_lang using the chat model."""
        try:
            system_prompt = (
                "You are a translation engine. Translate the user's text to the specified language. "
                "Only return the translated text, no explanations. Preserve meaning and tone."
            )
            user_prompt = f"Target language: {target_lang}\n\nText to translate:\n{text}"

            response = await self.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=min(max(64, len(text) // 2), settings.MAX_TOKENS),
                temperature=0.3,
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate multilingual embedding using sentence-transformers"""
        try:
            logger.info(f"Generating multilingual embedding via OpenRouter service for text: {text[:100]}...")
            embedding = await multilingual_embedding_service.generate_embedding(text)
            logger.info(f"Generated embedding with dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating multilingual embedding: {e}")
            # Fallback to zero vector
            dimension = multilingual_embedding_service.get_embedding_dimension()
            return [0.0] * dimension

# Global instance
openrouter_service = OpenRouterService()
