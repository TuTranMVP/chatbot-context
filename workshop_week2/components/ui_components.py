"""
UI Components for Maya Chatbot
Contains both text and voice mode interfaces
"""

import json
from typing import Any, Callable, Dict, List

import pandas as pd
import streamlit as st


def render_text_mode_ui(
    chat_history: List, handle_user_input_callback: Callable
):
    """Render the text-based chat interface"""

    st.subheader('💬 Chat Interface')

    # Chat history display
    chat_container = st.container()
    with chat_container:
        if chat_history:
            for i, (user_msg, bot_msg, structured_data) in enumerate(
                chat_history
            ):
                st.markdown(
                    f'<div class="user-message">👤 {user_msg}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="bot-message">🤖 {bot_msg}</div>',
                    unsafe_allow_html=True,
                )

                # Show structured data right after each bot response
                if structured_data:
                    response_type = structured_data.get('type', 'unknown')
                    with st.expander(
                        f'📋 {response_type.title()} Data', expanded=False
                    ):
                        if response_type == 'mock_data':
                            display_mock_data(structured_data)
                        elif response_type == 'guide':
                            display_guide_data(structured_data)
                        else:
                            st.json(structured_data)
        else:
            st.info(
                '👋 Welcome! Ask me anything about guides, mock data generation, or general questions.'
            )

    # User input with Enter to send
    st.text_input(
        'Your question:',
        placeholder='Type your message and press Enter to send...',
        key='user_input',
        label_visibility='collapsed',
        on_change=handle_user_input_callback,
    )


def render_voice_mode_ui(
    chat_history: List,
    voice_interface,
    tts_interface,
    handle_voice_input_callback: Callable,
):
    """Render the voice-based chat interface (ChatGPT-like)"""

    st.markdown(
        """
    <style>
    .voice-mode-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
    }
    .voice-orb {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 2rem auto;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .voice-orb:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    .voice-orb.recording {
        animation: pulse 1.5s infinite;
        background: linear-gradient(45deg, #ff6b6b 0%, #ee5a24 100%);
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .voice-controls {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
    }
    .voice-status {
        font-size: 1.2rem;
        margin: 1rem 0;
        color: #666;
    }
    .conversation-summary {
        max-width: 800px;
        margin: 2rem auto;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        text-align: left;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="voice-mode-container">', unsafe_allow_html=True)

    # Voice status
    if st.session_state.get('is_recording', False):
        st.markdown(
            '<div class="voice-status">🎤 Listening... Speak naturally!</div>',
            unsafe_allow_html=True,
        )
    elif st.session_state.get('is_processing', False):
        st.markdown(
            '<div class="voice-status">🔄 Processing your voice...</div>',
            unsafe_allow_html=True,
        )
    elif st.session_state.get('is_speaking', False):
        st.markdown(
            '<div class="voice-status">🔊 Maya is speaking...</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="voice-status">🎙️ Voice mode active - automatic speech detection</div>',
            unsafe_allow_html=True,
        )

    # Show last transcription if available
    if (
        'last_transcription' in st.session_state
        and st.session_state.last_transcription
    ):
        st.markdown(
            f'<div class="voice-status" style="color: #28a745;">Last heard: "{st.session_state.last_transcription}"</div>',
            unsafe_allow_html=True,
        )

    # Voice orb (main interaction element) - always active in voice mode
    orb_class = 'voice-orb recording'  # Always show as recording in voice mode
    orb_icon = '🎤'  # Always show microphone icon

    st.markdown(
        f"""
    <div class="{orb_class}">
        <span style="font-size: 4rem;">{orb_icon}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Voice controls - only show when Maya is speaking
    if st.session_state.get('is_speaking', False):
        st.markdown('<div class="voice-controls">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button(
                '🔇 Stop Speaking',
                key='stop_speaking',
                use_container_width=True,
            ):
                if tts_interface:
                    tts_interface.stop_speaking()
                    st.session_state['is_speaking'] = False
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Auto-recording info
    st.markdown('---')
    st.info(
        '� Voice mode is active - speak naturally and your voice will be automatically detected and transcribed'
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Conversation summary (compact view for voice mode)
    if chat_history:
        st.markdown('### 📝 Conversation Summary')
        with st.expander('View conversation history', expanded=False):
            for i, (user_msg, bot_msg, structured_data) in enumerate(
                chat_history[-5:]
            ):  # Show last 5 exchanges
                st.markdown(f'**You:** {user_msg}')
                st.markdown(
                    f'**Maya:** {bot_msg[:200]}{"..." if len(bot_msg) > 200 else ""}'
                )
                st.markdown('---')


def render_mode_selector():
    """Render the mode selection interface"""
    st.sidebar.markdown('### 🎛️ Interface Mode')

    mode = st.sidebar.radio(
        'Choose your preferred mode:',
        options=['text', 'voice'],
        format_func=lambda x: '💬 Text Mode'
        if x == 'text'
        else '🎤 Voice Mode',
        key='interface_mode',
    )

    if mode == 'voice':
        st.sidebar.markdown("""
        **Voice Mode Features:**
        - 🎤 Voice input with microphone
        - 🔊 Audio responses from Maya
        - 🎯 ChatGPT-like interface
        - 📝 Conversation summary
        """)

        # Microphone permission check
        st.sidebar.markdown('**🔒 Permissions:**')
        if st.sidebar.button('🎤 Test Microphone'):
            from .voice_interface import check_microphone_permission

            if check_microphone_permission():
                st.sidebar.success('✅ Microphone access granted')
            else:
                st.sidebar.error('❌ Microphone access denied')
                st.sidebar.markdown(
                    'Please enable microphone access in your browser settings.'
                )

    return mode


def display_mock_data(mock_data: Dict[str, Any]):
    """Display mock data in a formatted way"""
    st.write(f'**Data Type:** {mock_data.get("data_type", "Unknown")}')
    st.write(f'**Count:** {mock_data.get("count", 0)} entries')
    st.write(f'**Format:** {mock_data.get("output_format", "json").upper()}')

    if mock_data.get('ai_enhanced'):
        st.success('🤖 AI Enhanced with recommended fields')

    # Show generated data
    generated_data = mock_data.get('generated_data', [])
    if generated_data:
        output_format = mock_data.get('output_format', 'json').lower()
        data_type = mock_data.get('data_type', 'data')

        # Create unique identifier for this data instance
        unique_id = f'{data_type}_{hash(str(generated_data))}'

        if output_format == 'json':
            st.json(generated_data)
        elif output_format == 'csv':
            df = pd.DataFrame(generated_data)
            st.dataframe(df, use_container_width=True)

            # Download button for CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label='📥 Download CSV',
                data=csv,
                file_name=f'{data_type}.csv',
                mime='text/csv',
                key=f'csv_download_{unique_id}',
            )
        elif output_format == 'table':
            df = pd.DataFrame(generated_data)
            st.dataframe(df, use_container_width=True)

            # Download button for table as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label='📥 Download as CSV',
                data=csv,
                file_name=f'{data_type}_table.csv',
                mime='text/csv',
                key=f'table_download_{unique_id}',
            )
        elif output_format == 'xml':
            # Generate XML format
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml_content += f'<{data_type}s>\n'

            for item in generated_data:
                xml_content += f'  <{data_type}>\n'
                for key, value in item.items():
                    # Escape XML special characters
                    escaped_value = (
                        str(value)
                        .replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;')
                        .replace('"', '&quot;')
                        .replace("'", '&apos;')
                    )
                    xml_content += f'    <{key}>{escaped_value}</{key}>\n'
                xml_content += f'  </{data_type}>\n'

            xml_content += f'</{data_type}s>'

            st.code(xml_content, language='xml')

            # Download button for XML
            st.download_button(
                label='📥 Download XML',
                data=xml_content,
                file_name=f'{data_type}.xml',
                mime='application/xml',
                key=f'xml_download_{unique_id}',
            )
        else:
            st.code(json.dumps(generated_data, indent=2), language='json')


