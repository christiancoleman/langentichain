# LangEntiChain - Multi-Agent System

A multi-agent system powered by LangChain with intelligent routing. The system routes queries to specialized agents and provides real-time thinking visualization.

## 🌟 Features

- **Intelligent Routing**: Routes queries based on complexity and task type
- **Multi-Agent Architecture**: Specialized agents for different tasks:
  - 🧠 **Planner Agent**: Decomposes complex tasks into executable steps
  - 🌐 **Browser Agent**: Web automation with Selenium
  - 💻 **Coder Agent**: Code generation and debugging
  - 📁 **File Agent**: File system operations
  - 🔍 **Search Agent**: Web search capabilities
  - 💬 **Casual Agent**: Conversation and summaries
- **Real-Time Thinking Visualization**: See how agents think and make decisions
- **Streamlit Web Interface**: User-friendly UI with dark mode support
- **Configurable LLM Support**: Works with Ollama and LM Studio

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ollama or LM Studio running locally
- Chrome/Chromium browser (for browser automation)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/langentichain.git
cd langentichain
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your LLM provider in `config.ini`:
```ini
[LLM]
provider = lm_studio  # or ollama
lm_studio_model = your-model-name
lm_studio_address = http://localhost:1234
```

4. Run the Streamlit interface:
```bash
streamlit run streamlit_app.py
```

## 🎯 Usage Examples

### Simple Tasks (Direct Routing)
- "What's the weather like?"
- "Read the config.ini file"
- "Write a Python hello world script"
- "Search for Python tutorials"

### Complex Tasks (Multi-Step Planning)
- "Search for the top 5 Python web frameworks, create a comparison table, and save it to a file"
- "Find recent AI research papers and build a web interface to display them"
- "Navigate to GitHub, search for awesome-python, and save the top 10 repos to a file"

## 🏗️ Architecture

### Routing System

The system uses an intelligent router to analyze queries:

1. **Complexity Estimation**: Determines if a query is simple or complex
2. **Task Classification**: Routes simple queries to specific agents based on task type
3. **Multi-Agent Coordination**: Complex queries are handled by the planner agent

### Agent Communication Flow

```
User Query → Router (Complexity Analysis) → 
  ├─ Complex → Planner Agent → Task Decomposition → Multiple Agents
  └─ Simple → Direct Agent Assignment → Single Agent Execution
```

## 🛠️ Configuration

### config.ini Options

```ini
[LLM]
provider = lm_studio          # LLM provider: ollama or lm_studio
temperature = 0.7            # Generation temperature
max_tokens = 4096           # Maximum tokens per response

[AGENT]
max_iterations = 1000       # Max agent iterations
verbose = true             # Show detailed agent output

[BROWSER]
headless = false          # Run browser in headless mode
screenshot_on_navigate = true  # Take screenshots

[TOOLS]
enable_web_search = true
enable_file_operations = true
enable_browser = true
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Agent Gets Stuck or Loops
**Symptoms**: Agent repeats the same action multiple times

**Solutions**:
- Check that your LLM model supports tool calling properly
- Try a different model (some models handle agents better)
- Increase `temperature` in config.ini to 0.8 or 0.9
- Ensure tools are returning clear, parseable responses

#### 2. LM Studio Connection Failed
**Symptoms**: Can't connect to LM Studio

**Solutions**:
- Ensure LM Studio server is running
- Check it's on port 1234 (default)
- Model must be loaded in LM Studio
- Try http://localhost:1234/v1/models to verify

#### 3. Ollama Connection Failed
**Symptoms**: Can't connect to Ollama

**Solutions**:
- Run `ollama serve` in terminal
- Pull your model: `ollama pull model-name`
- Check port 11434 is available
- Verify with: `curl http://localhost:11434/api/tags`

#### 4. File Write Errors
**Symptoms**: Agent can't create files

**Solutions**:
- Check file permissions in the directory
- Use absolute paths if relative paths fail
- Ensure no special characters in filenames
- Remember the format: `filename|content`

#### 5. Import Errors
**Symptoms**: ModuleNotFoundError for langchain packages

**Solutions**:
```bash
# Clean reinstall
pip uninstall langchain langchain-community langchain-core -y
pip install -r requirements.txt
```

#### 6. Browser Automation Issues
**Symptoms**: Browser agent fails to navigate

**Solutions**:
- Install Chrome/Chromium browser
- Update chromedriver to match your Chrome version
- Check `headless` setting in config.ini
- Ensure no other Chrome instances are running

#### 7. Slow Response Times
**Symptoms**: Agent takes long to respond

**Solutions**:
- Check model size vs. your hardware
- Use smaller/faster models for testing
- Reduce `max_tokens` in config.ini
- Disable `verbose` mode for production use

#### 8. Memory/Context Issues
**Symptoms**: Agent forgets previous conversation

**Solutions**:
- ConversationBufferMemory is working but has limits
- For long conversations, consider ConversationSummaryMemory
- Clear chat history if context gets too large

### 9. Missing Input Keys Error
**Symptoms**: `ValueError: Missing some input keys: {'input'}`

**Solutions**:
- Use `agent.invoke({"input": query})` instead of `agent.run(query)`
- The new LangChain API expects dictionary input
- Extract output with `result.get('output', result)`

### 10. Deprecation Warnings
**Symptoms**: Various deprecation warnings about old methods

**Solutions**:
- These are informational - code still works
- Update to new methods when convenient:
  - `.run()` → `.invoke()`
  - `AgentExecutor` → Consider `LangGraph` for new projects
- See `UNDERSTANDING_ERRORS.md` for detailed migration guide

### Debug Mode

Add this to your config.ini for maximum debugging:
```ini
[AGENT]
verbose = true
return_intermediate_steps = true
```

Then check the console output when running the app.

## 📊 Thinking Visualization

The system provides real-time visualization of agent thinking processes:

- **Router Decisions**: See how queries are classified and routed
- **Agent Actions**: Track what each agent is doing
- **Thought Process**: Understand the reasoning behind decisions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- UI powered by [Streamlit](https://streamlit.io)
