"""
Example: How to add custom tools to LangEntiChain
This shows the pattern for extending the agent with new capabilities
"""

from langchain.agents import Tool

# Example 1: Simple Calculator Tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression
    Input: A mathematical expression as a string
    """
    try:
        # Only allow safe operations
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"

# Example 2: Weather API Tool (requires API key)
def get_weather(location: str) -> str:
    """
    Get current weather for a location
    Input: City name or coordinates
    """
    # This is a template - add your weather API
    api_key = "your-api-key"
    try:
        # Example with OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
        response = requests.get(url)
        data = response.json()
        
        temp_c = data['main']['temp'] - 273.15
        description = data['weather'][0]['description']
        
        return f"Weather in {location}: {temp_c:.1f}°C, {description}"
    except:
        return f"Weather data not available for {location}"

# Example 3: Database Query Tool
def query_database(query: str) -> str:
    """
    Execute a database query (example with SQLite)
    Input: SQL query string
    """
    import sqlite3
    
    try:
        # Connect to your database
        conn = sqlite3.connect('example.db')
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute(query)
        
        # Fetch results
        results = cursor.fetchall()
        conn.close()
        
        return f"Query results: {results}"
    except Exception as e:
        return f"Database error: {str(e)}"

# Example 4: API Integration Tool
def call_api(endpoint: str) -> str:
    """
    Make API calls to external services
    Input: API endpoint URL
    """
    try:
        response = requests.get(endpoint, timeout=10)
        return f"API Response: {response.json()}"
    except Exception as e:
        return f"API Error: {str(e)}"

# How to add these tools to your agent:
# 1. Import this file in main.py
# 2. Add to tools_list:

"""
# In main.py, after the existing tools:

if config.getboolean('TOOLS', 'enable_calculator', fallback=False):
    from tools.custom_tools import calculator
    tools_list.append(Tool(
        name="Calculator",
        func=calculator,
        description="Perform mathematical calculations. Input should be a mathematical expression."
    ))

if config.getboolean('TOOLS', 'enable_weather', fallback=False):
    from tools.custom_tools import get_weather
    tools_list.append(Tool(
        name="Weather",
        func=get_weather,
        description="Get current weather for a location. Input should be a city name."
    ))
"""

# Don't forget to add to config.ini:
"""
[TOOLS]
enable_calculator = true
enable_weather = true
enable_database = false
enable_api = true
"""
