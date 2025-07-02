"""Qdrant vector store for persistent memory."""

import os
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
)
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)


class QdrantStore:
    """Manages vector storage and retrieval using Qdrant."""
    
    def __init__(
        self,
        collection_name: str = "ollama_agent_memory",
        host: str = "localhost",
        port: int = 6333,
        vector_size: int = 384,  # Default for all-MiniLM-L6-v2
        use_memory_mode: bool = False,
    ):
        """Initialize Qdrant client and collection.
        
        Args:
            collection_name: Name of the Qdrant collection
            host: Qdrant server host
            port: Qdrant server port
            vector_size: Dimension of embedding vectors
            use_memory_mode: If True, use in-memory storage (no persistence)
        """
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Initialize client
        if use_memory_mode:
            logger.info("Using Qdrant in memory mode (no persistence)")
            self.client = QdrantClient(":memory:")
        else:
            try:
                self.client = QdrantClient(host=host, port=port)
                logger.info(f"Connected to Qdrant at {host}:{port}")
            except Exception as e:
                logger.warning(f"Failed to connect to Qdrant server: {e}")
                logger.info("Falling back to in-memory mode")
                self.client = QdrantClient(":memory:")
        
        # Create collection if it doesn't exist
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            if not any(col.name == self.collection_name for col in collections):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
            raise
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Add documents to the vector store.
        
        Args:
            texts: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts
            
        Returns:
            List of document IDs
        """
        if len(texts) != len(embeddings):
            raise ValueError("Number of texts must match number of embeddings")
        
        if metadatas and len(metadatas) != len(texts):
            raise ValueError("Number of metadatas must match number of texts")
        
        points = []
        ids = []
        
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            doc_id = str(uuid4())
            ids.append(doc_id)
            
            payload = {
                "text": text,
                "doc_id": doc_id,
            }
            
            if metadatas and i < len(metadatas):
                payload.update(metadatas[i])
            
            points.append(
                PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload=payload,
                )
            )
        
        # Upload points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )
        
        logger.info(f"Added {len(points)} documents to collection")
        return ids
    
    def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            filter_dict: Optional filter conditions
            
        Returns:
            List of search results with text, score, and metadata
        """
        search_filter = None
        if filter_dict:
            # Build filter from dict
            conditions = []
            for key, value in filter_dict.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )
            if conditions:
                search_filter = Filter(must=conditions)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=search_filter,
        )
        
        return [
            {
                "text": hit.payload.get("text", ""),
                "score": hit.score,
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
            }
            for hit in results
        ]
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            # Handle different attribute names in the collection info
            return {
                "name": self.collection_name,
                "vectors_count": getattr(info, 'vectors_count', 0),
                "points_count": getattr(info, 'points_count', 0),
                "status": getattr(info, 'status', 'unknown'),
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}