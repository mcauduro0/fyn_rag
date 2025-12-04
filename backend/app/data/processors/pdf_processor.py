"""
PDF Document Processor.
Extracts text content from PDF files.
"""

import logging
from typing import Dict, Any
from pypdf import PdfReader

from app.data.processors.base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class PDFProcessor(BaseProcessor):
    """Processor for PDF documents."""
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Validate file
            path = self._validate_file(file_path, ['.pdf', '.PDF'])
            
            logger.info(f"Processing PDF: {path}")
            
            # Read PDF
            reader = PdfReader(str(path))
            
            # Extract metadata
            metadata = {
                "num_pages": len(reader.pages),
                "file_name": path.name,
                "file_size_bytes": path.stat().st_size
            }
            
            # Add PDF metadata if available
            if reader.metadata:
                pdf_meta = reader.metadata
                metadata.update({
                    "title": pdf_meta.get("/Title", ""),
                    "author": pdf_meta.get("/Author", ""),
                    "subject": pdf_meta.get("/Subject", ""),
                    "creator": pdf_meta.get("/Creator", ""),
                    "producer": pdf_meta.get("/Producer", ""),
                    "creation_date": pdf_meta.get("/CreationDate", "")
                })
            
            # Extract text from all pages
            text_content = []
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(f"--- Page {page_num} ---\n{page_text}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
            
            # Combine all text
            full_text = "\n\n".join(text_content)
            
            logger.info(f"Successfully extracted {len(full_text)} characters from {metadata['num_pages']} pages")
            
            return self._success_response(full_text, metadata, path)
            
        except Exception as e:
            return self._error_response(e, file_path)


if __name__ == "__main__":
    # Test the PDF processor
    logging.basicConfig(level=logging.INFO)
    
    processor = PDFProcessor()
    
    # Test with a sample PDF (you'll need to provide a path)
    test_file = "sample.pdf"
    
    result = processor.process(test_file)
    
    if result["success"]:
        print(f"\nSuccessfully processed PDF:")
        print(f"Pages: {result['metadata']['num_pages']}")
        print(f"Content length: {result['content_length']} characters")
        print(f"\nFirst 500 characters:")
        print(result["content"][:500])
    else:
        print(f"\nError: {result['error']}")
