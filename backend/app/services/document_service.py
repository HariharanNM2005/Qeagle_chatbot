import time
from typing import List, Dict, Any, Optional
from app.database import get_database
from app.models.database import DocumentUpload, DocumentChunk, DocumentUploadResponse
from app.services.pdf_processor import pdf_processor
from app.services.vector_search import vector_search_service
from app.services.lc_vector_store import lc_vector_store_service
from fastapi import UploadFile, HTTPException
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentService:
    def __init__(self):
        self._database = None
        self._documents_collection = None
        self._chunks_collection = None
    
    @property
    def database(self):
        if self._database is None:
            self._database = get_database()
        return self._database
    
    @property
    def documents_collection(self):
        if self._documents_collection is None:
            self._documents_collection = self.database["documents"]
        return self._documents_collection
    
    @property
    def chunks_collection(self):
        if self._chunks_collection is None:
            self._chunks_collection = self.database["document_chunks"]
        return self._chunks_collection
    
    async def upload_document(self, file: UploadFile, user_id: Optional[str] = None) -> DocumentUploadResponse:
        """Upload and process a PDF document"""
        start_time = time.time()
        
        try:
            # Extract text from PDF
            pdf_result = await pdf_processor.extract_text_from_pdf(file)
            
            if not pdf_result["success"]:
                raise HTTPException(status_code=500, detail="Failed to process PDF")
            
            metadata = pdf_result["metadata"]
            full_text = pdf_result["full_text"]
            page_texts = pdf_result["page_texts"]
            
            # Create document record
            document = DocumentUpload(
                document_id=metadata["document_id"],
                filename=metadata["filename"],
                file_size=metadata["file_size"],
                file_hash=metadata["file_hash"],
                total_pages=metadata["total_pages"],
                extracted_pages=metadata["extracted_pages"],
                total_characters=metadata["total_characters"],
                uploaded_at=metadata["uploaded_at"],
                status="processed",
                user_id=user_id
            )
            
            # Save document to database
            print(f"DEBUG: Inserting document: {document.document_id}")
            result = await self.documents_collection.insert_one(document.dict(by_alias=True))
            print(f"DEBUG: Document inserted with ID: {result.inserted_id}")
            
            # Split text into chunks using LangChain splitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", "। ", " ", ""],
            )
            pieces = splitter.split_text(full_text or "")
            chunks = []
            cursor = 0
            for idx, piece in enumerate(pieces):
                piece = piece.strip()
                if not piece:
                    continue
                start_pos = (full_text or "").find(piece, cursor)
                if start_pos == -1:
                    start_pos = cursor
                end_pos = start_pos + len(piece)
                cursor = end_pos
                chunks.append({
                    "chunk_id": idx,
                    "text": piece,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "char_count": len(piece),
                })
            
            # Helper to infer a rough section label from text
            def _infer_section(text: str) -> str:
                t = (text or "").lower()
                if "project" in t:
                    return "projects"
                if "internship" in t or "internships" in t:
                    return "internships"
                if "education" in t:
                    return "education"
                if "skill" in t:
                    return "skills"
                if "experience" in t:
                    return "experience"
                return "other"

            # Process chunks and create embeddings
            chunks_created = 0
            # Ingest into LangChain vector store first (embeddings computed internally)
            try:
                texts = [c["text"] for c in chunks]
                metadatas = [
                    {
                        "document_id": metadata["document_id"],
                        "chunk_id": c["chunk_id"],
                        "start_pos": c["start_pos"],
                        "end_pos": c["end_pos"],
                        "char_count": c["char_count"],
                        "filename": metadata["filename"],
                        "section": _infer_section(c["text"]),
                    }
                    for c in chunks
                ]
                await lc_vector_store_service.add_texts(texts=texts, metadatas=metadatas)
            except Exception as e:
                print(f"Warning: Failed to add texts to LangChain vector store: {e}")

            for chunk in chunks:
                try:
                    # Generate embedding for the chunk
                    embedding = await vector_search_service.generate_embedding(chunk["text"])
                    
                    # Find page number for this chunk
                    page_number = None
                    for page in page_texts:
                        if chunk["text"] in page["text"]:
                            page_number = page["page_number"]
                            break
                    
                    # Create document chunk
                    document_chunk = DocumentChunk(
                        document_id=metadata["document_id"],
                        chunk_id=chunk["chunk_id"],
                        text=chunk["text"],
                        start_pos=chunk["start_pos"],
                        end_pos=chunk["end_pos"],
                        char_count=chunk["char_count"],
                        embedding=embedding,
                        page_number=page_number
                    )
                    
                    # Save chunk to database
                    print(f"DEBUG: Inserting chunk {chunk['chunk_id']}")
                    result = await self.chunks_collection.insert_one(document_chunk.dict(by_alias=True))
                    print(f"DEBUG: Chunk inserted with ID: {result.inserted_id}")
                    chunks_created += 1
                    
                except Exception as e:
                    print(f"Error processing chunk {chunk['chunk_id']}: {e}")
                    continue
            
            processing_time = (time.time() - start_time) * 1000
            
            return DocumentUploadResponse(
                document_id=metadata["document_id"],
                filename=metadata["filename"],
                status="success",
                message=f"Document processed successfully. Created {chunks_created} chunks.",
                chunks_created=chunks_created,
                processing_time_ms=processing_time
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")
    
    async def search_documents(self, query: str, document_id: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search through uploaded documents using LangChain vector similarity first, fallback to regex search."""
        try:
            print(f"DEBUG: Document service search - Query: '{query}', Document ID: '{document_id}'")
            # Try LangChain vector similarity
            try:
                filter_query = {"document_id": document_id} if document_id else None
                results = lc_vector_store_service.similarity_search_with_similarity(
                    query=query, k=top_k, metadata_filter=filter_query
                )
                vector_results: List[Dict[str, Any]] = []
                for item in results:
                    doc = item.get("doc")
                    sim = float(item.get("similarity", 0.0))
                    meta = getattr(doc, "metadata", None) or {}
                    vector_results.append({
                        "text": getattr(doc, "page_content", None),
                        "document_id": meta.get("document_id"),
                        "page_number": meta.get("page_number"),
                        "score": sim,
                        "filename": meta.get("filename"),
                        "chunk_id": meta.get("chunk_id"),
                        "section": meta.get("section"),
                    })
                if vector_results:
                    # Simple intent-based rerank to improve precision (projects vs internships, etc.)
                    q = (query or "").lower()
                    def bonus(r):
                        s = (r.get("section") or "").lower()
                        text = (r.get("text") or "").lower()
                        b = 0.0
                        if "project" in q:
                            if "project" in s or "project" in text:
                                b += 0.2
                            if "internship" in s or "internship" in text:
                                b -= 0.1
                        if "internship" in q:
                            if "internship" in s or "internship" in text:
                                b += 0.2
                            if "project" in s or "project" in text:
                                b -= 0.1
                        return b
                    vector_results.sort(key=lambda r: (r["score"] + bonus(r)), reverse=True)
                    print(f"DEBUG: Vector search found {len(vector_results)} results")
                    return vector_results
            except Exception as e:
                print(f"DEBUG: LangChain vector search failed, falling back. Reason: {e}")

            # Fallback to regex search
            results = await self._fallback_text_search(query, document_id, top_k)
            print(f"DEBUG: Fallback search - Found {len(results)} results")
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    async def _fallback_text_search(self, query: str, document_id: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Fallback text search when vector search is not available (regex-based)."""
        try:
            # Split query into words and create a more flexible search
            query_words = (query or "").lower().split()

            # Create multiple search patterns for better matching
            search_patterns: List[str] = []

            # Add the full query as a phrase (with flexible spacing)
            search_patterns.append((query or "").replace(" ", "\\s+"))

            # Add the full query as exact phrase
            search_patterns.append(query or "")

            # Add individual words
            search_patterns.extend(query_words)

            # Add variations (e.g., "foreign key" -> "foreignkey", "foreign-key")
            if len(query_words) > 1:
                search_patterns.append("".join(query_words))  # joined
                search_patterns.append("-".join(query_words))  # hyphenated
                search_patterns.append("_".join(query_words))  # underscored

            # Combine all patterns with OR
            search_pattern = "|".join([p for p in search_patterns if p])

            # Try multiple search strategies
            search_filters: List[Dict[str, Any]] = [
                {"text": {"$regex": search_pattern, "$options": "i"}},
            ]

            # If we have multiple words, also try searching for each word individually
            if len(query_words) > 1:
                for word in query_words:
                    search_filters.append({"text": {"$regex": word, "$options": "i"}})

            # Use $or to combine all search strategies
            search_filter: Dict[str, Any] = {"$or": search_filters}
            if document_id:
                search_filter = {
                    "$and": [
                        {"$or": search_filters},
                        {"document_id": document_id}
                    ]
                }

            # Use aggregation to join with documents collection
            pipeline = [
                {"$match": search_filter},
                {
                    "$lookup": {
                        "from": "documents",
                        "localField": "document_id",
                        "foreignField": "document_id",
                        "as": "document"
                    }
                },
                {
                    "$addFields": {
                        "score": 0.8,
                        "document_info": {"$arrayElemAt": ["$document", 0]}
                    }
                },
                {
                    "$project": {
                        "text": 1,
                        "document_id": 1,
                        "page_number": 1,
                        "score": 1,
                        "filename": "$document_info.filename",
                        "chunk_id": 1
                    }
                },
                {"$limit": top_k * 2}
            ]

            results = await self.chunks_collection.aggregate(pipeline).to_list(length=top_k)

            # Convert ObjectId to string for JSON serialization
            for result in results:
                if "_id" in result:
                    result["_id"] = str(result["_id"])

            return results

        except Exception as e:
            print(f"Error in fallback search: {e}")
            return []
    
    async def get_document_list(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of uploaded documents"""
        try:
            filter_query = {}
            if user_id:
                filter_query["user_id"] = user_id
            
            documents = await self.documents_collection.find(filter_query).sort("uploaded_at", -1).to_list(length=None)
            print(f"DEBUG: Found {len(documents)} documents in database")
            
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                doc["_id"] = str(doc["_id"])
                # Handle uploaded_at field - it might be a string or datetime
                if doc.get("uploaded_at"):
                    if hasattr(doc["uploaded_at"], 'isoformat'):
                        doc["uploaded_at"] = doc["uploaded_at"].isoformat()
                    # If it's already a string, keep it as is
                print(f"DEBUG: Document {doc.get('filename', 'Unknown')} - uploaded_at: {doc.get('uploaded_at')}")
            
            return documents
            
        except Exception as e:
            print(f"Error getting document list: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks"""
        try:
            # Delete document chunks
            await self.chunks_collection.delete_many({"document_id": document_id})
            
            # Delete document
            result = await self.documents_collection.delete_one({"document_id": document_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

document_service = DocumentService()
