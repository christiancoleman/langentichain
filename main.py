import configparser
import os
import warnings
from typing import Optional, Dict, Any
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.chat_models import ChatOllama
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from openai import OpenAI

# Import our modules
from agent_config import get_agent_config, get_react_prompt

# Suppress deprecation warnings for now
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Import tools based on config
tools_list = []

if config.getboolean('TOOLS', 'enable_web_search', fallback=True):
    from tools.web_browser import search_web
    tools_list.append(Tool(
        name="WebSearch", 
        func=search_web, 
        description="Search the web for current information. Use this when you need to find recent data, news, or facts. Input should be a search query string."
    ))

if config.getboolean('TOOLS', 'enable_file_operations', fallback=True):
    from tools.file_operations import read_file, write_file
    tools_list.append(Tool(
        name="ReadFile", 
        func=read_file, 
        description="Read the contents of a file. Input should be a file path as a string."
    ))
    tools_list.append(Tool(
        name="WriteFile", 
        func=write_file, 
        description="Write content to a file. Input format: 'filepath|content' where filepath is the target file and content is what to write."
    ))

if config.getboolean('TOOLS', 'enable_salesforce', fallback=False):
    from tools.salesforce import search_salesforce
    tools_list.append(Tool(
        name="SalesforceSearch", 
        func=search_salesforce, 
        description="Search Salesforce for data"
    ))


class LMStudioLLM(LLM):
    """Custom LLM class for LM Studio integration"""
    
    model: str
    base_url: str
    temperature: float = 0.7
    max_tokens: int = 4096
    
    def _call(
        self,
        prompt: str,
        stop: Optional[list] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> str:
        """Call LM Studio API"""
        client = OpenAI(
            base_url=f"{self.base_url}/v1",
            api_key="not-needed"  # LM Studio doesn't require an API key
        )
        
        # Clean up any thinking tags from the prompt
        prompt = self._clean_thinking_tags(prompt)
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop
        )
        
        # Clean up any thinking tags from the response
        response_text = response.choices[0].message.content
        return self._clean_thinking_tags(response_text)
    
    def _clean_thinking_tags(self, text: str) -> str:
        """Remove <think> tags and their content"""
        import re
        # Remove <think>...</think> tags and their content
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        return cleaned.strip()
    
    @property
    def _llm_type(self) -> str:
        return "lm_studio"


def get_llm():
    """Initialize LLM based on config"""
    provider = config.get('LLM', 'provider', fallback='ollama')
    
    if provider == 'ollama':
        model = config.get('LLM', 'ollama_model', fallback='deepseek-coder:33b')
        base_url = config.get('LLM', 'ollama_address', fallback='http://localhost:11434')
        return ChatOllama(
            model=model,
            base_url=base_url,
            temperature=config.getfloat('LLM', 'temperature', fallback=0.7)
        )
    
    elif provider == 'lm_studio':
        model = config.get('LLM', 'lm_studio_model')
        base_url = config.get('LLM', 'lm_studio_address', fallback='http://localhost:1234')
        return LMStudioLLM(
            model=model,
            base_url=base_url,
            temperature=config.getfloat('LLM', 'temperature', fallback=0.7),
            max_tokens=config.getint('LLM', 'max_tokens', fallback=4096)
        )
    
    else:
        raise ValueError(f"Unknown provider: {provider}")


def create_agent():
    """Create and configure the agent with proper settings"""
    llm = get_llm()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent_config = get_agent_config(config)
    
    # Create agent with custom configuration
    agent = initialize_agent(
        tools=tools_list,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        **agent_config  # Unpack all agent settings including max_iterations
    )
    
    return agent


# Initialize the agent
agent = create_agent()


def run_agent(user_input: str) -> str:
    """Run the agent with error handling using the new invoke method"""
    try:
        # Use invoke instead of run (addresses deprecation)
        result = agent.invoke({"input": user_input})
        
        # Extract the output from the result
        if isinstance(result, dict):
            return result.get('output', str(result))
        else:
            return str(result)
            
    except Exception as e:
        error_msg = str(e)
        
        # Check for specific error types
        if "iteration limit" in error_msg.lower():
            return f"The agent reached the maximum iteration limit. This might indicate the task is too complex or the tools aren't providing clear enough responses. Error: {error_msg}"
        elif "parsing" in error_msg.lower():
            return f"The agent had trouble understanding the tool responses. Error: {error_msg}"
        else:
            return f"Error: {error_msg}"


if __name__ == "__main__":
    # Test the agent
    print(f"Using {config.get('LLM', 'provider')} provider")
    print(f"Available tools: {[tool.name for tool in tools_list]}")
    print(f"Max iterations: {config.getint('AGENT', 'max_iterations', fallback=1000)}")
    
    test_input = "What LLM provider am I using?"
    print(f"\nTest query: {test_input}")
    print(f"Response: {run_agent(test_input)}")
