from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
from app.models.database import DocumentUploadResponse
from app.services.document_service import document_service
import time

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: Optional[str] = Query(None, description="Optional user ID")
):
    """Upload a PDF document for processing"""
    try:
        result = await document_service.upload_document(file, user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.get("/list")
async def get_documents(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """Get list of uploaded documents"""
    try:
        documents = await document_service.get_document_list(user_id)
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")

@router.get("/search")
async def search_documents(
    query: str = Query(..., description="Search query"),
    document_id: Optional[str] = Query(None, description="Filter by specific document"),
    top_k: int = Query(5, description="Number of results to return")
):
    """Search through uploaded documents"""
    try:
        results = await document_service.search_documents(query, document_id, top_k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and all its chunks"""
    try:
        success = await document_service.delete_document(document_id)
        if success:
            return {"message": "Document deleted successfully", "document_id": document_id}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.get("/{document_id}/info")
async def get_document_info(document_id: str):
    """Get information about a specific document"""
    try:
        documents = await document_service.get_document_list()
        document = next((doc for doc in documents if doc["document_id"] == document_id), None)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document info: {str(e)}")
