# 🧠 LangEntiChain - Configurable Agentic Chat

A flexible agentic chat application built with LangChain that supports multiple LLM providers and tools.

## ✨ Features

- **Multiple LLM Support**: Easy switching between Ollama and LM Studio via config file
- **Web Search**: Search the web for current information
- **File Operations**: Read and write files on your system
- **Conversation Memory**: Maintains context throughout the chat
- **Beautiful UI**: Streamlit-based interface with modern styling

## 🚀 Getting Started

### 1. Set up Virtual Environment

```bash
# Create virtual environment
python -m venv my_langentichain_env

# Activate it
# Windows:
.\my_langentichain_env\Scripts\activate
# Linux/Mac:
source my_langentichain_env/bin/activate
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Configure LLM Provider

Edit `config.ini` to choose your provider:

```ini
[LLM]
# Provider options: ollama, lm_studio
provider = lm_studio

# Model names for each provider
ollama_model = deepseek-coder:33b
lm_studio_model = deepseek-r1-distill-qwen-14b-abliterated-v2

# Server addresses
ollama_address = http://localhost:11434
lm_studio_address = http://localhost:1234
```

### 4. Run the Application

```bash
streamlit run streamlit_app.py
```

## 🛠️ Available Tools

- **WebSearch**: Search the web for current information
- **ReadFile**: Read contents of files on your system
- **WriteFile**: Create or overwrite files with new content

## 📝 Example Prompts

Try these prompts to test all features:

1. "Search the web for the current price of Bitcoin and save it to crypto_prices.txt"
2. "Read the config.ini file and tell me which LLM provider I'm using"
3. "Search for today's weather in New York and create a weather_report.txt file"

## 🐳 Docker Support

```bash
docker build -t langchain-agentic-chat .
docker run -p 8501:8501 langchain-agentic-chat
```

## (Random emoji) Example Prompt

>> Search the web for the current price of Bitcoin and Ethereum in USD, along with their 24-hour percentage changes. Then read the config.ini file in the current directory to identify which LLM provider I'm using. Finally, create a new file called 'crypto_report.txt' that contains: 1) Current date and time, 2) The cryptocurrency prices and changes you found, 3) The LLM provider from the config file, and 4) A brief 2-sentence analysis of whether crypto prices are trending up or down today. Format the report with clear headers for each section.

## 🔧 Troubleshooting

- **Ollama Connection**: Make sure Ollama is running (`ollama serve`)
- **LM Studio Connection**: Ensure LM Studio server is running on port 1234
- **File Permissions**: The app needs permission to read/write files in the directories you specify

## 📄 Configuration Options

The `config.ini` file supports:

- LLM provider selection (ollama/lm_studio)
- Model configuration for each provider
- Server addresses
- Temperature and max token settings
- Tool enabling/disabling

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
