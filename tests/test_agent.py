#!/usr/bin/env python3
"""Unit tests for the Agent class."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import Agent


class TestAgent(unittest.TestCase):
    """Test cases for the Agent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the Ollama models and Qdrant
        self.mock_llm = Mock()
        self.mock_embeddings = Mock()
        self.mock_memory = Mock()
        
        # Patch the imports
        self.patcher_llm = patch('src.agent.OllamaLLM')
        self.patcher_embeddings = patch('src.agent.OllamaEmbeddings')
        self.patcher_memory = patch('src.agent.QdrantStore')
        
        self.mock_llm_class = self.patcher_llm.start()
        self.mock_embeddings_class = self.patcher_embeddings.start()
        self.mock_memory_class = self.patcher_memory.start()
        
        # Configure the mocks
        self.mock_llm_class.return_value = self.mock_llm
        self.mock_embeddings_class.return_value = self.mock_embeddings
        self.mock_memory_class.return_value = self.mock_memory
        
        # Create agent instance
        self.agent = Agent()
    
    def tearDown(self):
        """Clean up after tests."""
        self.patcher_llm.stop()
        self.patcher_embeddings.stop()
        self.patcher_memory.stop()
    
    def test_initialization(self):
        """Test agent initialization."""
        # Check that models were initialized
        self.mock_llm_class.assert_called_once_with(model="mistral:7b")
        self.mock_embeddings_class.assert_called_once_with(model="all-minilm")
        self.mock_memory_class.assert_called_once()
        
        # Check agent attributes
        self.assertIsNotNone(self.agent.llm)
        self.assertIsNotNone(self.agent.embeddings)
        self.assertIsNotNone(self.agent.memory)
        self.assertIsInstance(self.agent.tools, dict)
    
    def test_embed_texts(self):
        """Test text embedding."""
        # Mock embedding response
        self.mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Test embedding
        texts = ["Hello world", "Test text"]
        embeddings = self.agent._embed_texts(texts)
        
        # Verify
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(embeddings[0], [0.1, 0.2, 0.3])
        self.assertEqual(self.mock_embeddings.embed_query.call_count, 2)
    
    def test_ingest_success(self):
        """Test successful content ingestion."""
        # Mock embedding
        self.mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Test ingestion
        content = "Test content to ingest"
        result = self.agent.ingest(content)
        
        # Verify
        self.assertTrue(result)
        self.mock_memory.add_documents.assert_called_once()
        
        # Check the call arguments
        call_args = self.mock_memory.add_documents.call_args
        self.assertEqual(call_args[1]['texts'], [content])
        self.assertEqual(len(call_args[1]['embeddings']), 1)
        self.assertEqual(len(call_args[1]['metadatas']), 1)
        self.assertIn('ingested_at', call_args[1]['metadatas'][0])
    
    def test_ingest_failure(self):
        """Test failed content ingestion."""
        # Mock embedding to raise exception
        self.mock_embeddings.embed_query.side_effect = Exception("Embedding failed")
        
        # Test ingestion
        result = self.agent.ingest("Test content")
        
        # Verify
        self.assertFalse(result)
    
    @patch('src.agent.os.getenv')
    def test_initialize_tools_with_keys(self, mock_getenv):
        """Test tool initialization with API keys."""
        # Mock environment variables
        def getenv_side_effect(key):
            return {
                'SERPAPI_API_KEY': 'test_serpapi_key',
                'BRAVE_API_KEY': 'test_brave_key',
                'FIRECRAWL_API_KEY': 'test_firecrawl_key'
            }.get(key)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Re-initialize tools
        with patch('src.agent.SerpAPITool'), \
             patch('src.agent.BraveSearchTool'), \
             patch('src.agent.FireCrawlTool'):
            tools = self.agent._initialize_tools()
        
        # Verify all tools were initialized
        self.assertIn('serpapi', tools)
        self.assertIn('brave', tools)
        self.assertIn('firecrawl', tools)
    
    def test_search_web_auto(self):
        """Test web search with auto tool selection."""
        # Mock tools
        mock_serpapi = Mock()
        mock_serpapi.return_value = [{"title": "Result 1", "url": "http://example.com"}]
        self.agent.tools = {"serpapi": mock_serpapi}
        
        # Test search
        results = self.agent.search_web("test query")
        
        # Verify
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Result 1")
        mock_serpapi.assert_called_once_with("test query")
    
    def test_search_web_specific_tool(self):
        """Test web search with specific tool."""
        # Mock tools
        mock_brave = Mock()
        mock_brave.return_value = [{"title": "Brave Result", "url": "http://example.com"}]
        self.agent.tools = {"brave": mock_brave}
        
        # Test search
        results = self.agent.search_web("test query", tool="brave")
        
        # Verify
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Brave Result")
        mock_brave.assert_called_once_with("test query")
    
    def test_fetch_url_success(self):
        """Test successful URL fetching."""
        # Mock firecrawl tool
        mock_firecrawl = Mock()
        mock_firecrawl.return_value = {
            "content": "Page content",
            "title": "Page Title",
            "url": "http://example.com"
        }
        self.agent.tools = {"firecrawl": mock_firecrawl}
        
        # Mock embedding for auto-ingest
        self.mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Test fetch
        result = self.agent.fetch_url("http://example.com")
        
        # Verify
        self.assertEqual(result["content"], "Page content")
        self.assertEqual(result["title"], "Page Title")
        mock_firecrawl.assert_called_once_with("http://example.com")
        
        # Verify auto-ingest was called
        self.mock_memory.add_documents.assert_called_once()
    
    def test_ask_with_memory(self):
        """Test asking questions with memory context."""
        # Mock memory search
        self.mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        self.mock_memory.search.return_value = [
            {"text": "Paris is the capital of France.", "score": 0.9}
        ]
        
        # Mock LLM response
        self.mock_llm.invoke.return_value = "Paris is the capital of France."
        
        # Test ask
        response = self.agent.ask("What is the capital of France?")
        
        # Verify
        self.assertEqual(response, "Paris is the capital of France.")
        self.mock_memory.search.assert_called_once()
        self.mock_llm.invoke.assert_called_once()
        
        # Check that context was included in prompt
        prompt = self.mock_llm.invoke.call_args[0][0]
        self.assertIn("Paris is the capital of France.", prompt)
    
    def test_ask_without_memory(self):
        """Test asking questions without memory context."""
        # Mock LLM response
        self.mock_llm.invoke.return_value = "I need more context."
        
        # Test ask
        response = self.agent.ask("What is the capital of France?", use_memory=False)
        
        # Verify
        self.assertEqual(response, "I need more context.")
        self.mock_memory.search.assert_not_called()
        self.mock_llm.invoke.assert_called_once()
    
    def test_get_memory_stats(self):
        """Test getting memory statistics."""
        # Mock memory stats
        self.mock_memory.get_collection_info.return_value = {
            "name": "test_collection",
            "points_count": 10,
            "vectors_count": 10
        }
        
        # Test stats
        stats = self.agent.get_memory_stats()
        
        # Verify
        self.assertEqual(stats["name"], "test_collection")
        self.assertEqual(stats["points_count"], 10)
        self.mock_memory.get_collection_info.assert_called_once()


if __name__ == '__main__':
    unittest.main()