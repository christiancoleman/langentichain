import requests
from urllib.parse import quote
import json
from datetime import datetime
import re

def search_web(query: str) -> str:
	"""
	Perform a web search and return structured results
	Enhanced to handle crypto prices and other common queries
	"""
	try:
		# Check if this is a crypto price query
		crypto_query = _check_crypto_query(query)
		if crypto_query:
			return _get_crypto_prices(crypto_query)
		
		# Otherwise use DuckDuckGo for general search
		encoded_query = quote(query)
		url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"
		
		response = requests.get(url, timeout=10)
		data = response.json()
		
		print("Web search response: {data}")  # Debugging line
		
		results = []
		
		# Get instant answer if available
		if data.get('Answer'):
			results.append(f"Direct Answer: {data['Answer']}")
		
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
			for i, topic in enumerate(data['RelatedTopics'][:3], 1):
				if isinstance(topic, dict) and 'Text' in topic:
					results.append(f"{i}. {topic['Text']}")
		
		if results:
			return "\n".join(results)
		else:
			# Return a more helpful message
			return f"Search completed for '{query}'. No direct results found. The query may require specialized data sources or real-time information."
			
	except Exception as e:
		return f"Error performing web search: {str(e)}"


def _check_crypto_query(query: str) -> list:
	"""Check if query is about cryptocurrency prices"""
	query_lower = query.lower()
	crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency']
	price_keywords = ['price', 'cost', 'value', 'worth', 'usd', 'dollar']
	
	has_crypto = any(keyword in query_lower for keyword in crypto_keywords)
	has_price = any(keyword in query_lower for keyword in price_keywords)
	
	if has_crypto and has_price:
		cryptos = []
		if 'bitcoin' in query_lower or 'btc' in query_lower:
			cryptos.append('bitcoin')
		if 'ethereum' in query_lower or 'eth' in query_lower:
			cryptos.append('ethereum')
		return cryptos if cryptos else ['bitcoin', 'ethereum']  # Default to both
	return None


def _get_crypto_prices(cryptos: list) -> str:
	"""Get simulated crypto prices (in real app, use actual API)"""
	# In a real implementation, you'd use CoinGecko or similar API
	# For now, return sample data that looks realistic
	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
	
	# Simulated prices (in production, fetch from real API)
	prices = {
		'bitcoin': {
			'price': 67543.21,
			'change_24h': 2.34,
			'symbol': 'BTC'
		},
		'ethereum': {
			'price': 3456.78,
			'change_24h': -1.23,
			'symbol': 'ETH'
		}
	}
	
	result = [f"Cryptocurrency Prices (as of {timestamp}):"]
	result.append("=" * 50)
	
	for crypto in cryptos:
		if crypto in prices:
			info = prices[crypto]
			change_symbol = "↑" if info['change_24h'] > 0 else "↓"
			result.append(
				f"\n{crypto.capitalize()} ({info['symbol']}):\n"
				f"  Price: ${info['price']:,.2f} USD\n"
				f"  24h Change: {change_symbol} {abs(info['change_24h']):.2f}% ({info['change_24h']:+.2f}%)"
			)
	
	result.append("\n" + "=" * 50)
	result.append("Note: These are simulated prices. For real-time data, integrate a cryptocurrency API.")
	
	return "\n".join(result)


def browse_web(query: str) -> str:
	"""Legacy function name - redirects to search_web"""
	return search_web(query)
