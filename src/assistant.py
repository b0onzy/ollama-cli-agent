#!/usr/bin/env python3
"""CLI REPL for ollama-cli-agent."""

import os
import sys
import argparse
from typing import Optional
import json
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import Agent
from utils.logging import logger, setup_logger


class Assistant:
    """CLI assistant for interacting with the agent."""
    
    def __init__(self, model: str = "mistral:7b", embedding_model: str = "all-minilm"):
        """Initialize the assistant.
        
        Args:
            model: Ollama model to use
            embedding_model: Embedding model to use
        """
        self.agent = Agent(model_name=model, embedding_model=embedding_model)
        self.commands = {
            "ask": self.cmd_ask,
            "ingest": self.cmd_ingest,
            "search": self.cmd_search,
            "fetch": self.cmd_fetch,
            "help": self.cmd_help,
            "stats": self.cmd_stats,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
        }
    
    def cmd_ask(self, args: str) -> None:
        """Ask a question to the agent."""
        if not args.strip():
            print("Usage: ask <question>")
            return
        
        print("\nThinking...")
        response = self.agent.ask(args)
        print(f"\n{response}\n")
    
    def cmd_ingest(self, args: str) -> None:
        """Ingest text or URL content."""
        if not args.strip():
            print("Usage: ingest <text or URL>")
            return
        
        # Check if it's a URL
        if args.startswith(("http://", "https://")):
            print(f"\nFetching and ingesting URL: {args}")
            result = self.agent.fetch_url(args)
            if result.get("error"):
                print(f"Error: {result['error']}")
            else:
                print(f"✓ Ingested: {result.get('title', 'Untitled')}")
        else:
            # Ingest as text
            success = self.agent.ingest(args)
            if success:
                print("✓ Content ingested successfully")
            else:
                print("✗ Failed to ingest content")
    
    def cmd_search(self, args: str) -> None:
        """Search the web."""
        if not args.strip():
            print("Usage: search <query>")
            return
        
        print(f"\nSearching for: {args}")
        results = self.agent.search_web(args)
        
        if not results:
            print("No results found.")
            return
        
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['link']}")
            print(f"   {result['snippet']}\n")
    
    def cmd_fetch(self, args: str) -> None:
        """Fetch and display content from a URL."""
        if not args.strip():
            print("Usage: fetch <URL>")
            return
        
        if not args.startswith(("http://", "https://")):
            print("Please provide a valid URL starting with http:// or https://")
            return
        
        print(f"\nFetching: {args}")
        result = self.agent.fetch_url(args)
        
        if result.get("error"):
            print(f"Error: {result['error']}")
        else:
            print(f"\nTitle: {result.get('title', 'Untitled')}")
            print(f"URL: {result.get('url', args)}")
            
            content = result.get('content', '')
            if content:
                # Show first 500 characters
                preview = content[:500] + "..." if len(content) > 500 else content
                print(f"\nContent preview:\n{preview}")
                print(f"\n✓ Full content ingested ({len(content)} characters)")
    
    def cmd_help(self, args: str) -> None:
        """Show help information."""
        print("\n🧠 Ollama CLI Agent - Available Commands:\n")
        print("  ask <question>     - Ask a question (uses memory for context)")
        print("  ingest <text/URL>  - Ingest text or fetch & ingest a URL")
        print("  search <query>     - Search the web")
        print("  fetch <URL>        - Fetch and display content from a URL")
        print("  stats              - Show memory statistics")
        print("  help               - Show this help message")
        print("  exit/quit          - Exit the assistant\n")
    
    def cmd_stats(self, args: str) -> None:
        """Show memory statistics."""
        stats = self.agent.get_memory_stats()
        
        if stats.get("error"):
            print(f"Error getting stats: {stats['error']}")
        else:
            print("\n📊 Memory Statistics:\n")
            print(json.dumps(stats, indent=2))
    
    def cmd_exit(self, args: str) -> None:
        """Exit the assistant."""
        print("\nGoodbye! 👋")
        sys.exit(0)
    
    def run(self) -> None:
        """Run the interactive REPL."""
        print("\n🧠 Ollama CLI Agent")
        print("Type 'help' for available commands\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command and arguments
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                # Execute command
                if command in self.commands:
                    self.commands[command](args)
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n\nUse 'exit' to quit.")
            except Exception as e:
                logger.error(f"Error in REPL: {e}")
                print(f"Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Ollama CLI Agent")
    parser.add_argument(
        "--model",
        default="mistral:7b",
        help="Ollama model to use (default: mistral:7b)"
    )
    parser.add_argument(
        "--embedding-model",
        default="all-minilm",
        help="Embedding model to use (default: all-minilm)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.debug:
        setup_logger(level=logging.DEBUG)
    
    # Create and run assistant
    assistant = Assistant(model=args.model, embedding_model=args.embedding_model)
    assistant.run()


if __name__ == "__main__":
    main()