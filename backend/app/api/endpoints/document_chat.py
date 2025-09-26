from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.database import QueryRequest, QueryResponse
from app.services.query_utils import normalize_query
from app.services.document_service import document_service
from app.services.openrouter_service import openrouter_service, RateLimitError, AuthenticationError, APIError
from app.core.config import settings
import time
import uuid

router = APIRouter()

@router.post("/chat", response_model=QueryResponse)
async def document_chat_answer(request: QueryRequest):
    """Answer questions based on uploaded documents"""
    start_time = time.time()
    
    try:
        print(f"DEBUG: Document chat - Original Query: '{request.query}'")
        print(f"DEBUG: Document chat - Document ID: '{request.course_id}'")
        
        # Preprocess query to make it more direct
        original_query = request.query
        request.query = normalize_query(request.query)
        query_lower = request.query.lower()
        
        # Convert common question patterns to more direct queries
        if "what is the" in query_lower and "score" in query_lower:
            if "aws" in query_lower:
                request.query = "AWS score"
            elif "cgpa" in query_lower:
                request.query = "CGPA"
            elif "leetcode" in query_lower:
                request.query = "Leetcode rating"
        elif "what is" in query_lower and "certificate" in query_lower:
            request.query = "certificates"
        elif "what is" in query_lower and "linkedin" in query_lower:
            request.query = "LinkedIn"
        elif "what is" in query_lower and "project" in query_lower:
            request.query = "projects"
        
        print(f"DEBUG: Original query: '{original_query}' -> Processed query: '{request.query}'")
        
        # Search for relevant document chunks using the processed query
        search_results = await document_service.search_documents(
            query=request.query,
            document_id=request.course_id,  # Using course_id as document_id filter
            top_k=request.top_k or 5
        )
        
        print(f"DEBUG: Document chat - Found {len(search_results)} results")
        if search_results:
            print(f"DEBUG: First result text preview: {search_results[0].get('text', '')[:100]}...")
        
        # Initialize variables
        answer = ""
        response = None
        
        # STRICT RAG MODE: Only answer if relevant document content is found
        if not search_results:
            # No relevant content found - return immediately without using LLM
            answer = f"I couldn't find any relevant information about '{request.query}' in the uploaded documents. Please try asking a different question or check if the relevant document has been uploaded correctly."
            response = None  # No LLM response needed
            print(f"RAG: No relevant context found for query: '{request.query}'")
        else:
            # Always use top-k; BM25 and vector scores are on different scales, so avoid strict thresholds
            relevant_results = search_results[: (request.top_k or 5)]
            
            # Lightweight intent-based rerank to improve precision
            ql = (request.query or "").lower()
            def _bonus(r):
                t = (r.get("text") or "").lower()
                b = 0.0
                if "project" in ql:
                    if "project" in t:
                        b += 0.2
                    if "internship" in t:
                        b -= 0.1
                if "internship" in ql:
                    if "internship" in t:
                        b += 0.2
                    if "project" in t:
                        b -= 0.1
                return b
            relevant_results = sorted(relevant_results, key=lambda r: (r.get("score", 0.0) + _bonus(r)), reverse=True)
            print(f"RAG: Using {len(relevant_results)} results for answer generation")

            # Check if the query is asking for general knowledge not in documents
            general_knowledge_indicators = [
                "what is", "define", "explain", "how to cook", "capital of", 
                "general knowledge", "common knowledge", "everyone knows"
            ]
            
            query_lower = request.query.lower()
            is_general_knowledge_query = any(indicator in query_lower for indicator in general_knowledge_indicators)
            
            if is_general_knowledge_query:
                # This looks like a general knowledge question - check if documents actually contain relevant info
                document_content = " ".join([r.get("text", "") for r in relevant_results]).lower()
                if not any(word in document_content for word in request.query.lower().split()):
                    answer = f"I couldn't find specific information about '{request.query}' in the uploaded documents. This appears to be a general knowledge question, but I can only answer based on the content in your uploaded documents."
                    response = None
                    print(f"RAG: General knowledge query detected, no relevant document content found")
                else:
                    # Document does contain relevant info, proceed with LLM
                    pass
            else:
                # Not a general knowledge query, proceed with LLM
                pass
            
            if response is None:  # If we haven't set a response yet, proceed with LLM
                # Build context from relevant document search results with length limiting
                context_parts = []
                total_length = 0
                
                for i, result in enumerate(relevant_results, 1):
                    filename = result.get("filename", "Unknown Document")
                    page_number = result.get("page_number", "Unknown Page")
                    text = result.get("text", "")
                    score = result.get("score", 0.0)
                    
                    source_text = f"Source {i} (from {filename}, page {page_number}, relevance: {score:.2f}):\n{text}"
                    
                    # Check if adding this source would exceed the context limit
                    if total_length + len(source_text) > settings.RAG_MAX_CONTEXT_LENGTH:
                        print(f"RAG: Context length limit reached ({settings.RAG_MAX_CONTEXT_LENGTH} chars), using {i-1} sources")
                        break
                    
                    context_parts.append(source_text)
                    total_length += len(source_text)
                
                context = "\n\n".join(context_parts)
                
                # STRICT system prompt - only use provided context
                system_prompt = """You are a helpful document assistant. Answer questions based on the provided document content.
                
                Instructions:
                - Use only information from the provided document content
                - Extract and provide specific numbers, scores, ratings, and values when asked
                - Be helpful and direct in your responses
                - Look for key terms in the question and find related information in the content
                - If you cannot find the information, say so clearly
                - Don't be overly strict about exact question wording - focus on the intent
                - IMPORTANT: Reply in the SAME LANGUAGE as the user's question (e.g., Hindi → Hindi, English → English)."""
                
                from app.utils.lang import detect_language_code, language_name
                user_lang = detect_language_code(request.query)
                user_prompt = f"""Question (answer in {language_name(user_lang)}): {request.query}
                
                Answer this question using the information from the document content below. Look for specific numbers, scores, and values.
                
                Document Content:
                {context}"""
                
                # Get response from OpenRouter only if we have relevant context
                try:
                    response = await openrouter_service.chat_completion(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_tokens=settings.MAX_TOKENS,
                        temperature=0.1  # Lower temperature for more focused responses
                    )
                    
                    answer = response['choices'][0]['message']['content']
                    print(f"RAG: Generated answer based on {len(relevant_results)} relevant document chunks")
                    
                except RateLimitError as e:
                    # Handle rate limit gracefully
                    answer = f"I'm sorry, but I've reached my daily limit for free AI responses. {str(e)}. Please try again tomorrow or consider upgrading your API plan."
                    response = None
                    print(f"Rate limit error handled gracefully: {e}")
                    
                except AuthenticationError as e:
                    # Handle authentication errors
                    answer = f"Authentication error: {str(e)}. Please check the API configuration."
                    response = None
                    print(f"Authentication error: {e}")
                    
                except APIError as e:
                    # Handle other API errors
                    answer = f"I'm experiencing technical difficulties: {str(e)}. Please try again later."
                    response = None
                    print(f"API error: {e}")
        
        # Create citations from relevant search results only
        citations = []
        if search_results:
            # Use relevant_results if available, otherwise use all search_results
            results_to_cite = relevant_results if 'relevant_results' in locals() and relevant_results else search_results
            for result in results_to_cite:
                citations.append({
                    "source_id": result.get("document_id", "unknown"),
                    "title": result.get("filename", "Unknown Document"),
                    "content": result.get("text", "")[:200] + "..." if len(result.get("text", "")) > 200 else result.get("text", ""),
                    "confidence": result.get("score", 0.0),
                    "page_number": result.get("page_number"),
                    "course_id": result.get("document_id", "unknown")
                })
        
        latency = (time.time() - start_time) * 1000
        
        return QueryResponse(
            answer=answer,
            citations=citations,
            usage=response.get('usage', {}) if response else {},
            latency_ms=latency,
            answer_id=str(uuid.uuid4()),
        )
        
    except Exception as e:
        print(f"Unexpected error in document chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

@router.get("/documents")
async def get_available_documents():
    """Get list of available documents for chat"""
    try:
        documents = await document_service.get_document_list()
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")

@router.get("/search")
async def search_documents_for_chat(
    query: str = Query(..., description="Search query"),
    document_id: Optional[str] = Query(None, description="Filter by specific document"),
    top_k: int = Query(5, description="Number of results to return")
):
    """Search documents and return formatted results for chat"""
    try:
        results = await document_service.search_documents(query, document_id, top_k)
        
        # Format results for chat interface
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result.get("text", ""),
                "filename": result.get("filename", "Unknown Document"),
                "page_number": result.get("page_number"),
                "score": result.get("score", 0.0),
                "document_id": result.get("document_id")
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@router.get("/rag-status")
async def get_rag_status():
    """Get RAG system status and configuration"""
    try:
        return {
            "rag_mode": "strict",
            "relevance_threshold": settings.RAG_RELEVANCE_THRESHOLD,
            "max_context_length": settings.RAG_MAX_CONTEXT_LENGTH,
            "strict_mode": settings.RAG_STRICT_MODE,
            "description": "RAG system configured to only answer based on uploaded document content",
            "behavior": {
                "no_context": "Returns 'no relevant information found' message",
                "low_relevance": "Returns 'insufficient relevant information' message", 
                "sufficient_context": "Uses LLM to generate answer from document content only"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting RAG status: {str(e)}")
