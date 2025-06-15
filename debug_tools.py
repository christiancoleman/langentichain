"""
Debug tool errors and test agent functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain.agents import Tool
from langchain_core.language_models.llms import LLM
from typing import List

class DebugLLM(LLM):
    """Debug LLM that shows what's happening"""
    
    @property
    def _llm_type(self) -> str:
        return "debug"
    
    def _call(self, prompt: str, stop: List[str] = None, **kwargs) -> str:
        print("\n" + "="*50)
        print("LLM PROMPT:")
        print("="*50)
        print(prompt)
        print("="*50 + "\n")
        
        # Return a simple response based on the prompt
        if "FillForm" in prompt:
            return 'I need to fill a form. Let me use the FillForm tool.\n\nAction: FillForm\nAction Input: {"username": "test", "password": "test123"}'
        elif "NavigateTo" in prompt:
            return 'I need to navigate to a URL.\n\nAction: NavigateTo\nAction Input: https://example.com'
        elif "ExtractText" in prompt:
            return 'I need to extract text from the page.\n\nAction: ExtractText\nAction Input: extract'
        else:
            return "I understand. Let me help you with that."

# Test tool functions
def test_fill_form(data: str) -> str:
    print(f"\n[TOOL CALLED] FillForm with input: {repr(data)}")
    return f"Form filled with: {data}"

def test_navigate(url: str) -> str:
    print(f"\n[TOOL CALLED] NavigateTo with input: {repr(url)}")
    return f"Navigated to: {url}"

def test_extract(dummy: str = "") -> str:
    print(f"\n[TOOL CALLED] ExtractText with input: {repr(dummy)}")
    return "Extracted text from page"

# Create test tools
test_tools = [
    Tool(
        name="FillForm",
        func=test_fill_form,
        description="Fill form fields. Input should be JSON like: {\"username\": \"myname\", \"password\": \"mypass\"}"
    ),
    Tool(
        name="NavigateTo",
        func=test_navigate,
        description="Navigate to a URL. Input should be the URL to visit."
    ),
    Tool(
        name="ExtractText",
        func=test_extract,
        description="Extract text from current page. Input can be empty string or anything."
    )
]

# Test agent creation
print("🧪 Testing Tool Descriptions and Agent Behavior\n")

try:
    from langchain.agents import initialize_agent, AgentType
    from langchain.memory import ConversationBufferMemory
    
    # Create debug LLM
    llm = DebugLLM()
    
    # Create agent
    agent = initialize_agent(
        tools=test_tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=ConversationBufferMemory(memory_key="chat_history"),
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Test different queries
    test_queries = [
        "Navigate to google.com",
        "Fill the login form with username 'john' and password 'secret'",
        "Extract the text from this page"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"TEST QUERY: {query}")
        print('='*60)
        
        try:
            result = agent.invoke({"input": query})
            output = result.get('output', result)
            print(f"\nRESULT: {output}")
        except Exception as e:
            print(f"\nERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
except Exception as e:
    print(f"Failed to create agent: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Debug test complete!")

# Additional tips
print("\n💡 Tips:")
print("1. If you see 'Missing input keys', use invoke({'input': query})")
print("2. Tool descriptions should be clear about input format")
print("3. All tool functions must accept at least one parameter")
print("4. Check QUICK_REFERENCE.md for common patterns")
print("5. Run system_check.py to verify your setup")
