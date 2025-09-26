from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class CourseContent(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    content: str
    course_id: str
    section_id: Optional[str] = None
    page_number: Optional[int] = None
    embedding: List[float] = Field(..., description="Vector embedding for semantic search")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class QueryRequest(BaseModel):
    query: str
    lang: Optional[str] = "en"
    top_k: Optional[int] = 5
    course_id: Optional[str] = None

class Citation(BaseModel):
    source_id: str
    title: str
    content: str
    confidence: float
    page_number: Optional[int] = None
    course_id: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    usage: Dict[str, Any]
    latency_ms: float
    answer_id: str

class FeedbackRequest(BaseModel):
    query: str
    answer_id: str
    label: str
    note: Optional[str] = None

class VectorSearchResult(BaseModel):
    content: CourseContent
    score: float
    distance: float

class DocumentUpload(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    document_id: str
    filename: str
    file_size: int
    file_hash: str
    total_pages: int
    extracted_pages: int
    total_characters: int
    uploaded_at: datetime
    status: str
    user_id: Optional[str] = None

class DocumentChunk(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    document_id: str
    chunk_id: int
    text: str
    start_pos: int
    end_pos: int
    char_count: int
    embedding: List[float] = Field(..., description="Vector embedding for semantic search")
    page_number: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentUploadRequest(BaseModel):
    filename: str
    user_id: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
    chunks_created: int
    processing_time_ms: float