def display_guide_data(guide_data: Dict[str, Any]):
    """Display guide data in a formatted way"""
    st.write(f'**Title:** {guide_data.get("title", "Untitled")}')
    st.write(f'**Category:** {guide_data.get("category", "General")}')
    st.write(
        f'**Difficulty:** {guide_data.get("difficulty_level", "intermediate").title()}'
    )

    if guide_data.get('estimated_time'):
        st.write(f'**Estimated Time:** {guide_data["estimated_time"]}')

    if guide_data.get('prerequisites'):
        st.write('**Prerequisites:**')
        for prereq in guide_data['prerequisites']:
            st.write(f'• {prereq}')

    if guide_data.get('tools_required'):
        st.write('**Tools Required:**')
        for tool in guide_data['tools_required']:
            st.write(f'• {tool}')

    st.write('**Steps:**')
    for i, step in enumerate(guide_data.get('guide_steps', []), 1):
        st.write(f'{i}. {step}')


def render_sidebar_info():
    """Render sidebar information"""
    st.sidebar.header('🔧 Features')
    st.sidebar.markdown("""
    **Maya can help you with:**
    - 📚 Step-by-step guides and tutorials
    - 📊 Mock data generation (various formats)
    - 💬 General FAQ questions

    **Supported Data Types:**
    - Users, Products, Orders
    - Employees, Custom data
    - Multiple output formats (JSON, CSV, XML, etc.)
    """)


def render_custom_css():
    """Render custom CSS styles"""
    st.markdown(
        """
    <style>
    .main-header {
        text-align: center;
        color: #2E86C1;
        padding: 1rem 0;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: right;
    }
    .bot-message {
        background-color: #e9ecef;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: left;
    }
    .json-display {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 1rem;
        font-family: monospace;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
