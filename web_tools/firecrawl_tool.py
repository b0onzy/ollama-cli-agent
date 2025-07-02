"""FireCrawl tool for full-page web scraping."""

import os
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()


class FireCrawlTool:
    """Tool for scraping web pages using FireCrawl API."""
    
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
        self.base_url = "https://api.firecrawl.dev/v0"
    
    def scrape(self, url: str, include_markdown: bool = True) -> Dict[str, Any]:
        """Scrape a web page using FireCrawl API.
        
        Args:
            url: URL to scrape
            include_markdown: Whether to include markdown content (default: True)
            
        Returns:
            Dictionary with scraped content including title, text, and metadata
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url,
            "pageOptions": {
                "includeMarkdown": include_markdown,
                "includeHtml": False,
                "onlyMainContent": True
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/scrape",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if "data" in data:
                result = data["data"]
                return {
                    "url": url,
                    "title": result.get("metadata", {}).get("title", ""),
                    "description": result.get("metadata", {}).get("description", ""),
                    "content": result.get("markdown", result.get("content", "")),
                    "metadata": result.get("metadata", {}),
                    "source": "firecrawl"
                }
            
            return {"url": url, "error": "No data returned", "source": "firecrawl"}
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping with FireCrawl: {e}")
            return {"url": url, "error": str(e), "source": "firecrawl"}
    
    def __call__(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make the tool callable."""
        return self.scrape(url, **kwargs)