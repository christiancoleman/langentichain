"""
AgentRouter with keyword-based routing
Simplified version without ML dependencies
"""

import os
import time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AgentRouter:
	"""
	Simple keyword-based router for agent selection
	"""
	
	def __init__(self, agents: Dict[str, Any]):
		self.agents = agents
		self.thinking_log = []
	
	def log_thinking(self, message: str, level: str = "info"):
		"""Log agent thinking for UI visualization"""
		timestamp = time.strftime("%H:%M:%S")
		self.thinking_log.append({
			"timestamp": timestamp,
			"level": level,
			"message": message
		})
		logger.info(f"[{timestamp}] {message}")
	
	def get_thinking_log(self) -> List[Dict[str, str]]:
		"""Get the thinking log for UI display"""
		return self.thinking_log
	
	def clear_thinking_log(self):
		"""Clear the thinking log"""
		self.thinking_log = []
	
	def estimate_complexity(self, query: str) -> str:
		"""Estimate if a query is simple (LOW) or complex (HIGH)"""
		self.log_thinking(f"Estimating complexity for: '{query[:50]}...'", "analyze")
		
		query_lower = query.lower()
		
		# Complex task indicators
		complex_indicators = [
			" and then ",
			" after that ",
			" finally ",
			" first ",
			" second ",
			" next ",
			" create a report",
			" analyze ",
			" compare ",
			" build a ",
			" develop ",
			" research ",
			" find .* and .* and ",
			" multiple ",
			" comprehensive ",
			" detailed ",
			" full "
		]
		
		# Check for multiple actions
		action_words = ["search", "create", "write", "read", "find", "analyze", "build", "save", "extract"]
		action_count = sum(1 for word in action_words if word in query_lower)
		
		if action_count >= 2:
			self.log_thinking(f"Multiple actions detected ({action_count})", "info")
			return "HIGH"
		
		# Check for complex indicators
		for indicator in complex_indicators:
			if indicator in query_lower:
				self.log_thinking(f"Complex indicator found: '{indicator}'", "info")
				return "HIGH"
		
		# Check query length (longer queries tend to be more complex)
		if len(query.split()) > 20:
			self.log_thinking("Long query detected", "info")
			return "HIGH"
		
		self.log_thinking("Query appears simple", "result")
		return "LOW"
	
	def classify_task(self, query: str) -> str:
		"""Classify the task type based on keywords"""
		self.log_thinking(f"Classifying task type for: '{query[:50]}...'", "analyze")
		
		query_lower = query.lower()
		
		# Define keyword mappings
		task_keywords = {
			"browser": ["navigate", "click", "fill form", "website", "webpage", "url", "browser", "screenshot"],
			"coder": ["code", "script", "function", "debug", "program", "write a", "create a", "python", "javascript", "html"],
			"file": ["file", "folder", "directory", "read", "write", "save", "list files", "create a file"],
			"search": ["search", "find online", "web", "look up", "google", "research online", "what is", "weather"],
		}
		
		# Count keyword matches for each category
		scores = {}
		for task_type, keywords in task_keywords.items():
			score = sum(1 for keyword in keywords if keyword in query_lower)
			if score > 0:
				scores[task_type] = score
		
		# Return the task type with highest score
		if scores:
			task_type = max(scores, key=scores.get)
			self.log_thinking(f"Keyword matches: {scores} → Selected: {task_type}", "result")
			return task_type
		
		# Default to casual for conversation
		self.log_thinking("No clear task type, defaulting to casual", "info")
		return "casual"
	
	def route(self, query: str) -> str:
		"""Route query to appropriate agent"""
		self.clear_thinking_log()
		self.log_thinking(f"Routing query: '{query[:100]}...'", "start")
		
		# First, estimate complexity
		complexity = self.estimate_complexity(query)
		
		# For complex queries, always use planner
		if complexity == "HIGH":
			self.log_thinking("Complex query detected → Routing to Planner Agent", "decision")
			return "planner"
		
		# For simple queries, route to specific agent
		task_type = self.classify_task(query)
		
		# Map task types to agent names
		agent_mapping = {
			"browser": "browser",
			"coder": "coder", 
			"file": "file",
			"search": "search",
			"casual": "casual"
		}
		
		agent_name = agent_mapping.get(task_type, "casual")
		
		# Check if the agent exists (e.g., browser might not be available)
		if agent_name not in self.agents:
			self.log_thinking(f"{agent_name.title()} agent not available, using casual agent", "warning")
			agent_name = "casual"
		
		self.log_thinking(f"Simple query → Routing to {agent_name.title()} Agent", "decision")
		
		return agent_name
