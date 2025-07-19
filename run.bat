@echo off
echo Starting Maya Chatbot...
echo.

echo Checking virtual environment...
if not exist ".venv" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first to create the virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Checking if we're in the correct directory...
if not exist "streamlit_chatbot.py" (
    echo Error: streamlit_chatbot.py not found!
    echo Please make sure you're in the correct directory.
    echo Current directory: %cd%
    echo.
    pause
    exit /b 1
)

echo Found streamlit_chatbot.py
echo.

echo Checking Streamlit installation...
streamlit --version >nul 2>&1

if %errorlevel% neq 0 (
    echo Streamlit is not installed! Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

echo Streamlit is installed.
echo.

echo Starting the application...
echo.
echo The application will open in your default web browser.
echo To stop the application, press Ctrl+C in this window.
echo.

streamlit run streamlit_chatbot.py

pause
