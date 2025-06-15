@echo off
echo Starting LangEntiChain Enhanced Multi-Agent System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "my_langentichain_env" (
    echo Creating virtual environment...
    python -m venv my_langentichain_env
)

REM Activate virtual environment
echo Activating virtual environment...
call my_langentichain_env\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if LLM provider is running
echo.
echo Checking LLM provider...
python test_connection.py
if errorlevel 1 (
    echo.
    echo Warning: LLM provider connection failed!
    echo Please ensure Ollama or LM Studio is running.
    echo.
)

REM Start Streamlit
echo.
echo Starting Streamlit interface...
echo.
streamlit run streamlit_app.py

pause