"""
Specialist agents for specific tasks
"""

from typing import Dict, Any
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_core.language_models.llms import LLM
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.agents import AgentExecutor

from tools.file_operations import read_file, write_file, list_files
from tools.web_browser import search_web
from browser_tool import BrowserTool
from core.thinking_log import AgentThinkingLog
from .prompts import get_agent_system_prompts, get_tool_error_handler


class ToolErrorHandler(BaseCallbackHandler):
	"""Callback handler to catch and handle tool errors"""
	def __init__(self, agent_name: str, error_handler):
		self.agent_name = agent_name
		self.error_handler = error_handler
		self.last_error = None
	
	def on_tool_error(self, error: Exception, **kwargs):
		"""Handle tool errors"""
		self.last_error = self.error_handler(str(error))
		return self.last_error


def create_agent_with_system_prompt(tools, llm, agent_type, memory, system_prompt, agent_name, thinking_log):
	"""Create an agent with a system prompt and error handling"""
	
	# Create error handler
	error_handler = get_tool_error_handler(agent_name)
	
	# Initialize the agent with system message
	agent = initialize_agent(
		tools=tools,
		llm=llm,
		agent=agent_type,
		memory=memory,
		verbose=True,
		handle_parsing_errors=True,
		max_iterations=5,
		early_stopping_method="generate"
	)
	
	# Add system prompt to the agent's prompt template
	if hasattr(agent, 'agent') and hasattr(agent.agent, 'llm_chain'):
		try:
			# Prepend system prompt to the agent's instructions
			if hasattr(agent.agent.llm_chain, 'prompt'):
				original_template = agent.agent.llm_chain.prompt.template
				agent.agent.llm_chain.prompt.template = f"{system_prompt}\n\n{original_template}"
		except:
			pass  # If we can't modify the prompt, continue anyway
	
	# Wrap the agent's step method to catch tool errors
	original_step = agent._take_next_step
	
	def wrapped_step(*args, **kwargs):
		try:
			result = original_step(*args, **kwargs)
			return result
		except Exception as e:
			error_msg = str(e)
			if "not found" in error_msg.lower() or "no tool" in error_msg.lower():
				handled_error = error_handler(error_msg)
				thinking_log.log(handled_error, "error")
				# Return a message about the missing tool
				return [{
					"action": "Final Answer",
					"action_input": handled_error
				}]
			raise
	
	agent._take_next_step = wrapped_step
	
	return agent


