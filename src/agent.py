"""Agent orchestration for ollama-cli-agent."""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.schema import Document

from src.qdrant_store import QdrantStore
from web_tools import SerpAPITool, BraveSearchTool, FireCrawlTool
from utils.logging import logger


class Agent:
    """Main agent class that orchestrates LLM, tools, and memory."""
    
    def __init__(
        self,
        model_name: str = "mistral:7b",
        embedding_model: str = "all-minilm",
        collection_name: str = "ollama_cli_agent"
    ):
        """Initialize the agent with LLM, tools, and memory.
        
        Args:
            model_name: Ollama model to use for generation
            embedding_model: Ollama model to use for embeddings
            collection_name: Qdrant collection name
        """
        # Initialize LLM
        self.llm = OllamaLLM(model=model_name)
        logger.info(f"Initialized Ollama LLM with model: {model_name}")
        
        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        logger.info(f"Initialized Ollama embeddings with model: {embedding_model}")
        
        # Initialize vector store
        self.memory = QdrantStore(
            collection_name=collection_name,
            use_memory_mode=True  # Use in-memory mode for development
        )
        logger.info(f"Initialized Qdrant memory with collection: {collection_name}")
        
        # Initialize tools
        self.tools = self._initialize_tools()
        logger.info(f"Initialized {len(self.tools)} tools")
    
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using Ollama embeddings."""
        embeddings = []
        for text in texts:
            embedding = self.embeddings.embed_query(text)
            embeddings.append(embedding)
        return embeddings
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize available tools."""
        tools = {}
        
        # Initialize SerpAPI if key is available
        if os.getenv("SERPAPI_API_KEY"):
            try:
                tools["serpapi"] = SerpAPITool()
                logger.info("Initialized SerpAPI tool")
            except Exception as e:
                logger.warning(f"Failed to initialize SerpAPI: {e}")
        
        # Initialize Brave Search if key is available
        if os.getenv("BRAVE_API_KEY"):
            try:
                tools["brave"] = BraveSearchTool()
                logger.info("Initialized Brave Search tool")
            except Exception as e:
                logger.warning(f"Failed to initialize Brave Search: {e}")
        
        # Initialize FireCrawl if key is available
        if os.getenv("FIRECRAWL_API_KEY"):
            try:
                tools["firecrawl"] = FireCrawlTool()
                logger.info("Initialized FireCrawl tool")
            except Exception as e:
                logger.warning(f"Failed to initialize FireCrawl: {e}")
        
        return tools
    
    def ingest(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Ingest content into memory.
        
        Args:
            content: Text content to ingest
            metadata: Optional metadata for the content
            
        Returns:
            Success status
        """
        try:
            if metadata is None:
                metadata = {}
            
            # Add timestamp
            metadata["ingested_at"] = datetime.now().isoformat()
            
            # Generate embeddings
            embeddings = self._embed_texts([content])
            
            # Add to memory with embeddings
            self.memory.add_documents(
                texts=[content],
                embeddings=embeddings,
                metadatas=[metadata]
            )
            logger.info(f"Ingested content: {len(content)} characters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest content: {e}")
            return False
    
    def search_web(self, query: str, tool: str = "auto") -> List[Dict[str, Any]]:
        """Search the web using available tools.
        
        Args:
            query: Search query
            tool: Tool to use ("serpapi", "brave", or "auto")
            
        Returns:
            List of search results
        """
        results = []
        
        if tool == "auto":
            # Try available tools in order
            for tool_name in ["serpapi", "brave"]:
                if tool_name in self.tools:
                    try:
                        results = self.tools[tool_name](query)
                        if results:
                            logger.info(f"Found {len(results)} results using {tool_name}")
                            break
                    except Exception as e:
                        logger.warning(f"Error using {tool_name}: {e}")
        else:
            # Use specific tool
            if tool in self.tools:
                try:
                    results = self.tools[tool](query)
                    logger.info(f"Found {len(results)} results using {tool}")
                except Exception as e:
                    logger.error(f"Error using {tool}: {e}")
            else:
                logger.warning(f"Tool {tool} not available")
        
        return results
    
    def fetch_url(self, url: str) -> Dict[str, Any]:
        """Fetch and scrape content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Scraped content dictionary
        """
        if "firecrawl" in self.tools:
            try:
                result = self.tools["firecrawl"](url)
                logger.info(f"Fetched content from {url}")
                
                # Auto-ingest if successful
                if "content" in result and not result.get("error"):
                    metadata = {
                        "source": "firecrawl",
                        "url": url,
                        "title": result.get("title", "")
                    }
                    self.ingest(result["content"], metadata)
                
                return result
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return {"url": url, "error": str(e)}
        else:
            logger.warning("FireCrawl tool not available")
            return {"url": url, "error": "FireCrawl not configured"}
    
    def ask(self, question: str, use_memory: bool = True) -> str:
        """Ask a question to the agent.
        
        Args:
            question: Question to ask
            use_memory: Whether to use memory for context
            
        Returns:
            Agent's response
        """
        try:
            context = ""
            
            if use_memory:
                # Search memory for relevant context
                query_embedding = self.embeddings.embed_query(question)
                relevant_docs = self.memory.search(
                    query_embedding=query_embedding,
                    limit=3
                )
                if relevant_docs:
                    context_parts = []
                    for doc in relevant_docs:
                        context_parts.append(doc["text"])
                    context = "\n\n".join(context_parts)
                    logger.info(f"Found {len(relevant_docs)} relevant documents in memory")
            
            # Build prompt
            if context:
                prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""
            else:
                prompt = f"Question: {question}\n\nAnswer:"
            
            # Generate response
            response = self.llm.invoke(prompt)
            logger.info(f"Generated response: {len(response)} characters")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory store."""
        try:
            info = self.memory.get_collection_info()
            return info
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}