import logging
import os
from typing import Optional
from fastapi import UploadFile, HTTPException
import PyPDF2
from config.settings import get_settings
import fitz
import io

logger = logging.getLogger(__name__)

class FileProcessor:
    """Service for processing uploaded files"""
    
    def __init__(self):
        self.settings = get_settings()
        logger.info("FileProcessor initialized")
    
    def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        # Check file size
        if file.size and file.size > self.settings.max_file_size:
            logger.warning(f"File {file.filename} exceeds size limit: {file.size} bytes")
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds limit of {self.settings.max_file_size} bytes"
            )
        
        # Check file extension
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in self.settings.supported_file_types:
                logger.warning(f"Unsupported file type: {file_ext}")
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type. Supported types: {', '.join(self.settings.supported_file_types)}"
                )
        
        logger.info(f"File {file.filename} validation passed")
        return True
    
    async def process_file(self, file: UploadFile) -> str:
        """Process uploaded file and extract text content"""
        self.validate_file(file)
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        content = await file.read()
        
        try:
            if file_ext == ".pdf":
                text_content = self._extract_pdf_text(content)
            elif file_ext == ".txt":
                text_content = content.decode('utf-8')
            else:
                raise HTTPException(status_code=415, detail=f"Unsupported file type: {file_ext}")
            
            logger.info(f"Successfully processed {file.filename}: {len(text_content)} characters extracted")
            return text_content
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    def _extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            text_content = ""
            pdf_stream = io.BytesIO(pdf_content)
            doc=fitz.open(stream = pdf_stream, filetype='pdf')
            
            for page_num in range(doc.page_count):
                try:
                    text_content+=doc[page_num].get_text()
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                    continue
            
            if not text_content.strip():
                raise ValueError("No text content could be extracted from PDF")
            
            logger.info(f"Successfully extracted {len(doc)} pages from PDF")
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def get_file_info(self, file: UploadFile) -> dict:
        """Get file information"""
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size,
            "extension": os.path.splitext(file.filename)[1].lower() if file.filename else None
        }

# Global file processor instance
file_processor = FileProcessor()