"""
Cache Service for RAG System
Implements in-memory caching to reduce latency
"""

import time
import hashlib
import json
from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """In-memory cache service for RAG responses"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = settings.CACHE_TTL
        self.enabled = settings.ENABLE_CACHING
        
    def _generate_cache_key(self, query: str, document_id: str, top_k: int) -> str:
        """Generate a unique cache key for the query"""
        cache_data = {
            "query": query.lower().strip(),
            "document_id": document_id,
            "top_k": top_k
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        if not cache_entry:
            return True
        
        timestamp = cache_entry.get("timestamp", 0)
        return (time.time() - timestamp) > self.cache_ttl
    
    def get_search_results(self, query: str, document_id: str, top_k: int) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results"""
        if not self.enabled:
            return None
        
        cache_key = self._generate_cache_key(query, document_id, top_k)
        cache_entry = self.cache.get(cache_key)
        
        if cache_entry and not self._is_expired(cache_entry):
            logger.info(f"Cache hit for search query: {query[:50]}...")
            return cache_entry.get("results")
        
        # Remove expired entry
        if cache_entry:
            del self.cache[cache_key]
        
        return None
    
    def set_search_results(self, query: str, document_id: str, top_k: int, results: List[Dict[str, Any]]):
        """Cache search results"""
        if not self.enabled:
            return
        
        cache_key = self._generate_cache_key(query, document_id, top_k)
        self.cache[cache_key] = {
            "results": results,
            "timestamp": time.time(),
            "query": query,
            "document_id": document_id,
            "top_k": top_k
        }
        logger.info(f"Cached search results for query: {query[:50]}...")
    
    def get_chat_response(self, query: str, document_id: str, top_k: int) -> Optional[Dict[str, Any]]:
        """Get cached chat response"""
        if not self.enabled:
            return None
        
        cache_key = self._generate_cache_key(query, document_id, top_k)
        cache_entry = self.cache.get(cache_key)
        
        if cache_entry and not self._is_expired(cache_entry):
            logger.info(f"Cache hit for chat query: {query[:50]}...")
            return cache_entry.get("chat_response")
        
        # Remove expired entry
        if cache_entry:
            del self.cache[cache_key]
        
        return None
    
    def set_chat_response(self, query: str, document_id: str, top_k: int, response: Dict[str, Any]):
        """Cache chat response"""
        if not self.enabled:
            return
        
        cache_key = self._generate_cache_key(query, document_id, top_k)
        self.cache[cache_key] = {
            "chat_response": response,
            "timestamp": time.time(),
            "query": query,
            "document_id": document_id,
            "top_k": top_k
        }
        logger.info(f"Cached chat response for query: {query[:50]}...")
    
    def clear_cache(self):
        """Clear all cached entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if self._is_expired(entry))
        active_entries = total_entries - expired_entries
        
        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "cache_size_mb": len(json.dumps(self.cache)) / (1024 * 1024),
            "enabled": self.enabled,
            "ttl_seconds": self.cache_ttl
        }
    
    def cleanup_expired(self):
        """Remove expired entries from cache"""
        expired_keys = []
        for key, entry in self.cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

# Global cache instance
cache_service = CacheService()
