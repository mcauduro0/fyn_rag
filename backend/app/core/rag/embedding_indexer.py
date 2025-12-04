"""
Embedding and Indexing Module for RAG System.
Generates embeddings using sentence-transformers and creates FAISS index.
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingIndexer:
    """Handles embedding generation and FAISS index creation."""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
        index_type: str = "flatl2"
    ):
        """
        Initialize the embedding indexer.
        
        Args:
            model_name: Name of the sentence-transformers model to use
            index_type: Type of FAISS index ('flatl2', 'ivfflat', 'hnsw')
        """
        self.model_name = model_name
        self.index_type = index_type
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        
    def load_model(self) -> None:
        """Load the sentence-transformers model."""
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info(f"Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def load_chunks(self, chunks_path: str) -> None:
        """
        Load chunks from JSON file.
        
        Args:
            chunks_path: Path to the chunks JSON file
        """
        logger.info(f"Loading chunks from {chunks_path}")
        
        chunks_file = Path(chunks_path)
        if not chunks_file.exists():
            raise FileNotFoundError(f"Chunks file not found at {chunks_path}")
        
        with open(chunks_file, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        logger.info(f"Loaded {len(self.chunks)} chunks")
    
    def generate_embeddings(self, batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for all chunks.
        
        Args:
            batch_size: Batch size for embedding generation
            
        Returns:
            numpy array of embeddings
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        if not self.chunks:
            raise RuntimeError("No chunks loaded. Call load_chunks() first.")
        
        logger.info(f"Generating embeddings for {len(self.chunks)} chunks...")
        
        # Extract content from chunks
        texts = [chunk['content'] for chunk in self.chunks]
        
        # Generate embeddings in batches
        self.embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        logger.info(f"Generated embeddings with shape: {self.embeddings.shape}")
        return self.embeddings
    
    def create_index(self) -> faiss.Index:
        """
        Create FAISS index from embeddings.
        
        Returns:
            FAISS index object
        """
        if self.embeddings is None:
            raise RuntimeError("Embeddings not generated. Call generate_embeddings() first.")
        
        dimension = self.embeddings.shape[1]
        n_vectors = self.embeddings.shape[0]
        
        logger.info(f"Creating FAISS index (type: {self.index_type}) with dimension {dimension}")
        
        if self.index_type == "flatl2":
            # Simple L2 distance index - best for small to medium datasets
            self.index = faiss.IndexFlatL2(dimension)
            
        elif self.index_type == "ivfflat":
            # IVF (Inverted File) index - faster for large datasets
            n_clusters = min(int(np.sqrt(n_vectors)), 100)
            quantizer = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, n_clusters)
            # Train the index
            logger.info("Training IVF index...")
            self.index.train(self.embeddings)
            
        elif self.index_type == "hnsw":
            # HNSW (Hierarchical Navigable Small World) - best accuracy/speed tradeoff
            self.index = faiss.IndexHNSWFlat(dimension, 32)
            self.index.hnsw.efConstruction = 40
            self.index.hnsw.efSearch = 16
            
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")
        
        # Add vectors to index
        logger.info(f"Adding {n_vectors} vectors to index...")
        self.index.add(self.embeddings)
        
        logger.info(f"Index created successfully. Total vectors: {self.index.ntotal}")
        return self.index
    
    def save_index(self, index_path: str) -> None:
        """
        Save FAISS index to disk.
        
        Args:
            index_path: Path to save the index file
        """
        if self.index is None:
            raise RuntimeError("Index not created. Call create_index() first.")
        
        index_file = Path(index_path)
        index_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving FAISS index to {index_file}")
        faiss.write_index(self.index, str(index_file))
        logger.info("Index saved successfully")
    
    def save_metadata(self, metadata_path: str) -> None:
        """
        Save chunk metadata (for mapping index IDs to chunks).
        
        Args:
            metadata_path: Path to save the metadata file
        """
        if not self.chunks:
            raise RuntimeError("No chunks loaded.")
        
        metadata_file = Path(metadata_path)
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create metadata with index mapping
        metadata = {
            "model_name": self.model_name,
            "index_type": self.index_type,
            "total_chunks": len(self.chunks),
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else None,
            "chunks": self.chunks
        }
        
        logger.info(f"Saving metadata to {metadata_file}")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info("Metadata saved successfully")
    
    def load_index(self, index_path: str) -> faiss.Index:
        """
        Load FAISS index from disk.
        
        Args:
            index_path: Path to the index file
            
        Returns:
            Loaded FAISS index
        """
        logger.info(f"Loading FAISS index from {index_path}")
        self.index = faiss.read_index(index_path)
        logger.info(f"Index loaded. Total vectors: {self.index.ntotal}")
        return self.index
    
    def load_metadata(self, metadata_path: str) -> Dict[str, Any]:
        """
        Load chunk metadata from disk.
        
        Args:
            metadata_path: Path to the metadata file
            
        Returns:
            Metadata dictionary
        """
        logger.info(f"Loading metadata from {metadata_path}")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.chunks = metadata.get('chunks', [])
        logger.info(f"Metadata loaded. Total chunks: {len(self.chunks)}")
        
        return metadata


def build_index(
    chunks_path: str,
    index_output_path: str,
    metadata_output_path: str,
    model_name: str = "sentence-transformers/all-mpnet-base-v2",
    index_type: str = "flatl2"
) -> None:
    """
    Complete pipeline to build and save FAISS index.
    
    Args:
        chunks_path: Path to chunks JSON file
        index_output_path: Path to save FAISS index
        metadata_output_path: Path to save metadata
        model_name: Sentence-transformers model name
        index_type: Type of FAISS index
    """
    indexer = EmbeddingIndexer(model_name=model_name, index_type=index_type)
    
    # Load model and chunks
    indexer.load_model()
    indexer.load_chunks(chunks_path)
    
    # Generate embeddings and create index
    indexer.generate_embeddings()
    indexer.create_index()
    
    # Save index and metadata
    indexer.save_index(index_output_path)
    indexer.save_metadata(metadata_output_path)
    
    logger.info("Index building complete!")


if __name__ == "__main__":
    # Test the embedding indexer
    logging.basicConfig(level=logging.INFO)
    
    chunks_path = "/app/data/faiss_index/framework_chunks.json"
    index_path = "/app/data/faiss_index/faiss.index"
    metadata_path = "/app/data/faiss_index/metadata.json"
    
    build_index(
        chunks_path=chunks_path,
        index_output_path=index_path,
        metadata_output_path=metadata_path,
        model_name="sentence-transformers/all-mpnet-base-v2",
        index_type="flatl2"
    )
