import PyPDF2
import io
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException
import hashlib
import uuid
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        self.allowed_extensions = ['.pdf']
    
    async def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        if not any(file.filename.lower().endswith(ext) for ext in self.allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Only PDF files are allowed. Got: {file.filename}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > self.max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
            )
        
        # Reset file pointer
        await file.seek(0)
        return True
    
    async def extract_text_from_pdf(self, file: UploadFile) -> Dict[str, Any]:
        """Extract text content from PDF file"""
        try:
            # Validate file first
            await self.validate_file(file)
            
            # Read file content
            file_content = await file.read()
            
            # First attempt: PyPDF2 (fast)
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            full_text = ""
            page_texts = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        full_text += page_text + "\n\n"
                        page_texts.append({
                            "page_number": page_num + 1,
                            "text": page_text.strip(),
                            "char_count": len(page_text.strip())
                        })
                except Exception as e:
                    logger.warning(f"PyPDF2: Error extracting text from page {page_num + 1}: {e}")
                    continue

            # If PyPDF2 extracted very little (common for Indic languages or embedded fonts),
            # try a more robust extractor: pdfminer.six
            if len(full_text.strip()) < 50:
                try:
                    logger.info("PyPDF2 extraction yielded little text; attempting pdfminer.six fallback")
                    from pdfminer.high_level import extract_text
                    pdfminer_text = extract_text(io.BytesIO(file_content)) or ""
                    if pdfminer_text.strip():
                        full_text = pdfminer_text
                        # Rebuild page_texts approximately by splitting on page delimiter if any
                        page_texts = []
                        # pdfminer doesn't easily expose per-page in high_level; keep single block
                        page_texts.append({
                            "page_number": 1,
                            "text": pdfminer_text.strip(),
                            "char_count": len(pdfminer_text.strip())
                        })
                        logger.info(f"pdfminer extracted {len(full_text)} characters")
                except Exception as e:
                    logger.error(f"pdfminer fallback failed: {e}")
            
            # Generate document metadata
            document_id = str(uuid.uuid4())
            file_hash = hashlib.md5(file_content).hexdigest()
            
            metadata = {
                "document_id": document_id,
                "filename": file.filename,
                "file_size": len(file_content),
                "file_hash": file_hash,
                "total_pages": len(getattr(pdf_reader, 'pages', [])) or None,
                "extracted_pages": len(page_texts),
                "total_characters": len(full_text),
                "uploaded_at": datetime.utcnow().isoformat(),
                "status": "processed"
            }
            
            return {
                "metadata": metadata,
                "full_text": full_text.strip(),
                "page_texts": page_texts,
                "success": True
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing PDF: {str(e)}"
            )
    

pdf_processor = PDFProcessor()
