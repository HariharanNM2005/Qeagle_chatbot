"""
Simple Chat Endpoints
Direct chat functionality without vector search
"""

from fastapi import APIRouter, HTTPException
from app.services.openrouter_service import openrouter_service, RateLimitError, AuthenticationError, APIError
from app.core.config import settings
import time
import uuid

# Initialize router
router = APIRouter()

@router.post("/chat")
async def simple_chat(request: dict):
    """Simple chat endpoint using OpenRouter Llama model"""
    try:
        query = request.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        start_time = time.time()
        
        # Use OpenRouter for chat completion
        try:
            response = await openrouter_service.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a helpful course assistant. Answer questions clearly and provide examples when helpful. IMPORTANT: Always reply in the SAME LANGUAGE as the user's message (e.g., Hindi → Hindi, Tamil → Tamil, English → English)."},
                    {"role": "user", "content": query}
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=0.7
            )
            
            answer = response['choices'][0]['message']['content']
            usage = response.get('usage', {})
            
        except RateLimitError as e:
            # Handle rate limit gracefully
            answer = f"I'm sorry, but I've reached my daily limit for free AI responses. {str(e)}. Please try again tomorrow or consider upgrading your API plan."
            usage = {}
            print(f"Rate limit error handled gracefully: {e}")
            
        except AuthenticationError as e:
            # Handle authentication errors
            answer = f"Authentication error: {str(e)}. Please check the API configuration."
            usage = {}
            print(f"Authentication error: {e}")
            
        except APIError as e:
            # Handle other API errors
            answer = f"I'm experiencing technical difficulties: {str(e)}. Please try again later."
            usage = {}
            print(f"API error: {e}")
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "answer": answer,
            "model": settings.OPENROUTER_MODEL,
            "usage": {
                "prompt_tokens": usage.get('prompt_tokens', 0),
                "completion_tokens": usage.get('completion_tokens', 0),
                "total_tokens": usage.get('total_tokens', 0)
            },
            "latency_ms": latency_ms,
            "answer_id": str(uuid.uuid4()),
            "cost": "$0.00 (FREE with Llama 3.3 70B)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

@router.post("/translate")
async def translate_text(request: dict):
    """Translate text to target language using LLM"""
    try:
        text = request.get("text", "")
        target_lang = request.get("target_lang", "en")
        if not text:
            raise HTTPException(status_code=400, detail="text is required")
        translated = await openrouter_service.translate_text(text, target_lang)
        return {"translated": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating text: {str(e)}")

@router.get("/models")
async def get_available_models():
    """Get information about available models"""
    return {
        "chat_model": settings.OPENROUTER_MODEL,
        "embedding_model": settings.OPENROUTER_EMBEDDING_MODEL,
        "provider": "OpenRouter",
        "cost": "FREE (Llama 3.3 70B)",
        "features": [
            "Free chat completions",
            "Course Q&A support",
            "Programming help",
            "Technical explanations"
        ]
    }

@router.get("/status")
async def get_chat_status():
    """Get chat service status"""
    try:
        # Test the connection
        response = await openrouter_service.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        return {
            "status": "healthy",
            "model": settings.OPENROUTER_MODEL,
            "provider": "OpenRouter",
            "connection": "active"
        }
    except RateLimitError as e:
        return {
            "status": "rate_limited",
            "model": settings.OPENROUTER_MODEL,
            "provider": "OpenRouter",
            "connection": "rate_limited",
            "error": "Daily rate limit exceeded",
            "message": "Please try again tomorrow or upgrade your plan"
        }
    except AuthenticationError as e:
        return {
            "status": "auth_error",
            "model": settings.OPENROUTER_MODEL,
            "provider": "OpenRouter",
            "connection": "auth_failed",
            "error": "Authentication failed",
            "message": "Please check your API key configuration"
        }
    except APIError as e:
        return {
            "status": "api_error",
            "model": settings.OPENROUTER_MODEL,
            "provider": "OpenRouter",
            "connection": "api_error",
            "error": str(e),
            "message": "API service temporarily unavailable"
        }
    except Exception as e:
        return {
            "status": "error",
            "model": settings.OPENROUTER_MODEL,
            "provider": "OpenRouter",
            "connection": "failed",
            "error": str(e),
            "message": "Unexpected error occurred"
        }

