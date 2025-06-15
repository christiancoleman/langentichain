#!/usr/bin/env python3
"""
Quick fix script for LangChain import issues
Run this after installing requirements if you still get import errors
"""

print("🔧 LangChain Import Diagnostics")
print("=" * 50)

# Test each import
imports_to_test = [
    ("langchain", "Core LangChain"),
    ("langchain_community", "LangChain Community"),
    ("langchain_core", "LangChain Core"),
    ("ollama", "Ollama Python client"),
    ("openai", "OpenAI client"),
    ("streamlit", "Streamlit"),
]

all_good = True
for module, description in imports_to_test:
    try:
        __import__(module)
        print(f"✅ {description:<25} - OK")
    except ImportError as e:
        print(f"❌ {description:<25} - MISSING")
        all_good = False

print("=" * 50)

if not all_good:
    print("\n⚠️  Some packages are missing. Run:")
    print("pip install -r requirements.txt")
else:
    print("\n✨ All packages installed correctly!")
    
    # Try importing specific classes
    print("\n🧪 Testing specific imports...")
    try:
        from langchain_community.chat_models import ChatOllama
        print("✅ ChatOllama import - OK")
    except ImportError as e:
        print(f"❌ ChatOllama import - ERROR: {e}")
        
    try:
        from langchain_core.language_models.llms import LLM
        print("✅ LLM base class import - OK")
    except ImportError as e:
        print(f"❌ LLM base class import - ERROR: {e}")

print("\n📝 If you're still having issues, try:")
print("1. pip uninstall langchain langchain-community langchain-core")
print("2. pip install langchain langchain-community langchain-core")
