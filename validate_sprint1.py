"""
Sprint 1 Validation Script
Validates that all components are properly implemented.
"""

import sys
from pathlib import Path

def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(path).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - NOT FOUND")
        return False

def main():
    print("=" * 60)
    print("Fyn RAG - Sprint 1 Validation")
    print("=" * 60)
    
    all_passed = True
    
    # Core RAG System
    print("\n📚 RAG System Components:")
    all_passed &= check_file_exists("backend/app/core/rag/data_preparation.py", "Data Preparation")
    all_passed &= check_file_exists("backend/app/core/rag/embedding_indexer.py", "Embedding Indexer")
    all_passed &= check_file_exists("backend/app/core/rag/query_system.py", "Query System")
    all_passed &= check_file_exists("backend/app/core/rag/rag_system.py", "RAG System Integration")
    all_passed &= check_file_exists("backend/app/core/rag/investment_kb_enriched.json", "Knowledge Base")
    
    # Data Fetchers
    print("\n📊 Data Fetchers:")
    all_passed &= check_file_exists("backend/app/data/fetchers/polygon_fetcher.py", "Polygon.io Fetcher")
    all_passed &= check_file_exists("backend/app/data/fetchers/fmp_fetcher.py", "FMP Fetcher")
    all_passed &= check_file_exists("backend/app/data/fetchers/fred_fetcher.py", "FRED Fetcher")
    all_passed &= check_file_exists("backend/app/data/fetchers/trading_economics_fetcher.py", "Trading Economics Fetcher")
    all_passed &= check_file_exists("backend/app/data/fetchers/reddit_fetcher.py", "Reddit Fetcher")
    
    # Document Processors
    print("\n📄 Document Processors:")
    all_passed &= check_file_exists("backend/app/data/processors/pdf_processor.py", "PDF Processor")
    all_passed &= check_file_exists("backend/app/data/processors/docx_processor.py", "DOCX Processor")
    all_passed &= check_file_exists("backend/app/data/processors/xlsx_processor.py", "XLSX Processor")
    all_passed &= check_file_exists("backend/app/data/processors/document_processor.py", "Document Processor Integration")
    
    # API Endpoints
    print("\n🌐 API Endpoints:")
    all_passed &= check_file_exists("backend/app/api/endpoints/rag.py", "RAG Endpoints")
    all_passed &= check_file_exists("backend/app/api/endpoints/data.py", "Data Endpoints")
    all_passed &= check_file_exists("backend/app/api/schemas/rag_schemas.py", "RAG Schemas")
    all_passed &= check_file_exists("backend/app/api/schemas/data_schemas.py", "Data Schemas")
    
    # Tests
    print("\n🧪 Tests:")
    all_passed &= check_file_exists("backend/tests/test_rag_system.py", "RAG System Tests")
    all_passed &= check_file_exists("backend/tests/test_data_layer.py", "Data Layer Tests")
    all_passed &= check_file_exists("backend/tests/conftest.py", "Test Configuration")
    
    # Infrastructure
    print("\n🐳 Infrastructure:")
    all_passed &= check_file_exists("docker-compose.yml", "Docker Compose")
    all_passed &= check_file_exists("backend/Dockerfile", "Backend Dockerfile")
    all_passed &= check_file_exists(".env", "Environment Variables")
    all_passed &= check_file_exists("backend/requirements.txt", "Python Requirements")
    
    # Documentation
    print("\n📖 Documentation:")
    all_passed &= check_file_exists("README.md", "Main README")
    all_passed &= check_file_exists(".gitignore", "Git Ignore")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Sprint 1 Validation: PASSED")
        print("All components are properly implemented!")
        return 0
    else:
        print("❌ Sprint 1 Validation: FAILED")
        print("Some components are missing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
