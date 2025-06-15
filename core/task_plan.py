"""
Task planning structures and utilities
"""

from typing import List
from pydantic import BaseModel, Field


class TaskPlan(BaseModel):
    """Structure for a task plan"""
    agent: str = Field(description="The agent to execute this task")
    id: str = Field(description="Unique ID for this task")
    need: List[str] = Field(default_factory=list, description="IDs of tasks this depends on")
    task: str = Field(description="Detailed description of the task")
