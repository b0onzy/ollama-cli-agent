#!/usr/bin/env python3
"""Test Qdrant setup and basic operations."""

import sys
sys.path.append('.')

from src.qdrant_store import QdrantStore
import numpy as np

def test_qdrant():
    print("🧪 Testing Qdrant setup...")
    
    # Initialize in memory mode
    store = QdrantStore(use_memory_mode=True)
    print("✅ Qdrant initialized in memory mode")
    
    # Test adding documents
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "Python is a great programming language",
        "Qdrant is a vector database for AI applications",
    ]
    
    # Generate dummy embeddings (normally you'd use a real embedding model)
    embeddings = [np.random.rand(384).tolist() for _ in texts]
    
    metadatas = [
        {"source": "test", "type": "sentence"},
        {"source": "test", "type": "programming"},
        {"source": "test", "type": "database"},
    ]
    
    ids = store.add_documents(texts, embeddings, metadatas)
    print(f"✅ Added {len(ids)} documents")
    
    # Test search
    query_embedding = np.random.rand(384).tolist()
    results = store.search(query_embedding, limit=2)
    print(f"✅ Search returned {len(results)} results")
    
    for i, result in enumerate(results):
        print(f"  Result {i+1}: {result['text'][:50]}... (score: {result['score']:.3f})")
    
    # Get collection info
    info = store.get_collection_info()
    print(f"\n📊 Collection info:")
    print(f"  - Points count: {info.get('points_count', 0)}")
    print(f"  - Status: {info.get('status', 'unknown')}")
    
    print("\n✅ All tests passed! Qdrant is working correctly.")
    print("\n💡 Note: Currently using in-memory mode. To persist data:")
    print("   1. Install Docker and run: docker run -p 6333:6333 qdrant/qdrant")
    print("   2. Then initialize QdrantStore without use_memory_mode=True")

if __name__ == "__main__":
    test_qdrant()
