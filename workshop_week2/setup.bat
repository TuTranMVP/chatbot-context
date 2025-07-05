@echo off
echo Installing Maya Chatbot Dependencies...
echo.

echo Step 1: Installing Python packages...
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
echo To run the application:
echo streamlit run streamlit_chatbot.py
echo.
echo Or use:
echo python -m streamlit run streamlit_chatbot.py
echo.
pause
