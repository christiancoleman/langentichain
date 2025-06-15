import streamlit as st
import configparser
from main import run_agent, config, tools_list

# Page config
st.set_page_config(
    page_title="LangEntiChain - Agentic Chat", 
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for better styling and dark mode support
st.markdown("""
<style>
    /* Light mode base */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Dark mode overrides */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0e1117;
        }
        
        /* Fix white background in agent output */
        .stMarkdown, .stCodeBlock, div[data-testid="stMarkdownContainer"] {
            background-color: transparent !important;
            color: inherit !important;
        }
        
        /* Dark mode for code blocks */
        pre {
            background-color: #1e2127 !important;
            color: #abb2bf !important;
        }
        
        /* Dark mode for message containers */
        div[data-testid="stChatMessage"] {
            background-color: #262730 !important;
        }
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
        background-color: rgba(59, 130, 246, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    .tool-badge {
        background-color: #4f46e5;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        margin-right: 0.5rem;
        font-size: 0.875rem;
    }
    
    /* Fix for agent thinking output */
    .agent-output {
        white-space: pre-wrap;
        font-family: monospace;
        background-color: rgba(0, 0, 0, 0.05);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* Dark mode agent output */
    @media (prefers-color-scheme: dark) {
        .agent-output {
            background-color: rgba(255, 255, 255, 0.05);
        }
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
    
    # Get agent config
    max_iterations = config.getint('AGENT', 'max_iterations', fallback=1000)
    
    st.info(f"""
    **LLM Provider:** {provider.upper()}  
    **Model:** {model}  
    **Server:** {config.get('LLM', f'{provider}_address', fallback='localhost')}  
    **Max Iterations:** {max_iterations}
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
    
    # Show example prompt
    with st.expander("📋 Example Test Prompt"):
        st.code("""Search the web for the current price of Bitcoin and Ethereum in USD, along with their 24-hour percentage changes. Then read the config.ini file in the current directory to identify which LLM provider I'm using. Finally, create a new file called 'crypto_report.txt' that contains: 1) Current date and time, 2) The cryptocurrency prices and changes you found, 3) The LLM provider from the config file, and 4) A brief 2-sentence analysis of whether crypto prices are trending up or down today.""")
    
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
        if message["role"] == "assistant":
            # Clean up any remaining think tags in display
            content = message["content"]
            import re
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
            st.markdown(content)
        else:
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
        message_placeholder = st.empty()
        
        # Show thinking message while processing
        with st.spinner("🤔 Agent is thinking..."):
            response = run_agent(prompt)
        
        # Clean any think tags from response
        import re
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Display the response
        message_placeholder.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<small>Configure in config.ini</small>', unsafe_allow_html=True)
with col2:
    st.markdown('<small>Max iterations: ' + str(max_iterations) + '</small>', unsafe_allow_html=True)
with col3:
    st.markdown('<small>Built with LangChain & Streamlit</small>', unsafe_allow_html=True)
