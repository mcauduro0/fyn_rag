"""
Base class for document processors.
Provides common functionality for extracting data from various document formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """Abstract base class for document processors."""
    
    def __init__(self):
        """Initialize the processor."""
        pass
    
    @abstractmethod
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document and extract its content.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        pass
    
    def _validate_file(self, file_path: str, expected_extensions: list) -> Path:
        """
        Validate that file exists and has correct extension.
        
        Args:
            file_path: Path to the file
            expected_extensions: List of valid extensions (e.g., ['.pdf', '.PDF'])
            
        Returns:
            Path object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file has wrong extension
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix not in expected_extensions:
            raise ValueError(
                f"Invalid file extension: {path.suffix}. "
                f"Expected one of: {expected_extensions}"
            )
        
        return path
    
    def _success_response(
        self,
        content: str,
        metadata: Dict[str, Any],
        file_path: str
    ) -> Dict[str, Any]:
        """
        Create a standardized success response.
        
        Args:
            content: Extracted text content
            metadata: Document metadata
            file_path: Path to the processed file
            
        Returns:
            Success response dictionary
        """
        return {
            "success": True,
            "content": content,
            "metadata": metadata,
            "file_path": str(file_path),
            "content_length": len(content)
        }
    
    def _error_response(self, error: Exception, file_path: str) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            error: The exception that occurred
            file_path: Path to the file that failed
            
        Returns:
            Error response dictionary
        """
        logger.error(f"Error processing {file_path}: {str(error)}")
        return {
            "success": False,
            "error": str(error),
            "file_path": str(file_path)
        }
