import configparser
import os
from typing import Optional
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.chat_models import ChatOllama
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from openai import OpenAI

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
        description="Search the web for current information. Use this when you need to find recent data, news, or facts."
    ))

if config.getboolean('TOOLS', 'enable_file_operations', fallback=True):
    from tools.file_operations import read_file, write_file
    tools_list.append(Tool(
        name="ReadFile", 
        func=read_file, 
        description="Read the contents of a file. Provide the file path as input."
    ))
    tools_list.append(Tool(
        name="WriteFile", 
        func=write_file, 
        description="Write content to a file. Use format: 'filename.txt|content to write'"
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
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop
        )
        
        return response.choices[0].message.content
    
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


# Initialize components
llm = get_llm()
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=tools_list,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)

def run_agent(user_input):
    """Run the agent with error handling"""
    try:
        return agent.run(user_input)
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Test the agent
    print(f"Using {config.get('LLM', 'provider')} provider")
    print(f"Available tools: {[tool.name for tool in tools_list]}")
    
    test_input = "What LLM provider am I using?"
    print(f"\nTest query: {test_input}")
    print(f"Response: {run_agent(test_input)}")
