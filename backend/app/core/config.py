from pydantic_settings import BaseSettings
from typing import List, Optional
import json


class Settings(BaseSettings):
    # OpenRouter Configuration
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str

    # App Configuration
    APP_NAME: str
    DEBUG: bool
    HOST: str
    PORT: int
    CORS_ORIGINS: Optional[str] = None
    _CORS_DEFAULT: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # MongoDB Atlas Configuration
    MONGODB_URL: str
    MONGODB_DATABASE: str
    MONGODB_COLLECTION: str
    MONGODB_VECTOR_INDEX: str

    # Vector Search Configuration
    VECTOR_DIMENSION: int
    VECTOR_SEARCH_TOP_K: int

    # Embedding Configuration
    EMBEDDING_MODEL: str
    EMBEDDING_MODEL_FALLBACK: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int

    # Model Configuration
    MAX_TOKENS: int
    SITE_URL: str = "http://localhost:3000"
    SITE_NAME: str = "Course Chatbot"

    # RAG Configuration
    RAG_RELEVANCE_THRESHOLD: float = 0.3
    RAG_STRICT_MODE: bool = True
    RAG_MAX_CONTEXT_LENGTH: int = 4000

    def get_cors_origins(self) -> List[str]:
        value = self.CORS_ORIGINS
        if not value:
            return list(self._CORS_DEFAULT)
        s = value.strip()
        if not s:
            return []
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(i).strip() for i in parsed if str(i).strip()]
            except Exception:
                pass
            inner = s.strip("[]")
            return [i.strip().strip('"') for i in inner.split(",") if i.strip().strip('"')]
        return [i.strip() for i in s.split(",") if i.strip()]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()