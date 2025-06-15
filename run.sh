#!/bin/bash

echo "Starting LangEntiChain Enhanced Multi-Agent System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "my_langentichain_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv my_langentichain_env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source my_langentichain_env/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if LLM provider is running
echo
echo "Checking LLM provider..."
python test_connection.py
if [ $? -ne 0 ]; then
    echo
    echo "Warning: LLM provider connection failed!"
    echo "Please ensure Ollama or LM Studio is running."
    echo
fi

# Start Streamlit
echo
echo "Starting Streamlit interface..."
echo
streamlit run streamlit_app.py