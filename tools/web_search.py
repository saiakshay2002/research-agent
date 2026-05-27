import os
from typing import List, Dict
from tavily import TavilyClient


class WebSearchTool:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not set in environment.")
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search the web and return structured results."""
        try:
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
            )
            return [
                {
                    "content": result.get("content", ""),
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "score": result.get("score", 0.0),
                }
                for result in response.get("results", [])
            ]
        except Exception as e:
            return [{"content": f"Web search error: {e}", "url": "error", "title": "Error", "score": 0.0}]
