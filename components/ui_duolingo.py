"""
Duolingo-Inspired UI Components for Maya Chatbot
Modern, playful, button-focused interface
"""

from typing import Any, Dict

import pandas as pd
import streamlit as st


def render_duolingo_landing():
    """Render Duolingo-inspired landing page"""
    st.markdown(
        """
        <div class="duolingo-landing">
            <div class="hero-section">
                <div class="maya-mascot">🤖</div>
                <h1 class="hero-title">Maya AI Assistant</h1>
                <p class="hero-subtitle">Free. Fun. Effective.</p>
                <div class="hero-stats">
                    <div class="stat-item">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Available</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">∞</div>
                        <div class="stat-label">Questions</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">🚀</div>
                        <div class="stat-label">Fast</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_duolingo_chat_mode():
    """Render Duolingo-inspired chat interface"""
    
    # Header navigation for chat mode
    st.markdown('<div class="chat-mode-header">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button('🏠 Home', key='home_chat_btn', use_container_width=True):
            st.session_state['current_mode'] = 'landing'
            st.rerun()
    
    with col2:
        if st.button('📁 Files', key='files_chat_btn', use_container_width=True):
            st.session_state['current_mode'] = 'files'
            st.rerun()
    
    with col3:
        st.markdown(
            '<div class="chat-header-title">💬 Chat Mode</div>',
            unsafe_allow_html=True,
        )
    
    with col4:
        if st.button('🎤 Voice', key='voice_chat_btn', use_container_width=True):
            st.session_state['current_mode'] = 'voice'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat history
    if st.session_state.get('chat_history'):
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for (
            user_msg,
            bot_response,
            structured_data,
        ) in st.session_state.chat_history:
            # User message
            with st.chat_message('user'):
                st.write(user_msg)

            # Bot response
            with st.chat_message('assistant'):
                st.write(bot_response)

                # Display structured data if available
                if structured_data:
                    if structured_data.get('data_type') == 'guide':
                        display_duolingo_guide(structured_data)
                    elif structured_data.get('data_type') in [
                        'data',
                        'user_data',
                        'product_data',
                    ]:
                        display_duolingo_data(structured_data)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Welcome message
        st.markdown(
            """
            <div class="welcome-message">
                <div class="maya-mascot">🤖</div>
                <h3>Hi! I'm Maya, your AI assistant!</h3>
                <p>Ask me anything or use the buttons below to get started.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Text input
    user_input = st.chat_input('Type your message here...', key='chat_input')
    if user_input:
        st.session_state['user_input'] = user_input
        st.session_state['suggestion_clicked'] = True

    st.markdown('</div>', unsafe_allow_html=True)


def render_duolingo_voice_mode():
    """Render Duolingo-inspired voice interface"""
    
    # Header navigation for voice mode
    st.markdown('<div class="voice-mode-header">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button('🏠 Home', key='home_voice_btn', use_container_width=True):
            st.session_state['current_mode'] = 'landing'
            st.rerun()

    with col2:
        if st.button('📁 Files', key='files_voice_btn', use_container_width=True):
            st.session_state['current_mode'] = 'files'
            st.rerun()

    with col3:
        st.markdown(
            '<div class="voice-header-title">🎤 Voice Mode</div>',
            unsafe_allow_html=True,
        )

    with col4:
        if st.button('💬 Chat', key='chat_voice_btn', use_container_width=True):
            st.session_state['current_mode'] = 'chat'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Voice status with playful design
    status = get_voice_status()
    st.markdown(
        f"""
        <div class="voice-status-duolingo">
            <div class="status-card {status['class']}">
                <div class="status-icon">{status['icon']}</div>
                <div class="status-text">{status['text']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Large voice button (Duolingo style)
    st.markdown(
        """
        <div class="voice-action-center">
            <div class="voice-orb-duolingo">
                <div class="orb-pulse"></div>
                <div class="orb-icon">🎤</div>
            </div>
            <p class="voice-instruction">Tap and speak!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Voice control buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.session_state.get('is_speaking', False):
            if st.button(
                '🔇 Stop Speaking', key='stop_voice', use_container_width=True
            ):
                # Stop TTS logic here
                st.session_state['is_speaking'] = False
                st.rerun()
        elif st.session_state.get('is_recording', False):
            if st.button(
                '⏹️ Stop Recording',
                key='stop_recording',
                use_container_width=True,
            ):
                # Stop recording logic here
                st.session_state['is_recording'] = False
                st.rerun()
        else:
            if st.button(
                '🎤 Start Recording',
                key='start_recording',
                use_container_width=True,
            ):
                # Start recording logic here
                st.session_state['is_recording'] = True
                st.rerun()

    # Chat history (same as text mode but with voice indicators)
    if st.session_state.get('chat_history'):
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for (
            user_msg,
            bot_response,
            structured_data,
        ) in st.session_state.chat_history:
            # User message with voice indicator
            with st.chat_message('user'):
                st.write(f'🎤 {user_msg}')

            # Bot response
            with st.chat_message('assistant'):
                st.write(bot_response)

                # Display structured data if available
                if structured_data:
                    if structured_data.get('data_type') == 'guide':
                        display_duolingo_guide(structured_data)
                    elif structured_data.get('data_type') in [
                        'data',
                        'user_data',
                        'product_data',
                    ]:
                        display_duolingo_data(structured_data)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Welcome message for voice mode
        st.markdown(
            """
            <div class="welcome-message">
                <div class="maya-mascot">🎤</div>
                <h3>Voice mode is ready!</h3>
                <p>Click the microphone button to start speaking with Maya.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def get_voice_status():
    """Get current voice status with appropriate styling"""
    if st.session_state.get('is_recording', False):
        return {'class': 'listening', 'icon': '🔴', 'text': 'Listening...'}
    elif st.session_state.get('is_processing', False):
        return {'class': 'processing', 'icon': '⚡', 'text': 'Processing...'}
    elif st.session_state.get('is_speaking', False):
        return {
            'class': 'speaking',
            'icon': '🔊',
            'text': 'Maya is speaking...',
        }
    else:
        return {'class': 'ready', 'icon': '✨', 'text': 'Ready to chat!'}


def render_quick_suggestions():
    """Render quick suggestion buttons"""
    pass


def render_duolingo_mode_selector():
    """Render Duolingo-style mode selector"""
    st.markdown('<div class="mode-selector-duolingo">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    current_mode = st.session_state.get('interface_mode', 'text')

    with col1:
        text_class = (
            'mode-button active' if current_mode == 'text' else 'mode-button'
        )
        if st.button(
            '💬 Text Chat', key='mode_text', use_container_width=True
        ):
            st.session_state['interface_mode'] = 'text'
            st.rerun()

    with col2:
        voice_class = (
            'mode-button active' if current_mode == 'voice' else 'mode-button'
        )
        if st.button(
            '🎤 Voice Chat', key='mode_voice', use_container_width=True
        ):
            st.session_state['interface_mode'] = 'voice'
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    return current_mode


def display_duolingo_data(data: Dict[str, Any]):
    """Display data in Duolingo card style"""
    data_type = data.get('data_type', 'Data')
    count = data.get('count', 0)
    format_type = data.get('output_format', 'json').upper()

    st.markdown(
        f"""
        <div class="data-card-duolingo">
            <div class="data-header">
                <div class="data-icon">📊</div>
                <div class="data-info">
                    <div class="data-title">{data_type}</div>
                    <div class="data-meta">{count} items • {format_type}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if data.get('ai_enhanced'):
        st.success('🤖 AI Enhanced!')

    # Show generated data
    generated_data = data.get('generated_data', [])
    if generated_data:
        if format_type.lower() in ['csv', 'table']:
            df = pd.DataFrame(generated_data)
            st.dataframe(df, use_container_width=True, height=200)

            # Download button with Duolingo styling
            csv = df.to_csv(index=False)
            st.download_button(
                '📥 Download',
                data=csv,
                file_name=f'{data_type.lower()}.csv',
                mime='text/csv',
                key=f'download_{hash(str(generated_data))}',
                use_container_width=True,
            )


def display_duolingo_guide(guide: Dict[str, Any]):
    """Display guide in Duolingo card style"""
    title = guide.get('title', 'Guide')
    category = guide.get('category', 'General')
    difficulty = guide.get('difficulty_level', 'intermediate').title()

    # Difficulty color mapping
    difficulty_colors = {
        'Beginner': '#58cc02',  # Green
        'Intermediate': '#ff9600',  # Orange
        'Advanced': '#ff4b4b',  # Red
    }

    color = difficulty_colors.get(difficulty, '#ff9600')

    st.markdown(
        f"""
        <div class="guide-card-duolingo">
            <div class="guide-header">
                <div class="guide-icon">📚</div>
                <div class="guide-info">
                    <div class="guide-title">{title}</div>
                    <div class="guide-meta">
                        <span class="guide-category">{category}</span>
                        <span class="guide-difficulty" style="background-color: {color};">
                            {difficulty}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if guide.get('estimated_time'):
        st.info(f'⏱️ Estimated time: {guide["estimated_time"]}')

    # Show steps in an expandable section
    steps = guide.get('guide_steps', [])
    if steps:
        with st.expander('📋 View Steps', expanded=True):
            for i, step in enumerate(steps, 1):
                st.markdown(
                    f"""
                    <div class="step-item">
                        <div class="step-number">{i}</div>
                        <div class="step-text">{step}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_duolingo_css():
    """Render Duolingo-inspired CSS styles"""
    st.markdown(
        """
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* Global font and reset */
    * {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Hide Streamlit branding */
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
    .stDecoration {display: none;}
    header[data-testid="stHeader"] {display: none;}
    .stMainBlockContainer {padding-top: 1rem !important;}
    
    /* Dark theme page background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #e0e0e0;
    }
    
    /* Dark theme for main container */
    .main .block-container {
        background: transparent;
        color: #e0e0e0;
    }
    
    /* Dark theme Duolingo-inspired landing page */
    .duolingo-landing {
        text-align: center;
        padding: 3rem 1rem;
        border-radius: 20px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(88, 204, 2, 0.4);
        border: 1px solid rgba(88, 204, 2, 0.3);
    }
    
    .hero-section {
        margin-bottom: 3rem;
    }
    
    .maya-mascot {
        font-size: 5rem;
        margin-bottom: 1rem;
        animation: bounce 2s infinite;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        font-weight: 400;
        opacity: 0.95;
        margin: 0;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Hero stats */
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 2rem;
        flex-wrap: nowrap;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        min-width: 80px;
        transition: all 0.3s ease;
        width: 100%;
        max-width: 95px;
    }
    
    .stat-item:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.25);
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Enhanced animations */
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced Streamlit button styling */
    .stButton > button {
        background: linear-gradient(135deg, #58cc02 0%, #89e219 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        font-weight: 600 !important;
        padding: 1rem 2rem !important;
        transition: all 0.3s ease !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(88, 204, 2, 0.3) !important;
        border: 3px solid transparent !important;
        min-height: 3rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(88, 204, 2, 0.4) !important;
        border-color: #1cb0f6 !important;
        animation: pulse 0.6s ease-in-out !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(88, 204, 2, 0.3) !important;
    }
    
    /* Primary button styling */
    div[data-testid="column"]:first-child .stButton > button {
        background: linear-gradient(135deg, #1cb0f6 0%, #00b4d8 100%) !important;
        box-shadow: 0 4px 15px rgba(28, 176, 246, 0.3) !important;
    }
    
    div[data-testid="column"]:first-child .stButton > button:hover {
        box-shadow: 0 8px 25px rgba(28, 176, 246, 0.4) !important;
    }
    
    /* Secondary button styling (for clear chat, etc.) */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%) !important;
        color: white !important;
        border: 2px solid #ff4757 !important;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #ff3742 0%, #ff5865 100%) !important;
        border-color: #ff3742 !important;
        box-shadow: 0 8px 25px rgba(255, 71, 87, 0.4) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Feature cards styling */
    .feature-grid .stButton > button {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #58cc02 !important;
        border: 2px solid #58cc02 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .feature-grid .stButton > button:hover {
        background: #58cc02 !important;
        color: white !important;
        transform: translateY(-5px) scale(1.02) !important;
    }
    
    /* Navigation buttons */
    .stButton > button[key*="home"] {
        background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%) !important;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3) !important;
    }
    
    .stButton > button[key*="home"]:hover {
        box-shadow: 0 8px 25px rgba(255, 71, 87, 0.4) !important;
    }
    
    /* Dark theme chat interface enhancements */
    .stChatMessage {
        border-radius: 15px !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        animation: slideIn 0.3s ease-out !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #1cb0f6 0%, #00b4d8 100%) !important;
        color: white !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
        color: #e0e0e0 !important;
        border-left: 4px solid #58cc02 !important;
    }
    
    /* Dark theme input styling */
    .stTextInput > div > div > input {
        border-radius: 15px !important;
        border: 2px solid #444 !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
        color: #e0e0e0 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #58cc02 !important;
        box-shadow: 0 0 15px rgba(88, 204, 2, 0.3) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a0a0a0 !important;
    }
    
    /* Dark theme welcome message styling */
    .welcome-message {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%);
        border-radius: 20px;
        margin: 0.5rem 0;
        border: 2px solid #58cc02;
        animation: slideIn 0.8s ease-out;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .welcome-message .maya-mascot {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: bounce 2s infinite;
        filter: drop-shadow(0 4px 8px rgba(88, 204, 2, 0.3));
    }
    
    .welcome-message h3 {
        color: #58cc02;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    .welcome-message p {
        color: #b0b0b0;
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* Dark theme chat container */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem 0;
        scrollbar-width: thin;
        scrollbar-color: #58cc02 #2c2c54;
    }
    
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #2c2c54;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #58cc02;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #45a002;
    }
    
    /* Dark theme suggestions section */
    .suggestions-section {
        margin: 2rem 0;
        padding: 1.5rem;
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%);
        border-radius: 15px;
        border: 1px solid rgba(88, 204, 2, 0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .suggestions-title {
        color: #58cc02;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Voice status styling */
    .voice-status-duolingo {
        text-align: center;
        margin: 2rem 0;
    }
    
    .status-card {
        display: inline-block;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem;
        min-width: 200px;
    }
    
    .status-card.listening {
        background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%);
        color: white;
        animation: pulse 1.5s infinite;
    }
    
    .status-card.processing {
        background: linear-gradient(135deg, #ffa502 0%, #ffb142 100%);
        color: white;
        animation: pulse 2s infinite;
    }
    
    .status-card.speaking {
        background: linear-gradient(135deg, #1cb0f6 0%, #00b4d8 100%);
        color: white;
        animation: pulse 1s infinite;
    }
    
    .status-card.ready {
        background: linear-gradient(135deg, #58cc02 0%, #89e219 100%);
        color: white;
    }
    
    .status-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .status-text {
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Chat mode header styling */
    .chat-mode-header {
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%);
        border-radius: 20px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        border: 2px solid rgba(88, 204, 2, 0.3);
        box-shadow: 0 6px 25px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        animation: headerSlideIn 0.6s ease-out;
    }
    
    .chat-mode-header:hover {
        border-color: rgba(88, 204, 2, 0.5);
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        transform: translateY(-2px);
    }
    
    .chat-header-title {
        text-align: center;
        font-size: 1.4rem;
        font-weight: 600;
        color: #58cc02;
        padding: 0.8rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, #58cc02 0%, #89e219 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: slideIn 0.8s ease-out 0.2s both;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 3rem;
    }
    
    /* Target specific Streamlit column class for chat mode header */
    .chat-mode-header .stColumn.st-emotion-cache-cbquie.e1msl4mp1 {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.5rem !important;
    }
    
    /* Alternative selectors for different Streamlit versions */
    .chat-mode-header [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.5rem !important;
    }
    
    /* Chat mode header buttons */
    .chat-mode-header .stButton > button {
        background: linear-gradient(135deg, #58cc02 0%, #89e219 100%) !important;
        color: white !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
        font-weight: 600 !important;
        padding: 0.8rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(88, 204, 2, 0.3) !important;
        min-height: 3rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        animation: slideIn 0.6s ease-out 0.4s both !important;
        width: 100% !important;
    }
    
    .chat-mode-header .stButton > button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(88, 204, 2, 0.4) !important;
        border-color: #1cb0f6 !important;
        animation: buttonPop 0.3s ease-in-out !important;
    }
    
    .chat-mode-header .stButton > button:active {
        transform: translateY(-1px) scale(1.02) !important;
        transition: all 0.1s ease !important;
    }
    
    /* Specific header button colors */
    .chat-mode-header button[key*="home"] {
        background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%) !important;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3) !important;
    }
    
    .chat-mode-header button[key*="home"]:hover {
        box-shadow: 0 8px 25px rgba(255, 71, 87, 0.4) !important;
        border-color: #ff3742 !important;
    }
    
    .chat-mode-header button[key*="voice"] {
        background: linear-gradient(135deg, #1cb0f6 0%, #00b4d8 100%) !important;
        box-shadow: 0 4px 15px rgba(28, 176, 246, 0.3) !important;
    }
    
    .chat-mode-header button[key*="voice"]:hover {
        box-shadow: 0 8px 25px rgba(28, 176, 246, 0.4) !important;
        border-color: #0099cc !important;
    }
    
    .chat-mode-header button[key*="files"] {
        background: linear-gradient(135deg, #ffa502 0%, #ffb142 100%) !important;
        box-shadow: 0 4px 15px rgba(255, 165, 2, 0.3) !important;
    }
    
    .chat-mode-header button[key*="files"]:hover {
        box-shadow: 0 8px 25px rgba(255, 165, 2, 0.4) !important;
        border-color: #e6940a !important;
    }
    
    /* Voice mode header styling */
    .voice-mode-header {
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%);
        border-radius: 20px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        border: 2px solid rgba(28, 176, 246, 0.3);
        box-shadow: 0 6px 25px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        animation: headerSlideIn 0.6s ease-out;
    }
    
    .voice-mode-header:hover {
        border-color: rgba(28, 176, 246, 0.5);
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        transform: translateY(-2px);
    }
    
    .voice-header-title {
        text-align: center;
        font-size: 1.4rem;
        font-weight: 600;
        color: #1cb0f6;
        padding: 0.8rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, #1cb0f6 0%, #00b4d8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: slideIn 0.8s ease-out 0.2s both;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 3rem;
    }
    
    /* Voice mode header buttons */
    .voice-mode-header .stButton > button {
        background: linear-gradient(135deg, #1cb0f6 0%, #00b4d8 100%) !important;
        color: white !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
        font-weight: 600 !important;
        padding: 0.8rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(28, 176, 246, 0.3) !important;
        min-height: 3rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        animation: slideIn 0.6s ease-out 0.4s both !important;
        width: 100% !important;
    }
    
    .voice-mode-header .stButton > button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(28, 176, 246, 0.4) !important;
        border-color: #58cc02 !important;
        animation: buttonPop 0.3s ease-in-out !important;
    }
    
    .voice-mode-header .stButton > button:active {
        transform: translateY(-1px) scale(1.02) !important;
        transition: all 0.1s ease !important;
    }
    
    /* Specific voice header button colors */
    .voice-mode-header button[key*="home"] {
        background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%) !important;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3) !important;
    }
    
    .voice-mode-header button[key*="home"]:hover {
        box-shadow: 0 8px 25px rgba(255, 71, 87, 0.4) !important;
        border-color: #ff3742 !important;
    }
    
    .voice-mode-header button[key*="files"] {
        background: linear-gradient(135deg, #ffa502 0%, #ffb142 100%) !important;
        box-shadow: 0 4px 15px rgba(255, 165, 2, 0.3) !important;
    }
    
    .voice-mode-header button[key*="files"]:hover {
        box-shadow: 0 8px 25px rgba(255, 165, 2, 0.4) !important;
        border-color: #e6940a !important;
    }
    
    .voice-mode-header button[key*="chat"] {
        background: linear-gradient(135deg, #58cc02 0%, #89e219 100%) !important;
        box-shadow: 0 4px 15px rgba(88, 204, 2, 0.3) !important;
    }
    
    .voice-mode-header button[key*="chat"]:hover {
        box-shadow: 0 8px 25px rgba(88, 204, 2, 0.4) !important;
        border-color: #45a002 !important;
    }
    
    /* Voice action center */
    .voice-action-center {
        text-align: center;
        margin: 3rem 0;
    }
    
    .voice-orb-duolingo {
        position: relative;
        display: inline-block;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #58cc02 0%, #89e219 100%);
        box-shadow: 0 8px 30px rgba(88, 204, 2, 0.3);
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .voice-orb-duolingo:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 40px rgba(88, 204, 2, 0.4);
    }
    
    .orb-icon {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3rem;
        color: white;
    }
    
    .orb-pulse {
        position: absolute;
        top: -10px;
        left: -10px;
        right: -10px;
        bottom: -10px;
        border: 3px solid #58cc02;
        border-radius: 50%;
        animation: pulse-ring 2s infinite;
        opacity: 0;
    }
    
    @keyframes pulse-ring {
        0% {
            transform: scale(0.8);
            opacity: 1;
        }
        100% {
            transform: scale(1.2);
            opacity: 0;
        }
    }
    
    .voice-instruction {
        color: #666;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2rem !important;
        }
        
        .maya-mascot {
            font-size: 3rem !important;
        }
        
        .stButton > button {
            padding: 0.8rem 1.5rem !important;
            font-size: 1rem !important;
        }
        
        .duolingo-landing {
            padding: 2rem 1rem !important;
        }
        
        /* Mobile chat mode header optimization */
        .chat-mode-header {
            padding: 0.8rem !important;
            margin-bottom: 1rem !important;
            border-radius: 15px !important;
        }
        
        .chat-header-title {
            font-size: 1.1rem !important;
            padding: 0.5rem 0 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        
        /* Mobile header buttons optimization */
        .chat-mode-header .stButton > button {
            padding: 0.6rem 0.8rem !important;
            font-size: 1rem !important;
            border-radius: 12px !important;
            min-height: 2.5rem !important;
        }
        
        .chat-mode-header .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(88, 204, 2, 0.4) !important;
        }
        
        /* Specific mobile button optimizations */
        .chat-mode-header button[key*="home"] {
            font-size: 1.2rem !important;
            padding: 0.5rem !important;
        }
        
        .chat-mode-header button[key*="voice"] {
            font-size: 1.2rem !important;
            padding: 0.5rem !important;
        }
        
        .chat-mode-header button[key*="files"] {
            font-size: 1rem !important;
        }
        
        /* Target Streamlit columns in mobile chat header */
        .chat-mode-header .stColumn.st-emotion-cache-cbquie.e1msl4mp1 {
            padding: 0.25rem !important;
        }
        
        .chat-mode-header [data-testid="column"] {
            padding: 0.25rem !important;
        }
        
        /* Mobile voice mode header optimization */
        .voice-mode-header {
            padding: 0.8rem !important;
            margin-bottom: 1rem !important;
            border-radius: 15px !important;
            border-color: rgba(28, 176, 246, 0.4) !important;
        }
        
        .voice-header-title {
            font-size: 1.1rem !important;
            padding: 0.5rem 0 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            color: #1cb0f6 !important;
        }
        
        /* Mobile voice header buttons optimization */
        .voice-mode-header .stButton > button {
            padding: 0.6rem 0.8rem !important;
            font-size: 1rem !important;
            border-radius: 12px !important;
            min-height: 2.5rem !important;
        }
        
        .voice-mode-header .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(28, 176, 246, 0.4) !important;
        }
        
        /* Target Streamlit columns in mobile voice header */
        .voice-mode-header .stColumn.st-emotion-cache-cbquie.e1msl4mp1 {
            padding: 0.25rem !important;
        }
        
        .voice-mode-header [data-testid="column"] {
            padding: 0.25rem !important;
        }
        
        /* Mobile voice status card optimization */
        .voice-status-duolingo {
            margin: 1rem 0 !important;
        }
        
        .status-card {
            padding: 1rem 1.5rem !important;
            min-width: 250px !important;
            border-radius: 15px !important;
        }
        
        .status-icon {
            font-size: 1.8rem !important;
            margin-bottom: 0.3rem !important;
        }
        
        .status-text {
            font-size: 1rem !important;
        }
        
        /* Mobile voice orb optimization */
        .voice-action-center {
            margin: 2rem 0 !important;
        }
        
        .voice-orb-duolingo {
            width: 100px !important;
            height: 100px !important;
            margin-bottom: 0.8rem !important;
        }
        
        .orb-icon {
            font-size: 2.5rem !important;
        }
        
        .voice-instruction {
            font-size: 1rem !important;
            margin-top: 0.5rem !important;
        }
        
        /* Mobile voice control buttons */
        .voice-control-buttons {
            margin: 1.5rem 0 !important;
        }
        
        .voice-control-buttons .stButton > button {
            padding: 0.8rem 1rem !important;
            font-size: 1rem !important;
            min-height: 2.5rem !important;
            border-radius: 12px !important;
        }
        
        /* Compact header for very small screens */
        @media (max-width: 480px) {
            .chat-mode-header {
                padding: 0.5rem !important;
                margin-bottom: 0.8rem !important;
            }
            
            .chat-header-title {
                font-size: 1rem !important;
                padding: 0.3rem 0 !important;
            }
            
            .chat-mode-header .stButton > button {
                font-size: 0.9rem !important;
                padding: 0.4rem 0.6rem !important;
                min-height: 2rem !important;
            }
            
            .chat-mode-header button[key*="home"],
            .chat-mode-header button[key*="voice"] {
                font-size: 1rem !important;
                padding: 0.4rem !important;
            }
            
            /* Voice mode compact */
            .voice-mode-header {
                padding: 0.5rem !important;
                margin-bottom: 0.8rem !important;
            }
            
            .voice-header-title {
                font-size: 1rem !important;
                padding: 0.3rem 0 !important;
            }
            
            .voice-mode-header .stButton > button {
                font-size: 0.9rem !important;
                padding: 0.4rem 0.6rem !important;
                min-height: 2rem !important;
            }
            
            /* Voice orb ultra compact */
            .voice-orb-duolingo {
                width: 80px !important;
                height: 80px !important;
            }
            
            .orb-icon {
                font-size: 2rem !important;
            }
            
            .status-card {
                padding: 0.8rem 1rem !important;
                min-width: 200px !important;
                font-size: 0.9rem !important;
            }
            
            .status-icon {
                font-size: 1.5rem !important;
            }
            
            .voice-instruction {
                font-size: 0.9rem !important;
            }
        }
        
        /* Mobile optimization for Streamlit horizontal blocks */
        .stHorizontalBlock {
            gap: 0.5rem !important;
        }
        
        .stHorizontalBlock > div {
            width: 100% !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Mobile optimization for column layouts */
        .stColumns {
            flex-direction: column !important;
            gap: 0.5rem !important;
        }
        
        .stColumns > div {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Stack navigation buttons vertically on mobile */
        div[data-testid="column"]:has(button[key*="home"]) {
            order: 1 !important;
        }
        
        div[data-testid="column"]:has(button[key*="files"]) {
            order: 3 !important;
        }
        
        div[data-testid="column"]:has(button[key*="voice"]) {
            order: 4 !important;
        }
        
        div[data-testid="column"]:has(button[key*="chat"]) {
            order: 4 !important;
        }
        
        /* Hero stats mobile optimization */
        .hero-stats {
                align-items: center !important;
            gap: 1rem !important;
        }
        
        .stat-item {
            width: 80% !important;
            max-width: 200px !important;
        }
        
        /* Voice orb mobile optimization */
        .voice-orb-duolingo {
            width: 100px !important;
            height: 100px !important;
        }
        
        .orb-icon {
            font-size: 2.5rem !important;
        }
        
        /* Landing page button optimization */
        .stColumns > div .stButton > button {
            min-height: 2.5rem !important;
            font-size: 0.95rem !important;
            white-space: nowrap !important;
        }
        
        /* Mobile chat optimization */
        .chat-container {
            max-height: 400px !important;
            padding: 0.5rem 0 !important;
        }
        
        .stChatMessage {
            margin: 0.3rem 0 !important;
            padding: 0.8rem !important;
            border-radius: 10px !important;
        }
        
        /* Mobile card optimization */
        .data-card-duolingo, .guide-card-duolingo {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .data-header, .guide-header {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 0.5rem !important;
        }
        
        .data-icon, .guide-icon {
            font-size: 1.5rem !important;
            align-self: center !important;
        }
        
        .data-title, .guide-title {
            font-size: 1.1rem !important;
            text-align: center !important;
        }
        
        .data-meta, .guide-meta {
            text-align: center !important;
            font-size: 0.8rem !important;
        }
        
        /* Mobile welcome message */
        .welcome-message {
            padding: 2rem 1rem !important;
            margin: 1rem 0 !important;
        }
        
        .welcome-message .maya-mascot {
            font-size: 3rem !important;
        }
        
        .welcome-message h3 {
            font-size: 1.3rem !important;
        }
        
        .welcome-message p {
            font-size: 1rem !important;
        }
        
        /* Mobile status card */
        .status-card {
            padding: 1rem !important;
            min-width: 150px !important;
        }
        
        .status-icon {
            font-size: 1.5rem !important;
        }
        
        .status-text {
            font-size: 1rem !important;
        }
        
        /* Mobile dataframe */
        .stDataFrame {
            font-size: 0.8rem !important;
        }
    }
    
    /* Tablet optimization */
    @media (max-width: 1024px) and (min-width: 769px) {
        /* Chat header tablet optimization */
        .chat-mode-header {
            padding: 1rem;
            margin-bottom: 1.2rem;
        }
        
        .chat-header-title {
            font-size: 1.2rem;
            padding: 0.6rem 0;
        }
        
        .chat-mode-header .stButton > button {
            font-size: 1rem !important;
            padding: 0.7rem 1.2rem !important;
            min-height: 2.5rem !important;
        }
    }
    
    /* Hide Streamlit menu */
    #MainMenu {visibility: hidden;}
    
    /* Custom spacing */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Loading spinner customization */
    .stSpinner {
        color: #58cc02 !important;
    }
    
    /* Dark theme dataframe styling */
    .stDataFrame {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
    }
    
    .stDataFrame > div {
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
        color: #e0e0e0 !important;
    }
    
    /* Dark theme expander styling */
    .stExpander {
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
        border: 1px solid rgba(88, 204, 2, 0.3) !important;
        border-radius: 15px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
    }
    
    .stExpander > div > div {
        background: transparent !important;
        color: #e0e0e0 !important;
    }
    
    .streamlit-expanderHeader {
        background: transparent !important;
        color: #58cc02 !important;
        font-weight: 600 !important;
    }
    
    /* Dark theme data and guide cards */
    .data-card-duolingo, .guide-card-duolingo {
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 6px 25px rgba(0,0,0,0.3) !important;
        border-left: 5px solid #58cc02 !important;
        transition: all 0.3s ease !important;
        animation: slideIn 0.5s ease-out !important;
        color: #e0e0e0 !important;
    }
    
    .data-card-duolingo:hover, .guide-card-duolingo:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 10px 35px rgba(0,0,0,0.4) !important;
        border-left-color: #89e219 !important;
    }
    
    .data-header, .guide-header {
        color: #e0e0e0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 1rem !important;
    }
    
    .data-title, .guide-title {
        color: #58cc02 !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        margin: 0 !important;
    }
    
    .data-meta, .guide-meta {
        color: #b0b0b0 !important;
        font-size: 0.9rem !important;
        margin: 0.5rem 0 0 0 !important;
    }
    
    .data-icon, .guide-icon {
        filter: drop-shadow(0 2px 4px rgba(88, 204, 2, 0.3)) !important;
        font-size: 2rem !important;
        flex-shrink: 0 !important;
    }
    
    .data-info, .guide-info {
        flex: 1 !important;
    }
    
    /* Dark theme success messages */
    .stSuccess {
        border-radius: 15px !important;
        border-left: 5px solid #58cc02 !important;
        animation: slideIn 0.5s ease-out !important;
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
        color: #58cc02 !important;
    }
    
    .stSuccess > div {
        background: transparent !important;
        color: #58cc02 !important;
    }
    
    /* Dark theme info messages */
    .stInfo {
        border-radius: 15px !important;
        border-left: 5px solid #1cb0f6 !important;
        animation: slideIn 0.5s ease-out !important;
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
        color: #1cb0f6 !important;
    }
    
    .stInfo > div {
        background: transparent !important;
        color: #1cb0f6 !important;
    }
    
    /* Dark theme voice instruction */
    .voice-instruction {
        color: #b0b0b0 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }
    
    /* Dark theme step items */
    .step-item {
        background: rgba(88, 204, 2, 0.1) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        border-left: 3px solid #58cc02 !important;
    }
    
    .step-number {
        background: #58cc02 !important;
        color: white !important;
        border-radius: 50% !important;
        width: 30px !important;
        height: 30px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 600 !important;
        margin-right: 1rem !important;
    }
    
    .step-text {
        color: #e0e0e0 !important;
        flex: 1 !important;
    }
    
    /* Dark theme captions */
    .stCaption {
        color: #b0b0b0 !important;
    }
    
    /* Dark theme sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    /* Dark theme radio buttons */
    .stRadio > div > label {
        color: #e0e0e0 !important;
    }
    
    .stRadio > div > label > div {
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
        border: 2px solid #58cc02 !important;
    }
    
    /* Dark theme selectbox */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #2c2c54 0%, #40407a 100%) !important;
        color: #e0e0e0 !important;
        border: 2px solid #444 !important;
    }
    
    </style>
        """,
        unsafe_allow_html=True,
    )
