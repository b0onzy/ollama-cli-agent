#!/usr/bin/env python3
"""Unit tests for the Assistant CLI class."""

import unittest
from unittest.mock import Mock, patch, call
import sys
import os
from io import StringIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.assistant import Assistant


class TestAssistant(unittest.TestCase):
    """Test cases for the Assistant CLI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the Agent
        self.mock_agent = Mock()
        
        # Patch the Agent import
        self.patcher_agent = patch('src.assistant.Agent')
        self.mock_agent_class = self.patcher_agent.start()
        self.mock_agent_class.return_value = self.mock_agent
        
        # Create assistant instance
        self.assistant = Assistant()
    
    def tearDown(self):
        """Clean up after tests."""
        self.patcher_agent.stop()
    
    def test_initialization(self):
        """Test assistant initialization."""
        # Check that agent was initialized
        self.mock_agent_class.assert_called_once_with(
            model_name="mistral:7b",
            embedding_model="all-minilm"
        )
        
        # Check commands are registered
        expected_commands = ["ask", "ingest", "search", "fetch", "help", "stats", "exit", "quit"]
        for cmd in expected_commands:
            self.assertIn(cmd, self.assistant.commands)
    
    @patch('builtins.print')
    def test_cmd_ask(self, mock_print):
        """Test ask command."""
        # Mock agent response
        self.mock_agent.ask.return_value = "The answer is 42."
        
        # Test ask
        self.assistant.cmd_ask("What is the meaning of life?")
        
        # Verify
        self.mock_agent.ask.assert_called_once_with("What is the meaning of life?")
        mock_print.assert_any_call("\nThinking...")
        mock_print.assert_any_call("\nThe answer is 42.\n")
    
    @patch('builtins.print')
    def test_cmd_ask_empty(self, mock_print):
        """Test ask command with empty input."""
        self.assistant.cmd_ask("")
        
        # Verify usage message
        mock_print.assert_called_once_with("Usage: ask <question>")
        self.mock_agent.ask.assert_not_called()
    
    @patch('builtins.print')
    def test_cmd_ingest_text(self, mock_print):
        """Test ingest command with text."""
        # Mock successful ingestion
        self.mock_agent.ingest.return_value = True
        
        # Test ingest
        self.assistant.cmd_ingest("Some important information")
        
        # Verify
        self.mock_agent.ingest.assert_called_once_with("Some important information")
        mock_print.assert_called_with("✓ Content ingested successfully")
    
    @patch('builtins.print')
    def test_cmd_ingest_url(self, mock_print):
        """Test ingest command with URL."""
        # Mock successful fetch and ingestion
        self.mock_agent.fetch_url.return_value = {
            "content": "Web page content",
            "title": "Page Title"
        }
        
        # Test ingest with URL
        self.assistant.cmd_ingest("https://example.com")
        
        # Verify
        self.mock_agent.fetch_url.assert_called_once_with("https://example.com")
        # The assistant doesn't call ingest for URLs, it just fetches
        mock_print.assert_any_call("✓ Ingested: Page Title")
    
    @patch('builtins.print')
    def test_cmd_search(self, mock_print):
        """Test search command."""
        # Mock search results
        self.mock_agent.search_web.return_value = [
            {"title": "Result 1", "link": "http://example1.com", "snippet": "Snippet 1"},
            {"title": "Result 2", "link": "http://example2.com", "snippet": "Snippet 2"}
        ]
        
        # Test search
        self.assistant.cmd_search("python programming")
        
        # Verify
        self.mock_agent.search_web.assert_called_once_with("python programming")
        mock_print.assert_any_call("\nSearching for: python programming")
        mock_print.assert_any_call("1. Result 1")
    
    @patch('builtins.print')
    def test_cmd_fetch(self, mock_print):
        """Test fetch command."""
        # Mock fetch result
        self.mock_agent.fetch_url.return_value = {
            "content": "Fetched content",
            "title": "Fetched Title",
            "url": "http://example.com"
        }
        
        # Test fetch
        self.assistant.cmd_fetch("http://example.com")
        
        # Verify
        self.mock_agent.fetch_url.assert_called_once_with("http://example.com")
        # Verify some output was printed
        self.assertTrue(mock_print.called)
    
    @patch('builtins.print')
    def test_cmd_stats(self, mock_print):
        """Test stats command."""
        # Mock memory stats
        self.mock_agent.get_memory_stats.return_value = {
            "name": "test_collection",
            "points_count": 10,
            "vectors_count": 10
        }
        
        # Test stats
        self.assistant.cmd_stats("")
        
        # Verify
        self.mock_agent.get_memory_stats.assert_called_once()
        # The actual implementation prints JSON, not formatted text
        mock_print.assert_any_call("\n📊 Memory Statistics:\n")
    
    @patch('builtins.print')
    def test_cmd_help(self, mock_print):
        """Test help command."""
        self.assistant.cmd_help("")
        
        # Verify help text is printed
        calls = [call.args[0] for call in mock_print.call_args_list]
        help_text = '\n'.join(calls)
        
        # Check that all commands are documented
        self.assertIn("ask", help_text)
        self.assertIn("ingest", help_text)
        self.assertIn("search", help_text)
        self.assertIn("fetch", help_text)
        self.assertIn("stats", help_text)
        self.assertIn("help", help_text)
        self.assertIn("exit", help_text)
    
    def test_cmd_exit(self):
        """Test exit command."""
        with self.assertRaises(SystemExit):
            self.assistant.cmd_exit("")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_basic_flow(self, mock_print, mock_input):
        """Test basic REPL flow."""
        # Mock user inputs
        mock_input.side_effect = ["help", "exit"]
        
        # Run REPL (will exit after two commands)
        with self.assertRaises(SystemExit):
            self.assistant.run()
        
        # Verify welcome message
        mock_print.assert_any_call("\n🧠 Ollama CLI Agent")
        mock_print.assert_any_call("Type 'help' for available commands\n")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_unknown_command(self, mock_print, mock_input):
        """Test handling of unknown commands."""
        # Mock user inputs
        mock_input.side_effect = ["unknown", "exit"]
        
        # Run REPL
        with self.assertRaises(SystemExit):
            self.assistant.run()
        
        # Verify error message
        mock_print.assert_any_call("Unknown command: unknown. Type 'help' for available commands.")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input):
        """Test handling of Ctrl+C."""
        # Mock keyboard interrupt followed by exit
        mock_input.side_effect = [KeyboardInterrupt(), "exit"]
        
        # Run REPL
        with self.assertRaises(SystemExit):
            self.assistant.run()
        
        # Verify message
        mock_print.assert_any_call("\n\nUse 'exit' to quit.")


class TestAssistantIntegration(unittest.TestCase):
    """Integration tests for the Assistant class."""
    
    @patch('src.assistant.Agent')
    def test_custom_model_initialization(self, mock_agent_class):
        """Test assistant initialization with custom models."""
        # Create assistant with custom models
        assistant = Assistant(model="llama2", embedding_model="custom-embed")
        
        # Verify agent was initialized with custom models
        mock_agent_class.assert_called_once_with(
            model_name="llama2",
            embedding_model="custom-embed"
        )


if __name__ == '__main__':
    unittest.main()
