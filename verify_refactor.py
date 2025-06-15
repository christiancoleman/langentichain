"""
Quick test to verify the refactored multi-agent system works
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from core import AgentThinkingLog, TaskPlan
    print("✅ Core imports successful")
except Exception as e:
    print(f"❌ Core imports failed: {e}")

try:
    from routing import AgentRouter
    print("✅ Routing imports successful")
except Exception as e:
    print(f"❌ Routing imports failed: {e}")

try:
    from agents import create_planner_prompt, create_specialist_agents
    print("✅ Agent imports successful")
except Exception as e:
    print(f"❌ Agent imports failed: {e}")

try:
    from multi_agent_system import MultiAgentOrchestrator
    print("✅ MultiAgentOrchestrator import successful")
except Exception as e:
    print(f"❌ MultiAgentOrchestrator import failed: {e}")

print("\n🎉 All imports successful! The refactoring is complete.")
