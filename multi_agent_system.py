"""
Multi-Agent System with adaptive routing and thinking visualization
"""

import json
import re
from typing import Dict, List, Any
from langchain_core.language_models.llms import LLM
from langchain.schema import OutputParserException

# Import our refactored modules
from routing import AgentRouter
from core import AgentThinkingLog, TaskPlan
from agents import create_planner_prompt, create_specialist_agents
from browser_tool import create_browser_driver


class MultiAgentOrchestrator:
    """Main orchestrator for the multi-agent system"""
    
    def __init__(self, llm: LLM, browser_driver=None):
        self.llm = llm
        self.browser_driver = browser_driver
        self.thinking_log = AgentThinkingLog()
        self.agents = create_specialist_agents(llm, self.thinking_log, browser_driver)
        self.router = AgentRouter(self.agents)
        self.planner_prompt = create_planner_prompt()
        self.task_results = {}
    
    def get_thinking_logs(self) -> Dict[str, Any]:
        """Get all thinking logs for UI display"""
        return {
            "router": self.router.get_thinking_log(),
            "agents": self.thinking_log.get_logs()
        }
    
    def parse_plan(self, plan_text: str) -> List[TaskPlan]:
        """Parse the JSON plan from LLM output"""
        try:
            # Extract JSON from the response
            json_match = re.search(r'```json\s*(.*)\s*```', plan_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_str = plan_text
            
            plan_data = json.loads(json_str)
            tasks = []
            
            for task_dict in plan_data.get("plan", []):
                task = TaskPlan(
                    agent=task_dict["agent"].lower(),
                    id=task_dict["id"],
                    need=task_dict.get("need", []),
                    task=task_dict["task"]
                )
                tasks.append(task)
            
            return tasks
        except Exception as e:
            raise OutputParserException(f"Failed to parse plan: {str(e)}")
    
    def execute_task(self, task: TaskPlan) -> str:
        """Execute a single task with the appropriate agent"""
        agent_name = task.agent.lower()
        
        # Start logging for this agent
        self.thinking_log.start_agent(agent_name)
        self.thinking_log.log(f"Starting task: {task.task[:100]}...", "start")
        
        if agent_name not in self.agents:
            error_msg = f"Error: Unknown agent '{agent_name}'"
            self.thinking_log.log(error_msg, "error")
            return error_msg
        
        # Prepare context from dependencies
        if task.need:
            self.thinking_log.log(f"Gathering context from tasks: {task.need}", "info")
            context_parts = []
            for dep_id in task.need:
                if dep_id in self.task_results:
                    context_parts.append(f"Result from task {dep_id}: {self.task_results[dep_id]}")
            if context_parts:
                context = "Context from previous tasks:\n" + "\n".join(context_parts) + "\n\n"
                self.thinking_log.log("Context prepared", "info")
            else:
                context = ""
        else:
            context = ""
        
        # Execute the task
        full_prompt = context + task.task
        
        try:
            self.thinking_log.log("Executing task", "action")
            
            if agent_name == "coder":
                # Special handling for coder agent
                code_result = self.generate_code(full_prompt)
                self.thinking_log.log("Code generation complete", "success")
                return code_result
            else:
                result = self.agents[agent_name].invoke({"input": full_prompt})
                self.thinking_log.log("Task execution complete", "success")
                return result.get('output', str(result))
                
        except Exception as e:
            error_msg = f"Error executing task: {str(e)}"
            self.thinking_log.log(error_msg, "error")
            return error_msg
    
    def generate_code(self, prompt: str) -> str:
        """Generate code using the LLM directly"""
        self.thinking_log.log("Preparing code generation prompt", "think")
        
        code_prompt = f"""Write complete, working code for the following request:

{prompt}

Provide the full code implementation with detailed comments explaining each section."""
        
        self.thinking_log.log("Generating code with LLM", "action")
        response = self.llm._call(code_prompt)
        
        self.thinking_log.log("Code generation complete", "success")
        return response
    
    def execute_plan(self, tasks: List[TaskPlan]) -> str:
        """Execute all tasks in the plan"""
        results = []
        
        for task in tasks:
            print(f"\n📋 Executing Task {task.id}: {task.agent} agent")
            print(f"   Task: {task.task[:100]}...")
            
            result = self.execute_task(task)
            self.task_results[task.id] = result
            results.append(f"Task {task.id} ({task.agent}): {result}")
            
            print(f"   ✅ Completed")
        
        # Create final summary
        self.thinking_log.start_agent("summary")
        self.thinking_log.log("Creating final summary", "action")
        summary = "\n\n".join(results)
        self.thinking_log.log("Summary complete", "success")
        
        return summary
    
    def run(self, query: str) -> str:
        """Main entry point - route and execute the query"""
        # Clear previous logs
        self.thinking_log.clear()
        self.task_results = {}
        
        # Route the query
        route = self.router.route(query)
        
        if route == "planner":
            print("🧠 Complex task detected - creating execution plan...")
            
            # Log planner thinking
            self.thinking_log.start_agent("planner")
            self.thinking_log.log("Analyzing complex query", "think")
            self.thinking_log.log("Identifying required subtasks", "think")
            self.thinking_log.log("Determining task dependencies", "think")
            
            # Generate plan
            plan_response = self.llm._call(self.planner_prompt.format(input=query))
            
            try:
                self.thinking_log.log("Parsing execution plan", "action")
                tasks = self.parse_plan(plan_response)
                print(f"\n📋 Created plan with {len(tasks)} tasks")
                self.thinking_log.log(f"Plan created with {len(tasks)} tasks", "success")
                
                # Execute plan
                result = self.execute_plan(tasks)
                return result
                
            except OutputParserException as e:
                error_msg = f"Failed to create plan: {str(e)}"
                self.thinking_log.log(error_msg, "error")
                return error_msg
        
        else:
            # Simple task - route directly
            print(f"🎯 Simple task - routing to {route} agent")
            
            # Execute with single agent
            self.thinking_log.start_agent(route)
            self.thinking_log.log(f"Executing simple task", "start")
            
            result = self.agents[route].invoke({"input": query})
            return result.get('output', str(result))
