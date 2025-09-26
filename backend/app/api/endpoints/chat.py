from fastapi import APIRouter, HTTPException
import time
import uuid

from app.models.database import QueryRequest, QueryResponse, FeedbackRequest, CourseContent
from app.core.config import settings
from app.services.vector_search import vector_search_service
from app.database import get_collection

# Initialize router
router = APIRouter()


@router.post("/answer", response_model=QueryResponse)
async def answer_question(request: QueryRequest):
    """Answer a question using MongoDB Atlas Vector Search and OpenAI"""
    try:
        # Use vector search service to find relevant content and generate answer
        result = await vector_search_service.search_and_generate_answer(
            query=request.query,
            top_k=request.top_k,
            course_id=request.course_id
        )
        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@router.post("/content", response_model=dict)
async def add_course_content(content_data: dict):
    """Add course content to the database with vector embedding"""
    try:
        # Validate required fields
        required_fields = ['title', 'content', 'course_id']
        for field in required_fields:
            if field not in content_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Add content to database
        content_id = await vector_search_service.add_course_content(content_data)
        
        return {
            "message": "Course content added successfully",
            "content_id": content_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding course content: {str(e)}")


@router.get("/content/{course_id}")
async def get_course_content(course_id: str, limit: int = 10, skip: int = 0):
    """Get course content by course ID"""
    try:
        collection = get_collection()
        
        # Query course content
        cursor = collection.find(
            {"course_id": course_id}
        ).skip(skip).limit(limit).sort("created_at", -1)
        
        content_list = []
        async for doc in cursor:
            # Remove embedding from response to reduce payload size
            doc.pop('embedding', None)
            content_list.append(doc)
        
        return {
            "course_id": course_id,
            "content": content_list,
            "total": len(content_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching course content: {str(e)}")


@router.get("/search")
async def search_content(query: str, course_id: str = None, top_k: int = 5):
    """Search for content using vector search"""
    try:
        results = await vector_search_service.search_similar_content(
            query=query,
            top_k=top_k,
            course_id=course_id
        )
        
        # Convert results to response format
        search_results = []
        for result in results:
            search_results.append({
                "title": result.content.title,
                "content": result.content.content[:200] + "..." if len(result.content.content) > 200 else result.content.content,
                "course_id": result.content.course_id,
                "score": result.score,
                "distance": result.distance
            })
        
        return {
            "query": query,
            "results": search_results,
            "total": len(search_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching content: {str(e)}")


@router.get("/source/{source_id}")
async def get_source(source_id: str):
    """Fetch a source document chunk"""
    return {
        "source_id": source_id,
        "content": f"This is the content for source {source_id}. "
                   f"In a real implementation, this would fetch the actual source from your database.",
        "metadata": {
            "page_number": 1,
            "section": "Introduction",
        },
    }


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback for answer quality"""
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": str(uuid.uuid4()),
    }
