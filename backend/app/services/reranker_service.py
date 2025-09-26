"""
Cross-Encoder reranking service for hybrid retrieval
"""

import asyncio
from typing import List, Tuple
from sentence_transformers import CrossEncoder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RerankerService:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model: CrossEncoder | None = None

    async def _load(self):
        if self.model is None:
            logger.info(f"Loading cross-encoder reranker: {self.model_name}")
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(None, lambda: CrossEncoder(self.model_name))
            logger.info("Reranker loaded")

    async def rerank(self, query: str, passages: List[str]) -> List[int]:
        """Return indices of passages sorted by relevance descending"""
        if not passages:
            return []
        await self._load()
        loop = asyncio.get_event_loop()
        pairs: List[Tuple[str, str]] = [(query, p) for p in passages]
        scores = await loop.run_in_executor(None, lambda: self.model.predict(pairs))
        # sort indices by score desc
        indices = list(range(len(passages)))
        indices.sort(key=lambda i: float(scores[i]), reverse=True)
        return indices


reranker_service = RerankerService()


