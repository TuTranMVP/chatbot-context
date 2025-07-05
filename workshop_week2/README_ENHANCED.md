# Maya Advanced FAQ Chatbot with Voice & Text Interface

A sophisticated conversational AI chatbot with dual-mode functionality - traditional text chat and modern voice interaction (ChatGPT-like interface).

## 🌟 Features

### Text Mode (Traditional Chat)
- 💬 Real-time text conversation
- 📚 Step-by-step guide generation
- 📊 Mock data generation with multiple formats
- 💡 General FAQ responses
- 📋 Full conversation history
- 🔄 Interactive data display and downloads

### Voice Mode (ChatGPT-like Interface)
- 🎤 Voice input with microphone access
- 🔊 Text-to-speech responses
- 🎯 Elegant circular voice interface
- 📝 Compact conversation summary
- ⚡ Real-time speech-to-text conversion
- 🎛️ Voice controls (start/stop recording)

## 🏗️ Architecture

The application is built with a modular architecture for easy maintenance:

```
chatbot-contextt/workshop_week2/
├── components/
│   ├── __init__.py              # Package initialization & documentation
│   ├── chatbot_core.py          # Core chatbot logic and OpenAI integration
│   ├── voice_interface.py       # Speech-to-text functionality
│   ├── tts_interface.py         # Text-to-speech functionality
│   └── ui_components.py         # UI rendering components
├── streamlit_chatbot.py         # Main application entry point
└── requirements.txt             # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Voice Features Setup

#### Windows:
```bash
# Install PyAudio for microphone access
pip install pipwin
pipwin install pyaudio

# Alternative with conda
conda install pyaudio
```

#### macOS:
```bash
brew install portaudio
pip install pyaudio
```

#### Linux:
```bash
sudo apt-get install python3-pyaudio
pip install pyaudio
```

### 3. Configure OpenAI

Update the OpenAI configuration in `components/chatbot_core.py`:
```python
return openai.AzureOpenAI(
    api_version="your-api-version",
    azure_endpoint="your-azure-endpoint", 
    api_key="your-api-key",
)
```

### 4. Run the Application

```bash
streamlit run streamlit_chatbot.py
```

## 🎯 Usage Guide

### Text Mode
1. Select "💬 Text Mode" from the sidebar
2. Type your questions in the input field
3. Press Enter to send
4. View responses and structured data
5. Download generated data in various formats

### Voice Mode
1. Select "🎤 Voice Mode" from the sidebar
2. Grant microphone permissions when prompted
3. Click the voice orb or "Start Recording" to begin
4. Speak your question clearly
5. Click "Stop Recording" when finished
6. Listen to Maya's voice response

## 🎛️ Features in Detail

### Supported Query Types

#### Guide Generation
- **Triggers**: "how to", "steps to", "guide me through", "tutorial for"
- **Output**: Structured step-by-step instructions
- **Example**: "How to create a React app"

#### Mock Data Generation
- **Triggers**: "generate data", "mock data", "sample users"
- **Formats**: JSON, CSV, XML, SQL, YAML, Table
- **Types**: Users, Products, Orders, Employees, Custom
- **Example**: "Generate 10 sample users in CSV format"

#### General FAQ
- **Triggers**: "what is", "tell me about", "explain", "compare"
- **Output**: Informational responses with related topics
- **Example**: "What is machine learning?"

### Voice Controls

| Control | Action |
|---------|--------|
| 🎤 Voice Orb | Visual indicator of recording state |
| ▶️ Start Recording | Begin continuous voice recording |
| ⏹️ Stop Recording | End recording and process speech |
| 🎙️ Single Question | Record one phrase quickly |
| 🔇 Stop Speaking | Interrupt Maya's voice response |

## 🔧 Customization

### Adding New Response Types
1. Define function schema in `chatbot_core.py`
2. Implement processing method in `MayaChatbot` class
3. Add formatting logic in `format_response()`
4. Update UI components if needed

### Modifying Voice Settings
Edit TTS settings in `components/tts_interface.py`:
```python
self.engine.setProperty('rate', 150)    # Speech speed
self.engine.setProperty('volume', 0.8)  # Volume level
```

### Customizing UI Themes
Modify CSS styles in `components/ui_components.py`:
```python
def render_custom_css():
    st.markdown("""
    <style>
    .voice-orb {
        background: linear-gradient(45deg, #your-colors);
        # Your custom styles
    }
    </style>
    """, unsafe_allow_html=True)
```

## 🌐 Browser Compatibility

### Voice Mode Requirements
- **Secure Context**: HTTPS or localhost required for microphone access
- **Supported Browsers**: Chrome, Firefox, Safari, Edge
- **Permissions**: Microphone access must be granted

### Troubleshooting Voice Issues

#### Microphone Problems
1. Check browser permissions for microphone
2. Ensure microphone isn't used by other applications
3. Use "Test Microphone" button in sidebar
4. Try refreshing and re-granting permissions

#### Audio Playback Issues
1. Check system audio settings
2. Ensure speakers/headphones are connected
3. Try different browsers if audio fails
4. Check volume levels

## 📱 Mobile Support

- **Text Mode**: Fully responsive on mobile devices
- **Voice Mode**: Limited support due to browser restrictions
- **Recommendation**: Use desktop/laptop for optimal voice experience

## 🔒 Security & Privacy

- **Voice Data**: Processed locally, not stored permanently
- **Conversation History**: Stored in browser session only
- **API Keys**: Secure configuration required
- **Microphone Access**: Requested only when voice mode is activated

## 🧪 Advanced Features

### AI-Enhanced Data Generation
- Intelligent field recommendations based on data type
- Context-aware data modeling
- Realistic sample data with proper relationships

### Conversation Memory
- Full conversation context maintained
- Smart response generation based on chat history
- Conversation clearing for privacy

### Multi-Format Export
- JSON, CSV, XML, SQL formats supported
- One-click downloads with proper file naming
- Preview and validation before download

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Test microphone permissions
3. Verify all dependencies are installed
4. Check browser console for errors

## 🔮 Future Enhancements

- [ ] Real-time voice conversation (interruption support)
- [ ] Multiple language support for voice
- [ ] Voice command shortcuts
- [ ] Audio response customization
- [ ] Conversation export/import
- [ ] Voice analytics and insights
- [ ] Mobile app version
