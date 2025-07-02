#!/usr/bin/env python3
"""Integration test for ollama-cli-agent."""

import sys
import os
import logging

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent import Agent
from utils.logging import setup_logger, logger

def test_agent():
    """Test basic agent functionality."""
    print("🧪 Testing ollama-cli-agent integration...\n")
    
    # Setup logging
    setup_logger(level=logging.INFO)
    
    try:
        # Initialize agent
        print("1. Initializing agent...")
        agent = Agent(model_name="mistral:7b", embedding_model="all-minilm")
        print("✓ Agent initialized successfully\n")
        
        # Test ingestion
        print("2. Testing content ingestion...")
        success = agent.ingest("The Eiffel Tower is located in Paris, France. It was built in 1889.")
        if success:
            print("✓ Content ingested successfully\n")
        else:
            print("✗ Failed to ingest content\n")
        
        # Test memory stats
        print("3. Testing memory stats...")
        stats = agent.get_memory_stats()
        print(f"✓ Memory stats: {stats}\n")
        
        # Test asking a question
        print("4. Testing question answering...")
        response = agent.ask("Where is the Eiffel Tower located?")
        print(f"✓ Response: {response[:200]}...\n" if len(response) > 200 else f"✓ Response: {response}\n")
        
        # Test web search (if configured)
        print("5. Testing web search...")
        if agent.tools:
            results = agent.search_web("Python programming", tool="auto")
            if results:
                print(f"✓ Found {len(results)} search results")
                print(f"   First result: {results[0]['title']}\n")
            else:
                print("⚠ No search results (API keys might not be configured)\n")
        else:
            print("⚠ No web tools configured (check API keys in .env)\n")
        
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    import logging
    test_agent()
