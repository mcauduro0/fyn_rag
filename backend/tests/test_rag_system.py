"""
Tests for RAG System.
"""

import pytest
from pathlib import Path

from app.core.rag.data_preparation import DataPreparation, FrameworkChunk
from app.core.rag.embedding_indexer import EmbeddingIndexer
from app.core.rag.query_system import QuerySystem
from app.core.rag.rag_system import RAGSystem


class TestDataPreparation:
    """Tests for DataPreparation class."""
    
    def test_load_knowledge_base(self, tmp_path):
        """Test loading knowledge base from JSON."""
        # Create a test knowledge base
        kb_file = tmp_path / "test_kb.json"
        kb_file.write_text('[{"name": "Test Framework", "category": "Test", "description": "Test description"}]')
        
        prep = DataPreparation(str(kb_file))
        prep.load_knowledge_base()
        
        assert len(prep.frameworks) == 1
        assert prep.frameworks[0]["name"] == "Test Framework"
    
    def test_create_semantic_chunks(self, tmp_path):
        """Test creating semantic chunks from frameworks."""
        # Create a test knowledge base
        kb_file = tmp_path / "test_kb.json"
        kb_file.write_text('''[{
            "name": "Test Framework",
            "category": "Test",
            "description": "Test description",
            "key_metrics": ["Metric 1", "Metric 2"],
            "application": "Test application"
        }]''')
        
        prep = DataPreparation(str(kb_file))
        prep.load_knowledge_base()
        chunks = prep.create_semantic_chunks()
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, FrameworkChunk) for chunk in chunks)
        assert any(chunk.chunk_type == "overview" for chunk in chunks)


class TestEmbeddingIndexer:
    """Tests for EmbeddingIndexer class."""
    
    @pytest.mark.slow
    def test_load_model(self):
        """Test loading sentence-transformers model."""
        indexer = EmbeddingIndexer(model_name="sentence-transformers/all-MiniLM-L6-v2")
        indexer.load_model()
        
        assert indexer.model is not None
        assert indexer.model.get_sentence_embedding_dimension() > 0
    
    @pytest.mark.slow
    def test_generate_embeddings(self, tmp_path):
        """Test generating embeddings from chunks."""
        # Create test chunks
        chunks_file = tmp_path / "chunks.json"
        chunks_file.write_text('''[{
            "chunk_id": "test_1",
            "framework_name": "Test",
            "framework_category": "Test",
            "chunk_type": "overview",
            "content": "This is a test chunk",
            "metadata": {}
        }]''')
        
        indexer = EmbeddingIndexer(model_name="sentence-transformers/all-MiniLM-L6-v2")
        indexer.load_model()
        indexer.load_chunks(str(chunks_file))
        embeddings = indexer.generate_embeddings()
        
        assert embeddings is not None
        assert len(embeddings) == 1
        assert embeddings.shape[1] > 0


class TestRAGSystem:
    """Tests for RAGSystem class."""
    
    def test_initialization(self, tmp_path):
        """Test RAG system initialization."""
        kb_file = tmp_path / "kb.json"
        kb_file.write_text('[{"name": "Test", "category": "Test", "description": "Test"}]')
        
        index_dir = tmp_path / "index"
        
        rag = RAGSystem(
            kb_path=str(kb_file),
            index_dir=str(index_dir)
        )
        
        assert rag.kb_path.exists()
        assert not rag._initialized
    
    @pytest.mark.slow
    def test_build_and_query(self, tmp_path):
        """Test building index and querying."""
        # Create test knowledge base
        kb_file = tmp_path / "kb.json"
        kb_file.write_text('''[{
            "name": "DCF Valuation",
            "category": "Valuation",
            "description": "Discounted Cash Flow valuation method",
            "core_concept": "Present value of future cash flows",
            "key_metrics": ["FCF", "WACC", "Terminal Value"],
            "application": "Used for valuing companies based on cash flow projections"
        }]''')
        
        index_dir = tmp_path / "index"
        
        rag = RAGSystem(
            kb_path=str(kb_file),
            index_dir=str(index_dir),
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Build index
        rag.build_index()
        
        # Initialize for querying
        rag.initialize(auto_build=False)
        
        # Query
        results = rag.query("How to value a company?", top_k=3)
        
        assert len(results) > 0
        assert results[0].framework_name == "DCF Valuation"
        assert results[0].score > 0


@pytest.fixture
def sample_kb_path(tmp_path):
    """Create a sample knowledge base for testing."""
    kb_file = tmp_path / "test_kb.json"
    kb_file.write_text('''[
        {
            "name": "Moat Analysis",
            "category": "Value Investing",
            "description": "Framework for identifying sustainable competitive advantages",
            "core_concept": "Economic moats protect long-term profitability",
            "key_metrics": ["Switching costs", "Network effects", "Brand strength"],
            "application": "Identify companies with durable competitive advantages"
        },
        {
            "name": "Rule of 40",
            "category": "Growth & VC",
            "description": "SaaS company health metric",
            "core_concept": "Growth rate + profit margin should exceed 40%",
            "key_metrics": ["Revenue growth", "EBITDA margin"],
            "application": "Evaluate SaaS company performance"
        }
    ]''')
    return kb_file


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
