"""SerpAPI tool for web search functionality."""

import os
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()


class SerpAPITool:
    """Tool for searching the web using SerpAPI."""
    
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not found in environment variables")
        self.base_url = "https://serpapi.com/search"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web using SerpAPI.
        
        Args:
            query: Search query string
            num_results: Number of results to return (default: 5)
            
        Returns:
            List of search results with title, link, and snippet
        """
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": num_results
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "organic_results" in data:
                for result in data["organic_results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": "serpapi"
                    })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching with SerpAPI: {e}")
            return []
    
    def __call__(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Make the tool callable."""
        return self.search(query, **kwargs)