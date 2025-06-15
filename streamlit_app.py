import streamlit as st
import configparser
from main import run_agent, config, tools_list

# Page config
st.set_page_config(
    page_title="LangEntiChain - Agentic Chat", 
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .config-info {
        background-color: #e0e7ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .tool-badge {
        background-color: #4f46e5;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        margin-right: 0.5rem;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🧠 LangEntiChain</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #6b7280;">Powered by LangChain with configurable LLM support</p>', unsafe_allow_html=True)

# Sidebar with configuration info
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Show current provider
    provider = config.get('LLM', 'provider', fallback='ollama')
    model = config.get('LLM', f'{provider}_model', fallback='unknown')
    
    st.info(f"""
    **LLM Provider:** {provider.upper()}  
    **Model:** {model}  
    **Server:** {config.get('LLM', f'{provider}_address', fallback='localhost')}
    """)
    
    # Show available tools
    st.subheader("🛠️ Available Tools")
    for tool in tools_list:
        st.write(f"• **{tool.name}** - {tool.description[:50]}...")
    
    # Instructions
    st.subheader("📝 Instructions")
    st.markdown("""
    This agent can:
    - 🔍 Search the web for information
    - 📄 Read files from your system
    - 💾 Write content to files
    - 🤖 Maintain conversation context
    
    Try asking it to search for information and save it to a file!
    """)
    
    # Clear history button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask your AI assistant..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(prompt)
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #9ca3af;">Configure LLM provider in config.ini | Built with LangChain & Streamlit</p>', 
    unsafe_allow_html=True
)
