"""
AgentRouter with adaptive routing
Adapted from AgenticSeek's approach
"""

import os
import random
from typing import List, Dict, Any, Optional
from .adaptive_classifier import AdaptiveClassifier
import logging
import time

logger = logging.getLogger(__name__)


class AgentRouter:
    """
    AgentRouter using few-shot learning with DistilBERT embeddings
    Compatible with AgenticSeek's routing approach
    """
    
    def __init__(self, agents: Dict[str, Any], llm_router_path: str = "./llm_router"):
        self.agents = agents
        self.llm_router_path = llm_router_path
        
        # Initialize thinking log for UI first
        self.thinking_log = []
        
        # Initialize classifiers
        self.task_classifier = self.load_llm_router()
        self.complexity_classifier = self.load_llm_router()
        
        # Learn few-shot examples
        self.learn_few_shots_tasks()
        self.learn_few_shots_complexity()
    
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
    
    def load_llm_router(self) -> AdaptiveClassifier:
        """Load the LLM router model"""
        try:
            # First try to load from pretrained
            if os.path.exists(self.llm_router_path):
                self.log_thinking(f"Loading LLM router from {self.llm_router_path}", "status")
                return AdaptiveClassifier.from_pretrained(self.llm_router_path)
            else:
                # Create new classifier if path doesn't exist
                self.log_thinking("Creating new AdaptiveClassifier", "status")
                return AdaptiveClassifier()
        except Exception as e:
            logger.error(f"Failed to load router: {e}")
            self.log_thinking(f"Failed to load router, creating new one: {e}", "warning")
            return AdaptiveClassifier()
    
    def learn_few_shots_complexity(self):
        """Few shot learning for complexity estimation"""
        few_shots = [
            # Simple tasks
            ("hi", "LOW"),
            ("What's the weather like today?", "LOW"),
            ("Can you find a file named 'notes.txt'?", "LOW"),
            ("Write a Python function to reverse a string", "LOW"),
            ("Search the web for Python tutorials", "LOW"),
            ("Debug this JavaScript code", "LOW"),
            ("What's the capital of France?", "LOW"),
            ("Tell me a joke", "LOW"),
            ("Read the config.ini file", "LOW"),
            ("Create a simple hello world program", "LOW"),
            
            # Complex tasks
            ("Search for Python tutorials, find the best 3, and create a summary file", "HIGH"),
            ("Find recent research on AI and build a web app to display it", "HIGH"),
            ("Create a game in JavaScript and save it to a file", "HIGH"),
            ("Analyze my code files and create a documentation", "HIGH"),
            ("Search for weather APIs and build a weather app", "HIGH"),
            ("Find the latest news on AI and create a report", "HIGH"),
            ("Build a web scraper and save the data to a database", "HIGH"),
            ("Create a full-stack application with React and Flask", "HIGH"),
            ("Research machine learning frameworks and create a comparison", "HIGH"),
            ("Find job listings online and apply to relevant ones", "HIGH"),
        ]
        
        random.shuffle(few_shots)
        texts = [text for text, _ in few_shots]
        labels = [label for _, label in few_shots]
        self.complexity_classifier.add_examples(texts, labels)
        self.log_thinking(f"Learned {len(few_shots)} complexity examples", "status")
    
    def learn_few_shots_tasks(self):
        """Few shot learning for task classification"""
        few_shots = [
            # Casual/conversation tasks
            ("Hi, how are you?", "casual"),
            ("Tell me a joke", "casual"),
            ("What's your favorite movie?", "casual"),
            ("Thanks for your help", "casual"),
            ("Explain quantum physics", "casual"),
            
            # Web/search tasks
            ("Search the web for Python tutorials", "search"),
            ("Find information about machine learning", "search"),
            ("Look up the latest news on AI", "search"),
            ("Search for the weather forecast", "search"),
            ("Find recent posts about climate change", "search"),
            
            # Browser tasks
            ("Navigate to github.com", "browser"),
            ("Fill out the form on the website", "browser"),
            ("Click the submit button", "browser"),
            ("Extract text from the webpage", "browser"),
            ("Take a screenshot of the page", "browser"),
            
            # Code tasks
            ("Write a Python script to sort a list", "coder"),
            ("Debug this JavaScript code", "coder"),
            ("Create a function to calculate factorial", "coder"),
            ("Generate a Flask web application", "coder"),
            ("Write a bash script to backup files", "coder"),
            
            # File tasks
            ("Read the config.ini file", "file"),
            ("Write the results to output.txt", "file"),
            ("List all files in the directory", "file"),
            ("Find files with .py extension", "file"),
            ("Create a new folder called 'data'", "file"),
        ]
        
        random.shuffle(few_shots)
        texts = [text for text, _ in few_shots]
        labels = [label for _, label in few_shots]
        self.task_classifier.add_examples(texts, labels)
        self.log_thinking(f"Learned {len(few_shots)} task examples", "status")
    
    def estimate_complexity(self, query: str) -> str:
        """Estimate if a query is simple (LOW) or complex (HIGH)"""
        self.log_thinking(f"Estimating complexity for: '{query[:50]}...'", "analyze")
        
        predictions = self.complexity_classifier.predict(query)
        if not predictions:
            self.log_thinking("No complexity prediction, defaulting to LOW", "warning")
            return "LOW"
        
        complexity, confidence = predictions[0]
        self.log_thinking(f"Complexity: {complexity} (confidence: {confidence:.2f})", "result")
        
        # If low confidence, err on the side of HIGH complexity
        if confidence < 0.3:
            self.log_thinking("Low confidence, treating as HIGH complexity", "warning")
            return "HIGH"
        
        return complexity
    
    def classify_task(self, query: str) -> str:
        """Classify the task type"""
        self.log_thinking(f"Classifying task type for: '{query[:50]}...'", "analyze")
        
        # Quick checks for obvious patterns
        query_lower = query.lower()
        
        # Browser-specific keywords
        if any(kw in query_lower for kw in ["navigate", "click", "fill form", "website", "webpage"]):
            self.log_thinking("Detected browser keywords", "info")
            return "browser"
        
        # Code-specific keywords
        elif any(kw in query_lower for kw in ["code", "script", "function", "debug", "program"]):
            self.log_thinking("Detected coding keywords", "info")
            return "coder"
        
        # File-specific keywords
        elif any(kw in query_lower for kw in ["file", "folder", "directory", "read", "write", "save"]):
            self.log_thinking("Detected file operation keywords", "info")
            return "file"
        
        # Web search keywords
        elif any(kw in query_lower for kw in ["search", "find online", "web", "look up"]):
            self.log_thinking("Detected web search keywords", "info")
            return "search"
        
        # Use classifier for ambiguous cases
        predictions = self.task_classifier.predict(query)
        if predictions:
            task_type, confidence = predictions[0]
            self.log_thinking(f"Classifier prediction: {task_type} (confidence: {confidence:.2f})", "result")
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
        self.log_thinking(f"Simple query → Routing to {agent_name.title()} Agent", "decision")
        
        return agent_name
    
    def save_model(self):
        """Save the trained classifiers"""
        os.makedirs(self.llm_router_path, exist_ok=True)
        
        # Save task classifier
        task_path = os.path.join(self.llm_router_path, "task_classifier")
        self.task_classifier.save(task_path)
        
        # Save complexity classifier  
        complexity_path = os.path.join(self.llm_router_path, "complexity_classifier")
        self.complexity_classifier.save(complexity_path)
        
        self.log_thinking(f"Saved classifiers to {self.llm_router_path}", "status")
