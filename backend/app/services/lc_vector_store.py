from typing import Any, Dict, List, Optional
from app.core.config import settings

from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
try:
    # Preferred modern import
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
    # Fallback for environments without langchain-huggingface installed yet
    from langchain_community.embeddings import HuggingFaceEmbeddings

# Local fallback: direct SentenceTransformer usage with dimension normalization
try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


class LocalSentenceTransformerEmbeddings:
    """
    Minimal adapter to match LangChain Embeddings interface using SentenceTransformer.
    Ensures output vectors exactly match settings.EMBEDDING_DIMENSION via pad/truncate.
    """

    def __init__(self, model_name: str):
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers is not installed")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        # Auto-detect dimension from model output once, fallback to configured dimension
        try:
            probe = self.model.encode("test", convert_to_tensor=False)
            dim = len(probe.tolist() if hasattr(probe, "tolist") else list(probe))
            self.target_dim = dim or settings.EMBEDDING_DIMENSION
        except Exception:
            self.target_dim = settings.EMBEDDING_DIMENSION

    def _normalize_dim(self, vec: List[float]) -> List[float]:
        if len(vec) == self.target_dim:
            return vec
        if len(vec) < self.target_dim:
            return vec + [0.0] * (self.target_dim - len(vec))
        return vec[: self.target_dim]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        inputs = [t if t is not None else "" for t in texts]
        embeddings = self.model.encode(inputs, convert_to_tensor=False)
        return [self._normalize_dim(e.tolist() if hasattr(e, "tolist") else list(e)) for e in embeddings]

    def embed_query(self, text: str) -> List[float]:
        vec = self.model.encode(text or "", convert_to_tensor=False)
        vec_list = vec.tolist() if hasattr(vec, "tolist") else list(vec)
        return self._normalize_dim(vec_list)


class LangChainVectorStoreService:
    def __init__(self):
        self._pymongo_client: Optional[MongoClient] = None
        self._collection = None
        self._vector_store: Optional[MongoDBAtlasVectorSearch] = None
        self._embeddings = None

    def _get_sync_collection(self):
        if self._pymongo_client is None:
            self._pymongo_client = MongoClient(settings.MONGODB_URL)
        if self._collection is None:
            db = self._pymongo_client[settings.MONGODB_DATABASE]
            self._collection = db[settings.MONGODB_COLLECTION]
        return self._collection

    def _get_embeddings(self):
        if self._embeddings is None:
            # Try LangChain's HuggingFaceEmbeddings first with configured model
            try:
                self._embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
            except Exception:
                # Try local SentenceTransformer with configured model
                try:
                    self._embeddings = LocalSentenceTransformerEmbeddings(model_name=settings.EMBEDDING_MODEL)
                except Exception:
                    # Final fallback to lightweight local model all-MiniLM-L6-v2
                    self._embeddings = LocalSentenceTransformerEmbeddings(model_name=settings.EMBEDDING_MODEL_FALLBACK)
        return self._embeddings

    def get_vector_store(self) -> MongoDBAtlasVectorSearch:
        if self._vector_store is None:
            self._vector_store = MongoDBAtlasVectorSearch(
                collection=self._get_sync_collection(),
                embedding=self._get_embeddings(),
                index_name=settings.MONGODB_VECTOR_INDEX,
                relevance_score_fn="cosine",
                text_key="text",
            )
        return self._vector_store

    async def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        vs = self.get_vector_store()
        ids = vs.add_texts(texts=texts, metadatas=metadatas or [])
        return ids

    def similarity_search(self, query: str, k: int = 5, metadata_filter: Optional[Dict[str, Any]] = None, **kwargs):
        # Tolerate legacy callers that pass filter=...
        if "filter" in kwargs and metadata_filter is None:
            metadata_filter = kwargs.pop("filter")
        vs = self.get_vector_store()
        search_kwargs: Dict[str, Any] = {"k": k}
        if metadata_filter:
            search_kwargs["filter"] = metadata_filter
        retriever = vs.as_retriever(search_kwargs=search_kwargs)
        # LangChain retriever returns Documents
        docs = retriever.invoke(query)
        return docs

    def similarity_search_with_similarity(self, query: str, k: int = 5, metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform similarity search and return list of dicts: { doc, similarity }
        - Uses similarity_search_with_score when available (distance -> similarity conversion)
        - Falls back to retriever rank-based similarity if scores not available
        """
        vs = self.get_vector_store()
        # Try to use vector store native scoring
        try:
            # LangChain API returns List[Tuple[Document, score]]
            results = vs.similarity_search_with_score(query, k=k, filter=metadata_filter)  # type: ignore[arg-type]
            normalized: List[Dict[str, Any]] = []
            for doc, score in results:
                # Heuristic: if score in [0,1], treat as similarity; else treat as distance
                if isinstance(score, (int, float)):
                    if 0.0 <= float(score) <= 1.0:
                        sim = float(score)
                    else:
                        # Convert distance to similarity in (0,1]
                        sim = 1.0 / (1.0 + float(score))
                else:
                    sim = 0.0
                # clamp
                if sim < 0.0:
                    sim = 0.0
                if sim > 1.0:
                    sim = 1.0
                normalized.append({"doc": doc, "similarity": sim})
            if normalized:
                return normalized
        except Exception:
            pass

        # Fallback: use retriever rank to synthesize similarity
        docs = self.similarity_search(query=query, k=k, metadata_filter=metadata_filter)
        total = max(1, len(docs))
        ranked: List[Dict[str, Any]] = []
        for idx, doc in enumerate(docs):
            sim = 1.0 - (idx / total)
            ranked.append({"doc": doc, "similarity": sim})
        return ranked


lc_vector_store_service = LangChainVectorStoreService()


