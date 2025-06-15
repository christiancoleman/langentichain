#!/usr/bin/env python3
"""Test script to verify LLM provider connections"""

import configparser
from main import get_llm, config

def test_connection():
    print("🧪 Testing LLM Connection...")
    print(f"Provider: {config.get('LLM', 'provider')}")
    
    try:
        llm = get_llm()
        print("✅ LLM initialized successfully!")
        
        # Test with a simple query
        if config.get('LLM', 'provider') == 'lm_studio':
            test_response = llm._call("Say 'Hello, LM Studio is working!'")
        else:  # Ollama
            test_response = llm.invoke("Say 'Hello, Ollama is working!'").content
            
        print(f"📝 Response: {test_response}")
        print("\n✨ Connection test passed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        if config.get('LLM', 'provider') == 'lm_studio':
            print("- Make sure LM Studio is running")
            print("- Check that the server is on port 1234")
            print("- Verify a model is loaded in LM Studio")
        else:
            print("- Make sure Ollama is running (ollama serve)")
            print("- Check that the model is pulled (ollama pull model_name)")

if __name__ == "__main__":
    test_connection()
