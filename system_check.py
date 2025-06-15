#!/usr/bin/env python3
"""
System Check and Recommendations
Analyzes your setup and provides specific recommendations
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

def check_package_version(package_name):
    """Check if a package is installed and get its version"""
    try:
        module = importlib.import_module(package_name.replace('-', '_'))
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, None

def check_langchain_setup():
    """Check LangChain installation and versions"""
    print("\n📦 Checking LangChain Installation:")
    print("-" * 40)
    
    packages = [
        'langchain',
        'langchain-core',
        'langchain-community',
        'streamlit',
        'selenium',
        'requests'
    ]
    
    all_good = True
    versions = {}
    
    for package in packages:
        installed, version = check_package_version(package)
        if installed:
            print(f"✅ {package:<20} {version}")
            versions[package] = version
        else:
            print(f"❌ {package:<20} NOT INSTALLED")
            all_good = False
    
    return all_good, versions

def check_file_structure():
    """Check if all required files exist"""
    print("\n📁 Checking File Structure:")
    print("-" * 40)
    
    required_files = [
        'main.py',
        'streamlit_app.py',
        'multi_agent_system.py',
        'config.ini',
        'requirements.txt',
        'agents/__init__.py',
        'routing/__init__.py',
        'tools/__init__.py',
        'core/__init__.py'
    ]
    
    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_good = False
    
    return all_good

def check_config():
    """Check configuration file"""
    print("\n⚙️ Checking Configuration:")
    print("-" * 40)
    
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        # Check key settings
        provider = config.get('LLM', 'provider', fallback='unknown')
        model = config.get('LLM', f'{provider}_model', fallback='unknown')
        
        print(f"✅ LLM Provider: {provider}")
        print(f"✅ Model: {model}")
        
        # Check if LLM is accessible
        if provider == 'ollama':
            print("   → Make sure Ollama is running: 'ollama serve'")
        elif provider == 'lm_studio':
            print("   → Make sure LM Studio server is running on port 1234")
        
        return True
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def check_deprecated_code():
    """Check for deprecated patterns in code"""
    print("\n🔍 Checking for Deprecated Patterns:")
    print("-" * 40)
    
    deprecated_patterns = {
        '.run(': 'Use .invoke({"input": query}) instead',
        'agent.run': 'Use agent.invoke instead',
        'Chain.run': 'Use Chain.invoke instead'
    }
    
    issues_found = False
    
    # Check Python files
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and cache
        if 'env' in root or '__pycache__' in root or '_deprecated' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern, fix in deprecated_patterns.items():
                            if pattern in content:
                                print(f"⚠️ {filepath}: Found '{pattern}'")
                                print(f"   → {fix}")
                                issues_found = True
                except:
                    pass
    
    if not issues_found:
        print("✅ No deprecated patterns found")
    
    return not issues_found

def provide_recommendations(checks):
    """Provide specific recommendations based on checks"""
    print("\n💡 Recommendations:")
    print("-" * 40)
    
    if not checks['packages']:
        print("\n1. Install missing packages:")
        print("   pip install -r requirements.txt")
    
    if not checks['files']:
        print("\n2. Ensure you're in the project root directory")
        print("   Some required files are missing")
    
    if not checks['deprecated']:
        print("\n3. Update deprecated code:")
        print("   - Replace .run() with .invoke()")
        print("   - See UNDERSTANDING_ERRORS.md for details")
    
    print("\n📚 Helpful Resources:")
    print("   - ERROR_SUMMARY.md - Quick error fixes")
    print("   - UNDERSTANDING_ERRORS.md - Detailed error guide")
    print("   - compare_architectures.py - Compare with AgenticSeek")
    print("   - debug_tools.py - Test tools in isolation")
    
    print("\n🚀 Next Steps:")
    print("   1. Fix any ❌ items above")
    print("   2. Run 'python test_imports.py' to verify imports")
    print("   3. Run 'streamlit run streamlit_app.py' to start")

def main():
    """Run all checks and provide recommendations"""
    print("🏥 LangEntiChain System Check")
    print("=" * 60)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run checks
    checks = {}
    
    packages_ok, versions = check_langchain_setup()
    checks['packages'] = packages_ok
    
    files_ok = check_file_structure()
    checks['files'] = files_ok
    
    config_ok = check_config()
    checks['config'] = config_ok
    
    deprecated_ok = check_deprecated_code()
    checks['deprecated'] = deprecated_ok
    
    # Overall status
    print("\n📊 Overall Status:")
    print("-" * 40)
    
    all_good = all(checks.values())
    if all_good:
        print("✅ System is ready to use!")
        print("\nRun: streamlit run streamlit_app.py")
    else:
        print("⚠️ Some issues need attention")
        provide_recommendations(checks)
    
    # Version compatibility note
    if 'langchain' in versions:
        lc_version = versions['langchain']
        if lc_version.startswith('0.1') or lc_version.startswith('0.2'):
            print("\n📌 Note: You're using LangChain v0.1/0.2")
            print("   Some examples online may use older syntax")
            print("   Refer to our updated examples")

if __name__ == "__main__":
    main()
