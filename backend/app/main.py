from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.endpoints import chat, simple_chat, documents, document_chat, embeddings
from app.core.config import settings
from app.database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    description="Course Q&A Chatbot with MongoDB Atlas Vector Search",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (modules export routers directly via endpoints.__init__)
app.include_router(chat, prefix="/api/v1", tags=["chat"]) 
app.include_router(simple_chat, prefix="/api/v1/simple-chat", tags=["simple-chat"]) 
app.include_router(documents, prefix="/api/v1/documents", tags=["documents"]) 
app.include_router(document_chat, prefix="/api/v1/document-chat", tags=["document-chat"]) 
app.include_router(embeddings, prefix="/api/v1/embeddings", tags=["embeddings"]) 

@app.get("/")
async def root():
    return {
        "message": "Course Q&A Chatbot API with MongoDB Atlas Vector Search", 
        "status": "running",
        "features": [
            "MongoDB Atlas Vector Search",
            "OpenRouter LLM Integration",
            "PDF Document Upload",
            "Semantic Search",
            "Citation Support",
            "Multilingual Embeddings (LaBSE)",
            "Language-Agnostic Search"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)