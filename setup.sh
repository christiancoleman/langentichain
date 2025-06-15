#!/bin/bash
echo "===================================="
echo "LangEntiChain Setup Script"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -f "my_langentichain_env/bin/activate" ]; then
    echo "Creating virtual environment..."
    python3 -m venv my_langentichain_env
fi

echo "Activating virtual environment..."
source my_langentichain_env/bin/activate

echo ""
echo "Cleaning old packages..."
pip uninstall langchain langchain-community langchain-core -y 2>/dev/null

echo ""
echo "Installing requirements..."
pip install --no-cache-dir -r requirements.txt

echo ""
echo "Running import check..."
python check_imports.py

echo ""
echo "===================================="
echo "Setup complete!"
echo ""
echo "To run the application:"
echo "  streamlit run streamlit_app.py"
echo "===================================="
