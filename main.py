"""
LangEntiChain - Multi-Agent System with Adaptive Routing
"""

import os
import configparser
from typing import List
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain.agents import Tool
from multi_agent_system import MultiAgentOrchestrator
from browser_tool import create_browser_driver

# Import tools
from tools.file_operations import read_file, write_file, list_files
from tools.web_browser import search_web

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Tool definitions for reference
tools_list = [
	Tool(
		name="WebSearch",
		func=search_web,
		description="Search the web for information. Input: search query"
	),
	Tool(
		name="ReadFile",
		func=read_file,
		description="Read the contents of a file. Input: file path"
	),
	Tool(
		name="WriteFile",
		func=write_file,
		description="Write content to a file. Input: 'filepath|content'"
	),
	Tool(
		name="ListFiles",
		func=list_files,
		description="List files in a directory. Input: directory path"
	)
]


class CustomLLM(LLM):
	"""Custom LLM wrapper for Ollama or LM Studio"""
	
	@property
	def _llm_type(self) -> str:
		return "custom"
	
	def _call(
		self,
		prompt: str,
		stop: List[str] = None,
		run_manager: CallbackManagerForLLMRun = None,
	) -> str:
		provider = config.get('LLM', 'provider', fallback='ollama')
		
		if provider == 'ollama':
			return self._call_ollama(prompt)
		elif provider == 'lm_studio':
			return self._call_lm_studio(prompt)
		else:
			raise ValueError(f"Unknown provider: {provider}")
	
	def _call_ollama(self, prompt: str) -> str:
		import requests
		
		address = config.get('LLM', 'ollama_address', fallback='http://localhost:11434')
		model = config.get('LLM', 'ollama_model', fallback='deepseek-coder:33b')
		
		try:
			response = requests.post(
				f"{address}/api/generate",
				json={
					"model": model,
					"prompt": prompt,
					"stream": False,
					"temperature": config.getfloat('LLM', 'temperature', fallback=0.7),
					"max_tokens": config.getint('LLM', 'max_tokens', fallback=4096)
				}
			)
			response.raise_for_status()
			return response.json()['response']
		except Exception as e:
			print(f"Ollama error: {e}")
			return f"Error calling Ollama: {str(e)}"
	
	def _call_lm_studio(self, prompt: str) -> str:
		import requests
		
		address = config.get('LLM', 'lm_studio_address', fallback='http://localhost:1234')
		
		try:
			response = requests.post(
				f"{address}/v1/completions",
				json={
					"prompt": prompt,
					"temperature": config.getfloat('LLM', 'temperature', fallback=0.7),
					"max_tokens": config.getint('LLM', 'max_tokens', fallback=4096),
					"stream": False
				}
			)
			response.raise_for_status()
			return response.json()['choices'][0]['text']
		except Exception as e:
			print(f"LM Studio error: {e}")
			return f"Error calling LM Studio: {str(e)}"


def get_llm():
	"""Get the configured LLM instance"""
	return CustomLLM()


# Global agent instance
agent = None
orchestrator = None


def initialize_agent():
	"""Initialize the multi-agent orchestrator"""
	global agent, orchestrator
	
	print("🚀 Initializing Multi-Agent System...")
	
	# Get LLM
	llm = get_llm()
	
	# Create browser driver if enabled
	browser_driver = None
	if config.getboolean('TOOLS', 'enable_browser', fallback=True):
		try:
			# Get headless setting from config
			headless = config.getboolean('BROWSER', 'headless', fallback=False)
			browser_driver = create_browser_driver(headless=headless)
			print("✅ Browser automation enabled")
		except Exception as e:
			print(f"⚠️ Browser automation disabled: {e}")
	
	# Create orchestrator
	orchestrator = MultiAgentOrchestrator(llm, browser_driver)
	agent = orchestrator
	
	print("✅ Multi-Agent System ready!")
	print("   - Planner Agent: Handles complex multi-step tasks")
	print("   - Browser Agent: Web automation and navigation")
	print("   - Coder Agent: Code generation and debugging")
	print("   - File Agent: File system operations")
	print("   - Search Agent: Web search capabilities")
	print("   - Casual Agent: Conversation and summaries")


def run_agent(query: str) -> str:
	"""Run the agent with a query"""
	global agent
	
	if agent is None:
		initialize_agent()
	
	try:
		result = agent.run(query)
		return result
	except Exception as e:
		return f"Error: {str(e)}"


def get_thinking_logs():
	"""Get thinking logs from the orchestrator"""
	global orchestrator
	
	if orchestrator is not None:
		return orchestrator.get_thinking_logs()
	return {"router": [], "agents": {}}


# Auto-initialize on import
if __name__ != "__main__":
	initialize_agent()


# CLI interface
if __name__ == "__main__":
	print("🤖 LangEntiChain - Multi-Agent CLI")
	print("Type 'quit' to exit")
	print()
	
	while True:
		query = input("You: ").strip()
		
		if query.lower() in ['quit', 'exit', 'q']:
			break
		
		if not query:
			continue
		
		print("\nAgent: ", end="", flush=True)
		response = run_agent(query)
		print(response)
		print()
