@echo off
echo Installing Maya Chatbot Dependencies...
echo.

echo Step 1: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11 or later and try again
    pause
    exit /b 1
)

echo Step 2: Creating virtual environment...
if exist .venv (
    echo Found existing virtual environment
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo Step 4: Installing Python packages...
pip install -r requirements.txt

echo.
echo Step 2: Testing Streamlit installation...
streamlit --version

if %errorlevel% neq 0 (
    echo Streamlit installation failed. Trying manual installation...
    pip install streamlit
)

echo.
echo Step 3: Installing PyAudio for voice features...
pip install pipwin
pipwin install pyaudio

echo.
echo Installation complete!
echo.
echo Virtual environment is now active. To use it in the future:
echo   1. Run: .venv\Scripts\activate.bat
echo   2. Then run the application using run.bat
echo.
echo To run the application now:
echo streamlit run streamlit_chatbot.py
echo.
echo Or use:
echo python -m streamlit run streamlit_chatbot.py
echo.
echo Note: Always ensure the virtual environment is activated before running the app
echo Current Python interpreter: 
where python
echo.
pause
