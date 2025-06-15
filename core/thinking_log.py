"""
Thinking log management for agent visualization
"""

import time
from typing import Dict, List


class AgentThinkingLog:
    """Manages thinking logs for all agents"""
    def __init__(self):
        self.logs = {}
        self.current_agent = None
    
    def start_agent(self, agent_name: str):
        """Start logging for an agent"""
        self.current_agent = agent_name
        if agent_name not in self.logs:
            self.logs[agent_name] = []
    
    def log(self, message: str, level: str = "info"):
        """Log a thinking step"""
        if self.current_agent:
            timestamp = time.strftime("%H:%M:%S")
            self.logs[self.current_agent].append({
                "timestamp": timestamp,
                "level": level,
                "message": message
            })
    
    def get_logs(self) -> Dict[str, List[Dict]]:
        """Get all thinking logs"""
        return self.logs
    
    def clear(self):
        """Clear all logs"""
        self.logs = {}
        self.current_agent = None
