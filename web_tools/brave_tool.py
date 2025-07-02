"""Brave Search API tool for privacy-focused web search."""

import os
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

load_dotenv()


class BraveSearchTool:
    """Tool for searching the web using Brave Search API."""
    
    def __init__(self):
        self.api_key = os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY not found in environment variables")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web using Brave Search API.
        
        Args:
            query: Search query string
            num_results: Number of results to return (default: 5)
            
        Returns:
            List of search results with title, link, and snippet
        """
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        
        params = {
            "q": query,
            "count": num_results
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "web" in data and "results" in data["web"]:
                for result in data["web"]["results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("url", ""),
                        "snippet": result.get("description", ""),
                        "source": "brave"
                    })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching with Brave API: {e}")
            return []
    
    def __call__(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Make the tool callable."""
        return self.search(query, **kwargs)