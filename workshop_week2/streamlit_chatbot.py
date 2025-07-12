"""
Maya Advanced FAQ Chatbot - Streamlit UI
A modern web interface for the Maya chatbot with voice and text functionality.
"""

import time

import streamlit as st

# Import modular components
try:
    from components.chatbot_core import MayaChatbot
    from components.file_manager import (
        render_file_manager,
        render_file_manager_css,
    )
    from components.tts_interface import TTSInterface
    from components.ui_duolingo import (
        display_duolingo_data,
        display_duolingo_guide,
        render_duolingo_chat_mode,
        render_duolingo_css,
        render_duolingo_landing,
        render_duolingo_voice_mode,
        render_quick_suggestions,
    )
    from components.voice_interface import VoiceInterface
except ImportError as e:
    st.error(f'Failed to import components: {e}')
    st.error(
        "Please ensure all component files are in the 'components' directory"
    )
    st.stop()


# Streamlit UI
def main():
    """Main Streamlit application with Duolingo-inspired UI"""
    st.set_page_config(
        page_title='Maya AI Assistant',
        page_icon='🤖',
        layout='wide',
        initial_sidebar_state='collapsed',
    )

    # Apply Duolingo-inspired CSS
    render_duolingo_css()
    render_file_manager_css()

    # Initialize components in session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = MayaChatbot()

    if 'voice_interface' not in st.session_state:
        st.session_state.voice_interface = VoiceInterface(
            st.session_state.chatbot
        )

    if 'tts_interface' not in st.session_state:
        st.session_state.tts_interface = TTSInterface()

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'pending_message' not in st.session_state:
        st.session_state.pending_message = None

    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False

    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False

    if 'is_speaking' not in st.session_state:
        st.session_state.is_speaking = False

    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = 'landing'

    # Process pending message if exists
    if st.session_state.pending_message:
        message = st.session_state.pending_message
        st.session_state.pending_message = None  # Clear it immediately

        with st.spinner('🤖 Maya is thinking...'):
            bot_response, structured_data = (
                st.session_state.chatbot.process_message(message)
            )

        # Add to chat history
        st.session_state.chat_history.append(
            (message, bot_response, structured_data)
        )

        # If in voice mode, speak the response
        if st.session_state.current_mode == 'voice':
            if st.session_state.tts_interface:
                st.session_state.is_speaking = True
                st.session_state.tts_interface.speak_text(bot_response)

    # Route to appropriate UI based on current mode
    if st.session_state.current_mode == 'landing':
        render_duolingo_landing()
        
        # Handle landing page actions
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button('💬 Start Chatting', key='start_chat', use_container_width=True, type='primary'):
                    st.session_state.current_mode = 'chat'
                    st.rerun()
            with col_b:
                if st.button('🎤 Voice Mode', key='start_voice', use_container_width=True):
                    st.session_state.current_mode = 'voice'
                    st.rerun()
            
            st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
            
            # Feature buttons
            col_1, col_2, col_3, col_4 = st.columns(4)
            with col_1:
                if st.button('📚 Guides', key='guides', use_container_width=True):
                    st.session_state.current_mode = 'guides'
                    st.rerun()
            with col_2:
                if st.button('📊 Data', key='data', use_container_width=True):
                    st.session_state.current_mode = 'data'
                    st.rerun()
            with col_3:
                if st.button('📁 Files', key='files', use_container_width=True):
                    st.session_state.current_mode = 'files'
                    st.rerun()
            with col_4:
                if st.button('❓ Q&A', key='qa', use_container_width=True):
                    st.session_state.current_mode = 'chat'
                    st.rerun()

    elif st.session_state.current_mode == 'chat':
        # Top navigation with back to landing
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button('🏠 Home', key='home_from_chat'):
                st.session_state.current_mode = 'landing'
                st.rerun()
        with col2:
            st.markdown('<h2 style="text-align: center; margin: 0;">💬 Chat Mode</h2>', unsafe_allow_html=True)
        with col3:
            if st.button('📁 Files', key='to_files_from_chat'):
                st.session_state.current_mode = 'files'
                st.rerun()
        with col4:
            if st.button('🎤 Voice', key='to_voice_from_chat'):
                st.session_state.current_mode = 'voice'
                st.rerun()
        
        render_duolingo_chat_mode()
        
        # Handle user input
        if st.session_state.get('user_input') or st.session_state.get('suggestion_clicked'):
            user_input = st.session_state.get('user_input', '')
            if user_input.strip():
                st.session_state.pending_message = user_input.strip()
                st.session_state['user_input'] = ''
                st.session_state['suggestion_clicked'] = False
                st.rerun()
        
        render_quick_suggestions()
        
        # Clear chat button for chat mode
        if st.session_state.chat_history:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button('🗑️ Clear Chat', key='clear_chat_text', use_container_width=True, type='secondary'):
                    st.session_state.chat_history = []
                    st.session_state.chatbot.clear_conversation()
                    st.rerun()

    elif st.session_state.current_mode == 'voice':
        # Auto-start voice recording when entering voice mode
        if not st.session_state.get('voice_mode_active', False):
            st.session_state.voice_mode_active = True
            if st.session_state.voice_interface.start_continuous_recording():
                st.session_state.is_recording = True

        # Top navigation with back to landing
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button('🏠 Home', key='home_from_voice'):
                st.session_state.current_mode = 'landing'
                if st.session_state.get('voice_mode_active', False):
                    st.session_state.voice_mode_active = False
                    st.session_state.voice_interface.stop_recording()
                    st.session_state.is_recording = False
                st.rerun()
        with col2:
            st.markdown('<h2 style="text-align: center; margin: 0;">🎤 Voice Mode</h2>', unsafe_allow_html=True)
        with col3:
            if st.button('📁 Files', key='to_files_from_voice'):
                st.session_state.current_mode = 'files'
                if st.session_state.get('voice_mode_active', False):
                    st.session_state.voice_mode_active = False
                    st.session_state.voice_interface.stop_recording()
                    st.session_state.is_recording = False
                st.rerun()
        with col4:
            if st.button('💬 Chat', key='to_chat_from_voice'):
                st.session_state.current_mode = 'chat'
                if st.session_state.get('voice_mode_active', False):
                    st.session_state.voice_mode_active = False
                    st.session_state.voice_interface.stop_recording()
                    st.session_state.is_recording = False
                st.rerun()

        render_duolingo_voice_mode()

        # Auto-refresh for voice mode
        if st.session_state.get('voice_mode_active', False):
            if 'last_voice_check' not in st.session_state:
                st.session_state.last_voice_check = time.time()

            current_time = time.time()
            if current_time - st.session_state.last_voice_check > 2.0:
                st.session_state.last_voice_check = current_time
                st.rerun()
        
        # Clear chat button for voice mode
        if st.session_state.chat_history:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button('🗑️ Clear Chat', key='clear_chat_voice', use_container_width=True, type='secondary'):
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

    elif st.session_state.current_mode == 'data':
        # Top navigation with back to landing
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button('🏠 Home', key='home_from_data'):
                st.session_state.current_mode = 'landing'
                st.rerun()
        with col2:
            st.markdown('<h2 style="text-align: center; margin: 0;">📊 Data Generation</h2>', unsafe_allow_html=True)
        with col3:
            if st.button('📁 Files', key='to_files_from_data'):
                st.session_state.current_mode = 'files'
                st.rerun()
        with col4:
            if st.button('💬 Chat', key='to_chat_from_data'):
                st.session_state.current_mode = 'chat'
                st.rerun()
        
        # Display sample data
        sample_data = {
            "data_type": "Sample Data",
            "count": 100,
            "output_format": "json",
            "ai_enhanced": True,
            "generated_data": [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
            ]
        }
        display_duolingo_data(sample_data)

    elif st.session_state.current_mode == 'guides':
        # Top navigation with back to landing
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button('🏠 Home', key='home_from_guides'):
                st.session_state.current_mode = 'landing'
                st.rerun()
        with col2:
            st.markdown('<h2 style="text-align: center; margin: 0;">📚 Guides</h2>', unsafe_allow_html=True)
        with col3:
            if st.button('📁 Files', key='to_files_from_guides'):
                st.session_state.current_mode = 'files'
                st.rerun()
        with col4:
            if st.button('💬 Chat', key='to_chat_from_guides'):
                st.session_state.current_mode = 'chat'
                st.rerun()
        
        # Display sample guide
        sample_guide = {
            "title": "Getting Started with Maya",
            "category": "Tutorial",
            "difficulty": "Beginner",
            "estimated_time": "5 minutes",
            "guide_steps": [
                "Click on Start Chatting to begin",
                "Type your question in the chat box",
                "Press Enter to send your message",
                "Maya will respond with helpful information",
                "Use Voice Mode for hands-free interaction"
            ]
        }
        display_duolingo_guide(sample_guide)

    elif st.session_state.current_mode == 'files':
        # Top navigation with back to landing
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button('🏠 Home', key='home_from_files'):
                st.session_state.current_mode = 'landing'
                st.rerun()
        with col2:
            st.markdown('<h2 style="text-align: center; margin: 0;">📁 File Manager</h2>', unsafe_allow_html=True)
        with col3:
            if st.button('💬 Chat', key='to_chat_from_files'):
                st.session_state.current_mode = 'chat'
                st.rerun()
        
        # Render file manager interface
        render_file_manager()
        
        # Instructions
        st.markdown(
            """
            <div style="padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <h4 style="color: #58cc02; margin-top: 0;">📋 How to use:</h4>
                <ul style="margin-bottom: 0;">
                    <li>📤 Upload .txt or .md files using the upload section</li>
                    <li>🔍 Search through your files by name or content</li>
                    <li>👁️ Preview file contents before using</li>
                    <li>💬 Click "Use in Chat" to send file content to Maya for analysis</li>
                    <li>🗑️ Delete individual files or clear all files</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Add footer to all pages except landing
    if st.session_state.current_mode != 'landing':
        st.markdown(
            """
            <div style="text-align: center; padding: 2rem 0; margin-top: 3rem; border-top: 1px solid #e0e0e0;">
                <p style="color: #666; margin: 0; font-size: 0.9rem;">
                    Made with ❤️ by TuTT42 Teams • Always learning, always helping
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

def handle_user_input():
    """Handle user input when Enter is pressed in text mode"""
    if st.session_state.user_input and st.session_state.user_input.strip():
        message = st.session_state.user_input.strip()

        # Store the message to be processed and clear input
        st.session_state.pending_message = message
        st.session_state.user_input = ''


def handle_voice_input(action: str):
    """Handle voice input actions"""
    if action == 'stop_speaking':
        if st.session_state.tts_interface:
            st.session_state.tts_interface.stop_speaking()
            st.session_state.is_speaking = False
            st.rerun()


def handle_suggestion_click(query: str):
    """Handle quick suggestion clicks"""
    st.session_state.pending_message = query
    st.rerun()


if __name__ == '__main__':
    main()
