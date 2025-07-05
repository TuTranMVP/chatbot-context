"""
UI Components for Maya Chatbot
Contains both text and voice mode interfaces
"""

from typing import Any, Callable, Dict, List

import pandas as pd
import streamlit as st


def render_text_mode_ui(
    chat_history: List, handle_user_input_callback: Callable
):
    """Render the minimalist text-based chat interface"""

    # Chat history display with improved styling
    chat_container = st.container()
    with chat_container:
        if chat_history:
            # Show only recent conversations (last 10) for better performance
            recent_history = (
                chat_history[-10:] if len(chat_history) > 10 else chat_history
            )

            for i, (user_msg, bot_msg, structured_data) in enumerate(
                recent_history
            ):
                # User message with clean styling
                st.markdown(
                    f'<div class="user-message">👤 {user_msg}</div>',
                    unsafe_allow_html=True,
                )

                # Bot message with clean styling
                st.markdown(
                    f'<div class="bot-message">🤖 {bot_msg}</div>',
                    unsafe_allow_html=True,
                )

                # Compact structured data display
                if structured_data:
                    response_type = structured_data.get('type', 'unknown')
                    with st.expander(
                        f'� {response_type.title()}', expanded=False
                    ):
                        if response_type == 'mock_data':
                            display_mock_data_compact(structured_data)
                        elif response_type == 'guide':
                            display_guide_data_compact(structured_data)
                        else:
                            st.json(structured_data)

            # Show conversation count if truncated
            if len(chat_history) > 10:
                st.caption(
                    f'Showing last 10 of {len(chat_history)} conversations'
                )
        else:
            # Welcome message with clean design
            st.markdown(
                """
                <div class="welcome-message">
                    <h3>👋 Welcome to Maya</h3>
                    <p>Your AI assistant for guides, data generation, and more!</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Minimalist input area
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.text_input(
        'Message Maya...',
        placeholder='Ask about guides, generate data, or anything else...',
        key='user_input',
        label_visibility='collapsed',
        on_change=handle_user_input_callback,
    )
    st.markdown('</div>', unsafe_allow_html=True)


def render_voice_mode_ui(
    chat_history: List,
    voice_interface,
    tts_interface,
    handle_voice_input_callback: Callable,
):
    """Render the minimalist voice-based chat interface"""

    # Simplified voice status display
    status_container = st.container()
    with status_container:
        if st.session_state.get('is_recording', False):
            st.markdown(
                '<div class="voice-status listening">🎤 Listening...</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.get('is_processing', False):
            st.markdown(
                '<div class="voice-status processing">⚡ Processing...</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.get('is_speaking', False):
            st.markdown(
                '<div class="voice-status speaking">🔊 Maya is speaking...</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="voice-status ready">🎙️ Ready to listen</div>',
                unsafe_allow_html=True,
            )

    # Simplified voice orb
    st.markdown(
        """
        <div class="voice-orb-container">
            <div class="voice-orb">
                <span class="orb-icon">🎤</span>
            </div>
            <p class="voice-hint">Speak naturally - I'm listening</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show last heard message (compact)
    if (
        'last_transcription' in st.session_state
        and st.session_state.last_transcription
    ):
        st.markdown(
            f'<div class="last-heard">💬 "{st.session_state.last_transcription}"</div>',
            unsafe_allow_html=True,
        )

    # Simple stop button when speaking
    if st.session_state.get('is_speaking', False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                '🔇 Stop', key='stop_speaking', use_container_width=True
            ):
                if tts_interface:
                    tts_interface.stop_speaking()
                    st.session_state['is_speaking'] = False
                    st.rerun()

    # Compact conversation history
    if chat_history:
        with st.expander('💬 Recent conversations', expanded=False):
            # Show only last 3 conversations
            for user_msg, bot_msg, _ in chat_history[-3:]:
                st.markdown(f'**You:** {user_msg}')
                # Truncate long responses
                display_msg = (
                    bot_msg[:150] + '...' if len(bot_msg) > 150 else bot_msg
                )
                st.markdown(f'**Maya:** {display_msg}')
                st.markdown('---')


def render_mode_selector():
    """Render the simplified mode selection interface"""

    # Clean mode selector without excessive info
    mode = st.radio(
        '🎛️ Interface Mode',
        options=['text', 'voice'],
        format_func=lambda x: '💬 Text' if x == 'text' else '🎤 Voice',
        key='interface_mode',
        horizontal=True,
    )

    # Show brief help based on selected mode
    if mode == 'voice':
        st.caption(
            '🎤 Voice mode: Speak naturally, Maya will respond with voice'
        )

        # Simple microphone test
        if st.button('🔍 Test Mic', help='Check microphone access'):
            from .voice_interface import check_microphone_permission

            if check_microphone_permission():
                st.success('✅ Microphone ready')
            else:
                st.error('❌ Microphone access needed')
    else:
        st.caption(
            '💬 Text mode: Type your messages and get instant responses'
        )

    return mode


def display_mock_data_compact(mock_data: Dict[str, Any]):
    """Display mock data in a compact, user-friendly way"""

    # Quick info summary
    data_type = mock_data.get('data_type', 'Unknown')
    count = mock_data.get('count', 0)
    output_format = mock_data.get('output_format', 'json').upper()

    st.markdown(
        f'**📊 {data_type}** • {count} entries • {output_format} format'
    )

    if mock_data.get('ai_enhanced'):
        st.success('🤖 AI Enhanced')

    # Show generated data with minimal styling
    generated_data = mock_data.get('generated_data', [])
    if generated_data:
        # Create unique identifier
        unique_id = f'{data_type}_{hash(str(generated_data))}'

        # Display based on format preference
        if output_format.lower() in ['csv', 'table']:
            df = pd.DataFrame(generated_data)
            st.dataframe(df, use_container_width=True, height=200)

            # Simple download button
            csv = df.to_csv(index=False)
            st.download_button(
                '📥 Download',
                data=csv,
                file_name=f'{data_type}.csv',
                mime='text/csv',
                key=f'download_{unique_id}',
            )
        else:
            # Show JSON in collapsed state by default
            with st.expander('View raw data', expanded=False):
                st.json(generated_data)


def display_guide_data_compact(guide_data: Dict[str, Any]):
    """Display guide data in a compact, user-friendly way"""

    title = guide_data.get('title', 'Untitled')
    category = guide_data.get('category', 'General')
    difficulty = guide_data.get('difficulty_level', 'intermediate').title()

    # Quick summary
    st.markdown(f'**📚 {title}** • {category} • {difficulty}')

    if guide_data.get('estimated_time'):
        st.caption(f'⏱️ {guide_data["estimated_time"]}')

    # Show steps in a clean format
    steps = guide_data.get('guide_steps', [])
    if steps:
        with st.expander('� View steps', expanded=True):
            for i, step in enumerate(steps, 1):
                st.markdown(f'{i}. {step}')

    # Show prerequisites and tools if available
    if guide_data.get('prerequisites') or guide_data.get('tools_required'):
        with st.expander('🔧 Requirements', expanded=False):
            if guide_data.get('prerequisites'):
                st.markdown('**Prerequisites:**')
                for prereq in guide_data['prerequisites']:
                    st.markdown(f'• {prereq}')

            if guide_data.get('tools_required'):
                st.markdown('**Tools:**')
                for tool in guide_data['tools_required']:
                    st.markdown(f'• {tool}')


def render_sidebar_info():
    """Render minimal sidebar information"""
    st.sidebar.markdown('### 🤖 Maya Features')
    st.sidebar.markdown("""
    📚 **Guides & Tutorials**  
    📊 **Data Generation**  
    💬 **General Q&A**
    """)

    # Quick data types reference
    with st.sidebar.expander('📊 Data Types', expanded=False):
        st.markdown("""
        • Users, Products, Orders
        • Employees, Custom data  
        • JSON, CSV, XML formats
        """)


def render_custom_css():
    """Render modern, minimalist CSS styles with Space Grotesk font"""
    st.markdown(
        """
    <!-- Google Fonts Import -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* Global font family - Space Grotesk */
    .stApp, .main, .stMarkdown, .stText, .stTextInput, .stSelectbox, .stRadio {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Main chat styles - clean and modern */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        text-align: right;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        max-width: 80%;
        margin-left: auto;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 400;
    }
    
    .bot-message {
        background: #f8f9fa;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        text-align: left;
        border: 1px solid #e9ecef;
        max-width: 80%;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* Welcome message styling */
    .welcome-message {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        margin: 1rem 0;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .welcome-message h3 {
        color: #333;
        margin-bottom: 0.5rem;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 1.5rem;
    }
    
    .welcome-message p {
        color: #666;
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 400;
        font-size: 1rem;
    }
    
    /* Input container styling */
    .input-container {
        margin-top: 1rem;
        padding: 1rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Voice mode styles - simplified */
    .voice-status {
        text-align: center;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 500;
        border-radius: 12px;
        margin: 1rem 0;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .voice-status.listening {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        animation: pulse 2s infinite;
    }
    
    .voice-status.processing {
        background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%);
        color: white;
    }
    
    .voice-status.speaking {
        background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
        color: white;
    }
    
    .voice-status.ready {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Voice orb - cleaner design */
    .voice-orb-container {
        text-align: center;
        padding: 2rem 0;
    }
    
    .voice-orb {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .orb-icon {
        font-size: 2.5rem;
    }
    
    .voice-hint {
        color: #666;
        font-size: 0.9rem;
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 400;
    }
    
    /* Last heard message */
    .last-heard {
        text-align: center;
        padding: 0.5rem 1rem;
        background: #e8f5e8;
        border-radius: 20px;
        margin: 1rem auto;
        max-width: 400px;
        color: #2e7d32;
        font-style: italic;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 400;
    }
    
    /* Animations */
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.02); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Clean expander styling */
    .streamlit-expanderHeader {
        font-weight: 500;
        font-size: 0.9rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Button styling */
    .stButton > button {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-j5r0tf {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 400;
        border-radius: 12px;
        border: 2px solid #e9ecef;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Radio button styling */
    .stRadio > div {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
    }
    
    /* Hide default streamlit elements for cleaner look */
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
    .stDecoration {display: none;}
    </style>
    """,
        unsafe_allow_html=True,
    )
