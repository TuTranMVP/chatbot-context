"""
Maya Chatbot - Voice and Text Interface Components

This package contains modular components for the Maya chatbot:
- chatbot_core.py: Core chatbot logic and OpenAI integration
- voice_interface.py: Speech-to-text functionality
- tts_interface.py: Text-to-speech functionality
- ui_components.py: UI rendering components

Quick Setup:
1. Install dependencies: pip install -r requirements.txt
2. Run application: python -m streamlit run streamlit_chatbot.py

For voice features on Windows:
pip install pipwin && pipwin install pyaudio

Troubleshooting:
- If "streamlit not recognized": use "python -m streamlit run streamlit_chatbot.py"
- If microphone issues: check browser permissions
- If audio issues: check system audio settings
"""

# Package version
__version__ = '1.0.0'

# Import main components for easy access
try:
    from .chatbot_core import MayaChatbot
    from .tts_interface import TTSInterface
    from .ui_duolingo import (
        render_duolingo_css,
        display_duolingo_data,
        display_duolingo_guide,
        render_duolingo_chat_mode,
        render_duolingo_landing,
        render_duolingo_voice_mode,
        render_quick_suggestions,
    )
    from .voice_interface import VoiceInterface, check_microphone_permission

    __all__ = [
        'MayaChatbot',
        'VoiceInterface',
        'check_microphone_permission',
        'TTSInterface',
        'render_duolingo_css',
        'display_duolingo_data',
        'display_duolingo_guide',
        'render_duolingo_chat_mode',
        'render_duolingo_landing',
        'render_duolingo_voice_mode',
        'render_quick_suggestions',
    ]

except ImportError as e:
    # Handle import errors gracefully
    print(f'Warning: Could not import some components: {e}')
    __all__ = []
