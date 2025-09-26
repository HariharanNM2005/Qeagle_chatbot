"""
Multilingual Embedding Service
Uses sentence-transformers for language-agnostic embeddings
"""

import asyncio
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultilingualEmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"):
        """
        Initialize the multilingual embedding service
        
        Args:
            model_name: The sentence-transformers model to use
                       Options:
                       - "sentence-transformers/paraphrase-multilingual-mpnet-base-v2" (768 dims, good balance)
                       - "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" (384 dims, faster)
                       - "sentence-transformers/LaBSE" (768 dims, excellent for 100+ languages)
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.embedding_dimension = self._get_embedding_dimension()
        
    def _get_embedding_dimension(self) -> int:
        """Get the embedding dimension for the selected model"""
        dimension_map = {
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2": 768,
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 384,
            "sentence-transformers/LaBSE": 768,
            "sentence-transformers/distiluse-base-multilingual-cased": 512,
        }
        return dimension_map.get(self.model_name, 768)
    
    async def _load_model(self):
        """Load the sentence transformer model asynchronously"""
        if self.model is None:
            try:
                logger.info(f"Loading multilingual embedding model: {self.model_name}")
                # Run model loading in a thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    None, 
                    lambda: SentenceTransformer(self.model_name)
                )
                logger.info(f"Successfully loaded model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise e
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate multilingual embedding for the given text
        
        Args:
            text: Input text in any language
            
        Returns:
            List of float values representing the embedding vector
        """
        try:
            # Ensure model is loaded
            await self._load_model()
            
            if not text or not text.strip():
                # Return zero vector for empty text
                return [0.0] * self.embedding_dimension
            
            # Clean and prepare text
            text = text.strip()
            
            # Generate embedding in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.model.encode(text, convert_to_tensor=False)
            )
            
            # Convert numpy array to list and ensure it's the right dimension
            embedding_list = embedding.tolist()
            
            # Ensure the embedding has the expected dimension
            if len(embedding_list) != self.embedding_dimension:
                logger.warning(f"Embedding dimension mismatch. Expected {self.embedding_dimension}, got {len(embedding_list)}")
                # Pad or truncate as needed
                if len(embedding_list) < self.embedding_dimension:
                    embedding_list.extend([0.0] * (self.embedding_dimension - len(embedding_list)))
                else:
                    embedding_list = embedding_list[:self.embedding_dimension]
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        try:
            # Ensure model is loaded
            await self._load_model()
            
            if not texts:
                return []
            
            # Clean texts
            cleaned_texts = [text.strip() if text else "" for text in texts]
            
            # Generate embeddings in batch
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(cleaned_texts, convert_to_tensor=False)
            )
            
            # Convert to list format and ensure correct dimensions
            result = []
            for embedding in embeddings:
                embedding_list = embedding.tolist()
                if len(embedding_list) != self.embedding_dimension:
                    if len(embedding_list) < self.embedding_dimension:
                        embedding_list.extend([0.0] * (self.embedding_dimension - len(embedding_list)))
                    else:
                        embedding_list = embedding_list[:self.embedding_dimension]
                result.append(embedding_list)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.embedding_dimension for _ in texts]
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension for this model"""
        return self.embedding_dimension
    
    def get_model_info(self) -> dict:
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "is_loaded": self.model is not None,
            "supported_languages": "100+ languages (multilingual)",
            "model_type": "sentence-transformers"
        }

# Global instance - use configured model from settings
multilingual_embedding_service = MultilingualEmbeddingService(
    model_name=settings.EMBEDDING_MODEL
)
