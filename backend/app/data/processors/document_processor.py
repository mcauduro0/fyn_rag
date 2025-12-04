"""
Unified Document Processor.
Automatically detects document type and routes to appropriate processor.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from app.data.processors.pdf_processor import PDFProcessor
from app.data.processors.docx_processor import DOCXProcessor
from app.data.processors.xlsx_processor import XLSXProcessor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Unified document processor that handles multiple file formats.
    Automatically detects file type and routes to appropriate processor.
    """
    
    def __init__(self):
        """Initialize all processors."""
        self.pdf_processor = PDFProcessor()
        self.docx_processor = DOCXProcessor()
        self.xlsx_processor = XLSXProcessor()
        
        self.processors = {
            '.pdf': self.pdf_processor,
            '.docx': self.docx_processor,
            '.xlsx': self.xlsx_processor
        }
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document file.
        Automatically detects file type and uses appropriate processor.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "file_path": str(file_path)
                }
            
            # Get file extension (lowercase)
            extension = path.suffix.lower()
            
            # Get appropriate processor
            processor = self.processors.get(extension)
            
            if not processor:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {extension}. Supported: {list(self.processors.keys())}",
                    "file_path": str(file_path)
                }
            
            logger.info(f"Processing {extension} file: {path.name}")
            
            # Process the document
            result = processor.process(str(path))
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": str(file_path)
            }
    
    def is_supported(self, file_path: str) -> bool:
        """
        Check if a file type is supported.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file type is supported, False otherwise
        """
        extension = Path(file_path).suffix.lower()
        return extension in self.processors
    
    def get_supported_formats(self) -> list:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported extensions
        """
        return list(self.processors.keys())


if __name__ == "__main__":
    # Test the unified document processor
    logging.basicConfig(level=logging.INFO)
    
    processor = DocumentProcessor()
    
    print(f"Supported formats: {processor.get_supported_formats()}")
    
    # Test with different file types
    test_files = ["sample.pdf", "sample.docx", "sample.xlsx"]
    
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"Testing: {test_file}")
        print(f"Supported: {processor.is_supported(test_file)}")
        
        result = processor.process(test_file)
        
        if result["success"]:
            print(f"✓ Success!")
            print(f"  Content length: {result['content_length']} characters")
            print(f"  Metadata: {list(result['metadata'].keys())}")
        else:
            print(f"✗ Error: {result['error']}")
