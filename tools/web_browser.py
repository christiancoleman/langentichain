import requests
from urllib.parse import quote
import json

def search_web(query: str) -> str:
    """
    Perform a web search using DuckDuckGo's instant answer API
    This is a simple implementation - you can enhance with other APIs
    """
    try:
        # Using DuckDuckGo's instant answer API (no key required)
        encoded_query = quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        results = []
        
        # Get instant answer if available
        if data.get('Answer'):
            results.append(f"Answer: {data['Answer']}")
        
        # Get abstract if available
        if data.get('Abstract'):
            results.append(f"Summary: {data['Abstract']}")
            if data.get('AbstractURL'):
                results.append(f"Source: {data['AbstractURL']}")
        
        # Get definition if available
        if data.get('Definition'):
            results.append(f"Definition: {data['Definition']}")
            if data.get('DefinitionURL'):
                results.append(f"Source: {data['DefinitionURL']}")
        
        # Get related topics
        if data.get('RelatedTopics'):
            results.append("\nRelated information:")
            for topic in data['RelatedTopics'][:3]:  # Limit to 3 topics
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append(f"- {topic['Text']}")
        
        if results:
            return "\n".join(results)
        else:
            # Fallback message if no structured data
            return f"Web search completed for '{query}'. For real-time data like cryptocurrency prices, please note that DuckDuckGo's instant API may not provide live market data. Consider using a dedicated financial API for accurate pricing."
            
    except Exception as e:
        return f"Error performing web search: {str(e)}"


def browse_web(query: str) -> str:
    """Legacy function name - redirects to search_web"""
    return search_web(query)
