import streamlit as st
import configparser
from main import run_agent, config, tools_list, get_thinking_logs
import re
import json

# Page config
st.set_page_config(
    page_title="LangEntiChain - Multi-Agent System", 
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for better styling and thinking visualization
st.markdown("""
<style>
    /* Base styles */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0e1117;
        }
        
        .thinking-log {
            background-color: #1a1b26 !important;
            border-color: #2d2e3f !important;
        }
        
        .log-entry {
            background-color: #262730 !important;
        }
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    /* Thinking visualization styles */
    .thinking-log {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .log-entry {
        background-color: white;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.875rem;
    }
    
    .log-timestamp {
        color: #6c757d;
        font-weight: bold;
    }
    
    .log-level-info { color: #0066cc; }
    .log-level-action { color: #28a745; }
    .log-level-think { color: #6f42c1; }
    .log-level-success { color: #28a745; font-weight: bold; }
    .log-level-error { color: #dc3545; font-weight: bold; }
    .log-level-warning { color: #ffc107; }
    .log-level-start { color: #17a2b8; font-weight: bold; }
    .log-level-decision { color: #e83e8c; font-weight: bold; }
    .log-level-analyze { color: #fd7e14; }
    .log-level-result { color: #20c997; }
    
    .agent-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem 0;
        font-size: 0.875rem;
    }
    
    .config-info {
        background-color: rgba(102, 126, 234, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Thinking display functions
def format_log_entry(entry):
    """Format a single log entry"""
    timestamp = entry.get("timestamp", "")
    level = entry.get("level", "info")
    message = entry.get("message", "")
    
    return f'<div class="log-entry"><span class="log-timestamp">{timestamp}</span> <span class="log-level-{level}">[{level.upper()}]</span> {message}</div>'

def display_thinking_logs(logs):
    """Display thinking logs in a formatted way"""
    # Router logs
    if "router" in logs and logs["router"]:
        st.markdown('<div class="agent-indicator">🧭 Router</div>', unsafe_allow_html=True)
        router_html = '<div class="thinking-log">'
        for entry in logs["router"]:
            router_html += format_log_entry(entry)
        router_html += '</div>'
        st.markdown(router_html, unsafe_allow_html=True)
    
    # Agent logs
    if "agents" in logs and logs["agents"]:
        for agent_name, agent_logs in logs["agents"].items():
            if agent_logs:
                agent_emoji = {
                    "planner": "🧠",
                    "browser": "🌐",
                    "coder": "💻",
                    "file": "📁",
                    "search": "🔍",
                    "casual": "💬",
                    "summary": "📋"
                }.get(agent_name, "🤖")
                
                st.markdown(f'<div class="agent-indicator">{agent_emoji} {agent_name.title()} Agent</div>', unsafe_allow_html=True)
                agent_html = '<div class="thinking-log">'
                for entry in agent_logs:
                    agent_html += format_log_entry(entry)
                agent_html += '</div>'
                st.markdown(agent_html, unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🧠 LangEntiChain</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #6b7280;">Multi-Agent System with Adaptive Routing</p>', unsafe_allow_html=True)

# Layout with sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Show current provider
    provider = config.get('LLM', 'provider', fallback='ollama')
    model = config.get('LLM', f'{provider}_model', fallback='unknown')
    
    st.info(f"""
    **🤖 Multi-Agent Mode Active**  
    **LLM Provider:** {provider.upper()}  
    **Model:** {model}  
    **Server:** {config.get('LLM', f'{provider}_address', fallback='localhost')}
    """)
    
    # Available agents
    st.subheader("🤖 Specialized Agents")
    agent_info = {
        "🧠 Planner": "Decomposes complex tasks into steps",
        "🌐 Browser": "Web automation & navigation",
        "💻 Coder": "Code generation & debugging",
        "📁 File": "File system operations",
        "🔍 Search": "Web search capabilities",
        "💬 Casual": "Conversation & summaries"
    }
    
    for agent, desc in agent_info.items():
        st.write(f"{agent}: {desc}")
    
    # Show thinking logs toggle
    if 'show_thinking' not in st.session_state:
        st.session_state.show_thinking = True
    
    st.session_state.show_thinking = st.checkbox(
        "Show Agent Thinking",
        value=st.session_state.show_thinking,
        help="Display the thinking process of agents"
    )
    
    # Example prompts
    with st.expander("📋 Example Prompts"):
        st.markdown("""
        **Simple Tasks:**
        - "What's the weather like?"
        - "Read the README.md file"
        - "Write a Python hello world script"
        
        **Complex Tasks:**
        - "Search for Python web frameworks, compare them, and save to a file"
        - "Find recent AI news and create a summary report"
        - "Build a simple web scraper for news headlines"
        - "Research machine learning libraries and create documentation"
        """)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    # Welcome message
    if len(st.session_state.messages) == 0:
        st.info("""
        👋 Welcome to the Multi-Agent System!
        
        I use adaptive routing to intelligently handle both simple and complex tasks:
        - **Simple tasks** go directly to specialized agents
        - **Complex tasks** are planned and executed step-by-step
        
        Try asking me something complex like: "Search for the top Python web frameworks and create a comparison file"
        """)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show thinking logs if enabled and available
            if message["role"] == "assistant" and st.session_state.show_thinking:
                if "thinking_logs" in message:
                    with st.expander("🧠 Agent Thinking Process", expanded=False):
                        display_thinking_logs(message["thinking_logs"])

# Chat input
if prompt := st.chat_input("Ask your AI assistant..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("🤔 Processing your request..."):
            # Run agent
            response = run_agent(prompt)
            
            # Get thinking logs
            thinking_logs = get_thinking_logs()
            
            # Clean response
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
            
            # Display response
            message_placeholder.markdown(response)
            
            # Show thinking logs inline if enabled
            if st.session_state.show_thinking and thinking_logs:
                with st.expander("🧠 Agent Thinking Process", expanded=True):
                    display_thinking_logs(thinking_logs)
    
    # Add assistant response to history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "thinking_logs": thinking_logs
    })

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<small>🚀 Multi-Agent System</small>', unsafe_allow_html=True)
with col2:
    st.markdown('<small>⚡ Powered by Adaptive Routing</small>', unsafe_allow_html=True)
with col3:
    st.markdown('<small>🛠️ Built with LangChain</small>', unsafe_allow_html=True)
