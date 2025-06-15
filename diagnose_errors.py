"""
Error Diagnosis Helper for LangChain
Helps understand and fix common LangChain errors
"""

import re
from typing import Dict, List, Tuple

class ErrorDiagnoser:
    """Diagnose and suggest fixes for LangChain errors"""
    
    def __init__(self):
        self.error_patterns = {
            # Pattern: (regex, explanation, fixes)
            r"Missing some input keys: \{'(\w+)'\}": (
                "Input Format Error",
                "The agent expects input in dictionary format with specific keys",
                [
                    "Use agent.invoke({'input': your_query}) instead of agent.run(query)",
                    "Check if your input matches the expected format",
                    "For tools, ensure descriptions don't contain literal JSON examples"
                ]
            ),
            r"The method `(\w+)` was deprecated": (
                "Deprecation Warning",
                "You're using an old API that will be removed in future versions",
                [
                    "Replace .run() with .invoke({'input': query})",
                    "Replace Chain() with newer patterns",
                    "Consider migrating to LangGraph for complex workflows"
                ]
            ),
            r"Tool named (\w+) not found": (
                "Missing Tool Error",
                "The agent is trying to use a tool that doesn't exist",
                [
                    "Check tool name spelling in your tool list",
                    "Ensure all tools are properly registered",
                    "Verify tool descriptions match actual tool names"
                ]
            ),
            r"Error parsing LLM output": (
                "LLM Output Parse Error",
                "The LLM's response couldn't be parsed into expected format",
                [
                    "Check if your LLM supports the agent format",
                    "Try increasing temperature for more varied responses",
                    "Use handle_parsing_errors=True in agent init",
                    "Consider using a different agent type"
                ]
            ),
            r"maximum context length": (
                "Context Length Error",
                "The prompt is too long for the model",
                [
                    "Reduce max_tokens in config",
                    "Use ConversationSummaryMemory instead of BufferMemory",
                    "Clear conversation history periodically",
                    "Use a model with larger context window"
                ]
            )
        }
    
    def diagnose(self, error_text: str) -> List[Tuple[str, str, List[str]]]:
        """Diagnose error and return explanations and fixes"""
        diagnoses = []
        
        for pattern, (error_type, explanation, fixes) in self.error_patterns.items():
            if re.search(pattern, error_text):
                diagnoses.append((error_type, explanation, fixes))
        
        return diagnoses
    
    def format_diagnosis(self, error_text: str) -> str:
        """Format diagnosis in readable way"""
        diagnoses = self.diagnose(error_text)
        
        if not diagnoses:
            return "❓ Unknown error type. Please check the full stack trace."
        
        output = []
        for error_type, explanation, fixes in diagnoses:
            output.append(f"🔍 {error_type}")
            output.append(f"   {explanation}")
            output.append("   Fixes:")
            for fix in fixes:
                output.append(f"   • {fix}")
            output.append("")
        
        return "\n".join(output)


def analyze_error_from_file(filepath: str):
    """Analyze error from a file"""
    try:
        with open(filepath, 'r') as f:
            error_text = f.read()
        
        diagnoser = ErrorDiagnoser()
        print("🩺 Error Diagnosis Report")
        print("=" * 60)
        print(diagnoser.format_diagnosis(error_text))
        
    except FileNotFoundError:
        print(f"Error: Could not find file {filepath}")
    except Exception as e:
        print(f"Error reading file: {e}")


def quick_fix_guide():
    """Print quick fix guide for common issues"""
    print("\n🚀 Quick Fix Guide")
    print("=" * 60)
    
    fixes = {
        "Missing input keys": """
# OLD (wrong)
result = agent.run("Do something")

# NEW (correct)
result = agent.invoke({"input": "Do something"})
output = result.get('output', result)
""",
        
        "Tool descriptions": """
# OLD (confusing)
Tool(name="Fill", description="Fill form: {'field': 'value'}")

# NEW (clear)
Tool(name="Fill", description="Fill form. Input: JSON format")
""",
        
        "Memory setup": """
# Correct memory initialization
memory = ConversationBufferMemory(
    memory_key="chat_history",  # Must match prompt
    return_messages=True        # For chat models
)
""",
        
        "Agent types": """
# Different agent types for different needs
ZERO_SHOT_REACT_DESCRIPTION          # Simple, general
STRUCTURED_CHAT_ZERO_SHOT_REACT      # JSON tool calling
CONVERSATIONAL_REACT_DESCRIPTION     # With memory
OPENAI_FUNCTIONS                     # OpenAI function calling
"""
    }
    
    for issue, code in fixes.items():
        print(f"\n📌 {issue}:")
        print(code)


if __name__ == "__main__":
    import sys
    
    # Example: Analyze the error from your paste
    sample_error = """
ValueError: Missing some input keys: {'input'}
    File "debug_tools.py", line 102, in <module>
        result = agent.run(query)
    """
    
    print("Analyzing sample error...")
    diagnoser = ErrorDiagnoser()
    print(diagnoser.format_diagnosis(sample_error))
    
    # Show quick fixes
    quick_fix_guide()
    
    # If file path provided, analyze that
    if len(sys.argv) > 1:
        print(f"\n\nAnalyzing error from file: {sys.argv[1]}")
        analyze_error_from_file(sys.argv[1])
