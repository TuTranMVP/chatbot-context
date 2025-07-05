"""
Maya Advanced FAQ Chatbot - Streamlit UI
A modern web interface for the Maya chatbot with voice and text functionality.
"""

import streamlit as st
import time
from typing import Dict, List, Tuple, Optional, Any

# Import modular components
try:
    from components.chatbot_core import MayaChatbot
    from components.voice_interface import VoiceInterface, check_microphone_permission
    from components.tts_interface import TTSInterface
    from components.ui_components import (
        render_text_mode_ui, 
        render_voice_mode_ui,
        render_mode_selector,
        render_sidebar_info,
        render_custom_css
    )
except ImportError as e:
    st.error(f"Failed to import components: {e}")
    st.error("Please ensure all component files are in the 'components' directory")
    st.stop()

# Streamlit UI
def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Maya Advanced FAQ Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    render_custom_css()
    
    # Initialize components in session state
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = MayaChatbot()
    
    if "voice_interface" not in st.session_state:
        st.session_state.voice_interface = VoiceInterface(st.session_state.chatbot)
    
    if "tts_interface" not in st.session_state:
        st.session_state.tts_interface = TTSInterface()
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "pending_message" not in st.session_state:
        st.session_state.pending_message = None
    
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False
    
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    
    if "is_speaking" not in st.session_state:
        st.session_state.is_speaking = False
    
    # Process pending message if exists
    if st.session_state.pending_message:
        message = st.session_state.pending_message
        st.session_state.pending_message = None  # Clear it immediately
        
        with st.spinner("🤖 Maya is thinking..."):
            bot_response, structured_data = st.session_state.chatbot.process_message(message)
        
        # Add to chat history
        st.session_state.chat_history.append((message, bot_response, structured_data))
        
        # If in voice mode, speak the response
        if st.session_state.get('interface_mode') == 'voice':
            if st.session_state.tts_interface:
                st.session_state.is_speaking = True
                st.session_state.tts_interface.speak_text(bot_response)
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Maya Advanced FAQ Chatbot</h1>', unsafe_allow_html=True)
    
    # Sidebar with mode selector and information
    with st.sidebar:
        # Mode selector
        mode = render_mode_selector()
        
        # Information
        render_sidebar_info()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.session_state.chatbot.clear_conversation()
            # Stop any ongoing voice operations
            if st.session_state.voice_interface:
                st.session_state.voice_interface.stop_recording()
            if st.session_state.tts_interface:
                st.session_state.tts_interface.stop_speaking()
            st.session_state.is_recording = False
            st.session_state.is_speaking = False
            st.rerun()
    
    # Main interface based on selected mode
    if mode == "voice":
        # Auto-start voice recording when entering voice mode
        if not st.session_state.get('voice_mode_active', False):
            st.session_state.voice_mode_active = True
            if st.session_state.voice_interface.start_continuous_recording():
                st.session_state.is_recording = True
        
        # Check for new transcriptions
        if st.session_state.is_recording:
            # Voice interface now processes messages directly through chatbot
            # No need to check for transcriptions manually
            pass
        
        render_voice_mode_ui(
            st.session_state.chat_history,
            st.session_state.voice_interface,
            st.session_state.tts_interface,
            handle_voice_input
        )
        
        # Simple auto-refresh for voice mode
        if st.session_state.get('voice_mode_active', False):
            # Use a simple timer for periodic refresh in voice mode
            if 'last_voice_check' not in st.session_state:
                st.session_state.last_voice_check = time.time()
            
            current_time = time.time()
            if current_time - st.session_state.last_voice_check > 2.0:  # Check every 2 seconds
                st.session_state.last_voice_check = current_time
                st.rerun()
    else:
        # Stop voice recording when leaving voice mode
        if st.session_state.get('voice_mode_active', False):
            st.session_state.voice_mode_active = False
            st.session_state.voice_interface.stop_recording()
            st.session_state.is_recording = False
        
        render_text_mode_ui(
            st.session_state.chat_history,
            handle_user_input
        )

def handle_user_input():
    """Handle user input when Enter is pressed in text mode"""
    if st.session_state.user_input and st.session_state.user_input.strip():
        message = st.session_state.user_input.strip()
        
        # Store the message to be processed and clear input
        st.session_state.pending_message = message
        st.session_state.user_input = ""

def handle_voice_input(action: str):
    """Handle voice input actions"""
    if action == "stop_speaking":
        if st.session_state.tts_interface:
            st.session_state.tts_interface.stop_speaking()
            st.session_state.is_speaking = False
            st.rerun()

if __name__ == "__main__":
    main()