def create_specialist_agents(llm: LLM, thinking_log: AgentThinkingLog, browser_driver=None) -> Dict[str, Any]:
	"""Create specialized agents with thinking visualization and self-awareness"""
	agents = {}
	system_prompts = get_agent_system_prompts()
	
	# Browser Agent with Selenium
	if browser_driver:
		browser_tool = BrowserTool(driver=browser_driver)
		
		def log_navigate(url: str) -> str:
			thinking_log.log(f"Navigating to: {url}", "action")
			result = browser_tool.navigate_to(url)
			thinking_log.log(f"Navigation complete", "success")
			return result
		
		def log_extract(dummy_input: str = "") -> str:
			thinking_log.log("Extracting text from page", "action")
			result = browser_tool.get_page_text()
			thinking_log.log(f"Extracted {len(result)} characters", "info")
			return result
		
		def log_fill_form(data: str) -> str:
			thinking_log.log(f"Filling form with: {data}", "action")
			result = browser_tool.fill_form(data)
			thinking_log.log("Form filled", "success")
			return result
		
		def log_click(element: str) -> str:
			thinking_log.log(f"Clicking element: {element}", "action")
			result = browser_tool.click_element(element)
			thinking_log.log("Click successful", "success")
			return result
		
		browser_tools = [
			Tool(name="NavigateTo", func=log_navigate, description="Navigate to a URL. Input should be the URL to visit."),
			Tool(name="ExtractText", func=log_extract, description="Extract text from current page. Input can be empty string or anything."),
			Tool(name="FillForm", func=log_fill_form, description="Fill form fields. Input should be JSON like: {\"username\": \"myname\", \"password\": \"mypass\"}"),
			Tool(name="Click", func=log_click, description="Click an element. Input should be the link text or CSS selector.")
		]
		
		def log_screenshot(filename: str = "") -> str:
			thinking_log.log("Taking screenshot", "action")
			if filename:
				result = browser_tool.take_screenshot(filename)
			else:
				result = browser_tool.take_screenshot()
			thinking_log.log("Screenshot saved", "success")
			return result
		
		browser_tools.append(
			Tool(name="Screenshot", func=log_screenshot, description="Take a screenshot. Input is optional filename (leave empty for auto-generated name).")
		)
		
		agents["browser"] = create_agent_with_system_prompt(
			tools=browser_tools,
			llm=llm,
			agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
			memory=ConversationBufferMemory(memory_key="chat_history"),
			system_prompt=system_prompts["browser"],
			agent_name="browser",
			thinking_log=thinking_log
		)
	
	# File Agent
	def log_read_file(path: str) -> str:
		thinking_log.log(f"Reading file: {path}", "action")
		result = read_file(path)
		thinking_log.log(f"Read {len(result)} characters", "info")
		return result
	
	def log_write_file(data: str) -> str:
		parts = data.split('|', 1)
		if len(parts) != 2:
			return "Error: Use format 'filepath|content'"
		filepath, content = parts
		thinking_log.log(f"Writing to file: {filepath}", "action")
		result = write_file(data)
		thinking_log.log("Write complete", "success")
		return result
	
	def log_list_files(path: str) -> str:
		thinking_log.log(f"Listing files in: {path}", "action")
		result = list_files(path)
		file_count = len(result.split('\\n'))
		thinking_log.log(f"Found {file_count} items", "info")
		return result
	
	file_tools = [
		Tool(name="ReadFile", func=log_read_file, description="Read file contents. Input should be the file path."),
		Tool(name="WriteFile", func=log_write_file, description="Write content to a file. Input format: filepath|content to write"),
		Tool(name="ListFiles", func=log_list_files, description="List files in a directory. Input should be the directory path.")
	]
	
	agents["file"] = create_agent_with_system_prompt(
		tools=file_tools,
		llm=llm,
		agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
		memory=ConversationBufferMemory(memory_key="chat_history"),
		system_prompt=system_prompts["file"],
		agent_name="file",
		thinking_log=thinking_log
	)
	
	# Search Agent
	def log_search(query: str) -> str:
		thinking_log.log(f"Searching web for: {query}", "action")
		result = search_web(query)
		thinking_log.log("Search complete", "success")
		return result
	
	search_tools = [
		Tool(name="WebSearch", func=log_search, description="Search the web for information. Input should be your search query.")
	]
	
	agents["search"] = create_agent_with_system_prompt(
		tools=search_tools,
		llm=llm,
		agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
		memory=ConversationBufferMemory(memory_key="chat_history"),
		system_prompt=system_prompts["search"],
		agent_name="search",
		thinking_log=thinking_log
	)
	
	# Coder Agent
	def log_write_code(request: str) -> str:
		thinking_log.log(f"Writing code for: {request[:100]}...", "action")
		thinking_log.log("Analyzing requirements", "think")
		thinking_log.log("Generating code structure", "think")
		return f"I'll write the code for: {request}"
	
	coder_tools = [
		Tool(name="WriteCode", func=log_write_code, description="Generate code based on requirements. Input should describe what code you need.")
	]
	
	agents["coder"] = create_agent_with_system_prompt(
		tools=coder_tools,
		llm=llm,
		agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
		memory=ConversationBufferMemory(memory_key="chat_history"),
		system_prompt=system_prompts["coder"],
		agent_name="coder",
		thinking_log=thinking_log
	)
	
	# Casual Agent (conversation and summary) - No tools
	agents["casual"] = create_agent_with_system_prompt(
		tools=[],  # No tools for casual agent
		llm=llm,
		agent_type=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
		memory=ConversationBufferMemory(memory_key="chat_history"),
		system_prompt=system_prompts["casual"],
		agent_name="casual",
		thinking_log=thinking_log
	)
	
	return agents
