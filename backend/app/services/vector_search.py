import numpy as np
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.database import get_collection
from app.models.database import CourseContent, VectorSearchResult, Citation
from app.services.openrouter_service import openrouter_service
from app.services.embedding_service import multilingual_embedding_service
import time
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorSearchService:
    def __init__(self):
        self.openrouter_service = openrouter_service
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_collection()
        return self._collection
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate multilingual embedding using sentence-transformers"""
        try:
            logger.info(f"Generating multilingual embedding for text: {text[:100]}...")
            embedding = await multilingual_embedding_service.generate_embedding(text)
            logger.info(f"Generated embedding with dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating multilingual embedding: {e}")
            # Fallback to zero vector
            dimension = multilingual_embedding_service.get_embedding_dimension()
            return [0.0] * dimension
    
    async def add_course_content(self, content_data: Dict[str, Any]) -> str:
        """Add course content with embedding to MongoDB"""
        try:
            # Generate embedding for the content
            text_for_embedding = f"{content_data['title']} {content_data['content']}"
            embedding = await self.generate_embedding(text_for_embedding)
            
            # Create course content document
            course_content = CourseContent(
                title=content_data['title'],
                content=content_data['content'],
                course_id=content_data['course_id'],
                section_id=content_data.get('section_id'),
                page_number=content_data.get('page_number'),
                embedding=embedding,
                metadata=content_data.get('metadata', {})
            )
            
            # Insert into MongoDB
            result = await self.collection.insert_one(course_content.dict(by_alias=True))
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error adding course content: {e}")
            raise e
    
    async def search_similar_content(
        self, 
        query: str, 
        top_k: int = 5, 
        course_id: Optional[str] = None,
        min_score: float = 0.7
    ) -> List[VectorSearchResult]:
        """Search for similar content using MongoDB Atlas Vector Search"""
        try:
            # Generate embedding for the query
            query_embedding = await self.generate_embedding(query)
            
            # Build aggregation pipeline for vector search
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": settings.MONGODB_VECTOR_INDEX,
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": top_k * 2,  # Get more candidates for filtering
                        "limit": top_k
                    }
                }
            ]
            
            # Add course filter if specified
            if course_id:
                pipeline.append({
                    "$match": {
                        "course_id": course_id
                    }
                })
            
            # Add score calculation
            pipeline.extend([
                {
                    "$addFields": {
                        "score": {
                            "$meta": "vectorSearchScore"
                        }
                    }
                },
                {
                    "$match": {
                        "score": {"$gte": min_score}
                    }
                }
            ])
            
            # Execute search
            cursor = self.collection.aggregate(pipeline)
            results = []
            
            async for doc in cursor:
                # Convert MongoDB document to CourseContent
                course_content = CourseContent(**doc)
                
                # Calculate distance (1 - score for cosine similarity)
                distance = 1 - doc.get('score', 0)
                
                results.append(VectorSearchResult(
                    content=course_content,
                    score=doc.get('score', 0),
                    distance=distance
                ))
            
            return results
            
        except Exception as e:
            print(f"Error in vector search: {e}")
            # Fallback to text search if vector search fails
            return await self.fallback_text_search(query, top_k, course_id)
    
    async def fallback_text_search(
        self, 
        query: str, 
        top_k: int = 5, 
        course_id: Optional[str] = None
    ) -> List[VectorSearchResult]:
        """Fallback text search using MongoDB text index"""
        try:
            # Create text index if it doesn't exist
            await self.collection.create_index([("title", "text"), ("content", "text")])
            
            # Build search query
            search_query = {
                "$text": {"$search": query}
            }
            
            if course_id:
                search_query["course_id"] = course_id
            
            # Execute text search with textScore
            cursor = self.collection.find(search_query, {
                "score": {"$meta": "textScore"},
                "title": 1,
                "content": 1,
                "course_id": 1,
                "section_id": 1,
                "page_number": 1,
                "embedding": 1,
                "metadata": 1
            }).sort([("score", {"$meta": "textScore"})]).limit(top_k)
            results = []
            
            async for doc in cursor:
                course_content = CourseContent(**doc)
                # Use text score as similarity score
                raw = float(doc.get('score', 0.0) or 0.0)
                # Normalize textScore (unbounded) into 0..1 using logistic-like mapping
                text_score = 1.0 - (1.0 / (1.0 + raw)) if raw > 0 else 0.0
                
                results.append(VectorSearchResult(
                    content=course_content,
                    score=text_score,
                    distance=1 - text_score
                ))
            
            return results
            
        except Exception as e:
            print(f"Error in fallback text search: {e}")
            return []
    
    async def get_citations_from_results(
        self, 
        search_results: List[VectorSearchResult], 
        query: str
    ) -> List[Citation]:
        """Convert search results to citations"""
        citations = []
        
        for i, result in enumerate(search_results):
            # Extract relevant span from content
            content = result.content.content
            title = result.content.title
            
            # Simple span extraction (you can improve this with more sophisticated logic)
            words = query.lower().split()
            content_lower = content.lower()
            
            # Find the best matching span
            best_span = content[:200] + "..." if len(content) > 200 else content
            
            # Find the position of query words in content
            for word in words:
                if word in content_lower:
                    start_pos = content_lower.find(word)
                    if start_pos != -1:
                        # Extract context around the match
                        start = max(0, start_pos - 50)
                        end = min(len(content), start_pos + len(word) + 50)
                        best_span = content[start:end]
                        if start > 0:
                            best_span = "..." + best_span
                        if end < len(content):
                            best_span = best_span + "..."
                        break
            
            citation = Citation(
                source_id=str(result.content.id),
                title=title,
                content=best_span,
                confidence=result.score,
                page_number=result.content.page_number,
                course_id=result.content.course_id
            )
            citations.append(citation)
        
        return citations
    
    async def search_and_generate_answer(
        self, 
        query: str, 
        top_k: int = 5, 
        course_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for relevant content and generate answer using OpenAI"""
        start_time = time.time()
        
        try:
            # Search for relevant content
            search_results = await self.search_similar_content(
                query=query,
                top_k=top_k,
                course_id=course_id
            )
            
            if not search_results:
                return {
                    "answer": "I couldn't find relevant information to answer your question. Please try rephrasing or check if the course content is available.",
                    "citations": [],
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    "latency_ms": (time.time() - start_time) * 1000,
                    "answer_id": str(uuid.uuid4())
                }
            
            # Prepare context for OpenAI
            context_parts = []
            for result in search_results:
                context_parts.append(f"Title: {result.content.title}\nContent: {result.content.content}")
            
            context = "\n\n".join(context_parts)
            
            # Generate answer using OpenAI
            system_prompt = """You are a helpful course assistant. Answer the user's question based on the provided course content.
            Requirements:
            - Use only the provided content; if insufficient, say so clearly.
            - Be accurate and concise; cite specific content when relevant.
            - IMPORTANT: Reply in the SAME LANGUAGE as the user's question (e.g., Hindi → Hindi, English → English)."""
            
            from app.utils.lang import detect_language_code, language_name
            user_lang = detect_language_code(query)
            lang_name = language_name(user_lang)
            user_prompt = f"""Based on the following course content, answer in {lang_name}. Question: {query}

Course Content:
{context}"""
            
            response = await self.openrouter_service.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # Generate citations
            citations = await self.get_citations_from_results(search_results, query)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "answer": answer,
                "citations": [citation.dict() for citation in citations],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "latency_ms": latency_ms,
                "answer_id": str(uuid.uuid4())
            }
            
        except Exception as e:
            print(f"Error in search and generate answer: {e}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "citations": [],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "latency_ms": (time.time() - start_time) * 1000,
                "answer_id": str(uuid.uuid4())
            }

# Global instance
vector_search_service = VectorSearchService()
