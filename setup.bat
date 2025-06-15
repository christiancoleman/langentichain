@echo off
echo ====================================
echo LangEntiChain Setup Script
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "my_langentichain_env\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv my_langentichain_env
)

echo Activating virtual environment...
call my_langentichain_env\Scripts\activate.bat

echo.
echo Cleaning old packages...
pip uninstall langchain langchain-community langchain-core -y 2>nul

echo.
echo Installing requirements...
pip install --no-cache-dir -r requirements.txt

echo.
echo Running import check...
python check_imports.py

echo.
echo ====================================
echo Setup complete!
echo.
echo To run the application:
echo   streamlit run streamlit_app.py
echo ====================================
pause
