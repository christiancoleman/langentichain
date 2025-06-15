# Agent Configuration Module
"""Configuration for LangChain agents and tools"""

from typing import Dict, Any

def get_agent_config(config) -> Dict[str, Any]:
    """Get agent configuration from config file"""
    return {
        "max_iterations": config.getint('AGENT', 'max_iterations', fallback=1000),
        "max_execution_time": config.getfloat('AGENT', 'max_execution_time', fallback=3600),  # 1 hour default
        "handle_parsing_errors": config.getboolean('AGENT', 'handle_parsing_errors', fallback=True),
        "verbose": config.getboolean('AGENT', 'verbose', fallback=True),
        "return_intermediate_steps": config.getboolean('AGENT', 'return_intermediate_steps', fallback=False),
    }

def get_react_prompt():
    """Custom ReAct prompt to improve agent behavior"""
    return """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
