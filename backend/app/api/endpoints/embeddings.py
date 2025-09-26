"""
Embedding API endpoints for testing multilingual embeddings
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.embedding_service import multilingual_embedding_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

class EmbeddingRequest(BaseModel):
    text: str
    language: str = "auto"  # Language hint (optional)

class EmbeddingResponse(BaseModel):
    text: str
    embedding: List[float]
    dimension: int
    model_info: Dict[str, Any]

class BatchEmbeddingRequest(BaseModel):
    texts: List[str]
    language: str = "auto"

class BatchEmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    dimension: int
    model_info: Dict[str, Any]

@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """Generate multilingual embedding for a single text"""
    try:
        logger.info(f"Generating embedding for text: {request.text[:100]}...")
        
        # Generate embedding
        embedding = await multilingual_embedding_service.generate_embedding(request.text)
        
        # Get model info
        model_info = multilingual_embedding_service.get_model_info()
        
        return EmbeddingResponse(
            text=request.text,
            embedding=embedding,
            dimension=len(embedding),
            model_info=model_info
        )
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

@router.post("/generate-batch", response_model=BatchEmbeddingResponse)
async def generate_embeddings_batch(request: BatchEmbeddingRequest):
    """Generate multilingual embeddings for multiple texts"""
    try:
        logger.info(f"Generating batch embeddings for {len(request.texts)} texts")
        
        # Generate embeddings
        embeddings = await multilingual_embedding_service.generate_embeddings_batch(request.texts)
        
        # Get model info
        model_info = multilingual_embedding_service.get_model_info()
        
        return BatchEmbeddingResponse(
            embeddings=embeddings,
            dimension=len(embeddings[0]) if embeddings else 0,
            model_info=model_info
        )
        
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating batch embeddings: {str(e)}")

@router.get("/model-info")
async def get_model_info():
    """Get information about the current embedding model"""
    try:
        model_info = multilingual_embedding_service.get_model_info()
        return model_info
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

@router.get("/test-multilingual")
async def test_multilingual_embeddings():
    """Test multilingual embeddings with sample texts in different languages"""
    try:
        # Sample texts in different languages
        test_texts = [
            "Hello, how are you?",  # English
            "Hola, ¿cómo estás?",  # Spanish
            "Bonjour, comment allez-vous?",  # French
            "Hallo, wie geht es dir?",  # German
            "Ciao, come stai?",  # Italian
            "Olá, como você está?",  # Portuguese
            "Привет, как дела?",  # Russian
            "你好，你好吗？",  # Chinese
            "こんにちは、元気ですか？",  # Japanese
            "안녕하세요, 어떻게 지내세요?",  # Korean
            "مرحبا، كيف حالك؟",  # Arabic
            "नमस्ते, आप कैसे हैं?",  # Hindi
        ]
        
        # Generate embeddings
        embeddings = await multilingual_embedding_service.generate_embeddings_batch(test_texts)
        
        # Calculate similarity between English and other languages
        import numpy as np
        
        english_embedding = np.array(embeddings[0])
        similarities = []
        
        for i, text in enumerate(test_texts[1:], 1):
            other_embedding = np.array(embeddings[i])
            # Calculate cosine similarity
            similarity = np.dot(english_embedding, other_embedding) / (
                np.linalg.norm(english_embedding) * np.linalg.norm(other_embedding)
            )
            similarities.append({
                "text": text,
                "similarity": float(similarity),
                "language": ["Spanish", "French", "German", "Italian", "Portuguese", 
                           "Russian", "Chinese", "Japanese", "Korean", "Arabic", "Hindi"][i-1]
            })
        
        return {
            "model_info": multilingual_embedding_service.get_model_info(),
            "test_results": {
                "total_texts": len(test_texts),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                "similarities": similarities
            },
            "message": "Multilingual embedding test completed successfully!"
        }
        
    except Exception as e:
        logger.error(f"Error testing multilingual embeddings: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing multilingual embeddings: {str(e)}")
