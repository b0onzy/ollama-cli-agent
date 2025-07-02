#!/bin/bash

echo "🚀 Setting up Qdrant for ollama-cli-agent"
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker found. Setting up Qdrant with Docker..."
    
    # Pull and run Qdrant
    docker pull qdrant/qdrant
    
    # Create data directory for persistence
    mkdir -p ./qdrant_storage
    
    # Run Qdrant with persistent storage
    docker run -d \
        --name qdrant \
        -p 6333:6333 \
        -v $(pwd)/qdrant_storage:/qdrant/storage \
        qdrant/qdrant
    
    echo "✅ Qdrant is running on http://localhost:6333"
    echo "📁 Data is persisted in ./qdrant_storage"
    echo ""
    echo "To stop Qdrant: docker stop qdrant"
    echo "To start again: docker start qdrant"
else
    echo "⚠️  Docker not found. You can:"
    echo "1. Install Docker: https://docs.docker.com/get-docker/"
    echo "2. Or use Qdrant in-memory mode (data won't persist between runs)"
    echo ""
    echo "For in-memory mode, the Python client will handle it automatically."
fi
