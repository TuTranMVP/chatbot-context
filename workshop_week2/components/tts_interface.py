"""
Text-to-Speech Interface Component for Maya Chatbot
Handles speech synthesis for bot responses
"""

import streamlit as st
import pyttsx3
import threading
import tempfile
import os
from typing import Optional
import base64

class TTSInterface:
    """Handles text-to-speech conversion"""
    
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        
    def initialize_tts(self) -> bool:
        """Initialize TTS engine"""
        try:
            self.engine = pyttsx3.init()
            # Configure voice settings
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 0.8)  # Volume (0.0 to 1.0)
            return True
        except Exception as e:
            st.error(f"Failed to initialize text-to-speech: {e}")
            return False
    
    def speak_text(self, text: str) -> bool:
        """Speak the given text"""
        if self.engine is None:
            if not self.initialize_tts():
                return False
        
        try:
            # Run TTS in a separate thread to avoid blocking UI
            def speak():
                self.is_speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
            
            speech_thread = threading.Thread(target=speak)
            speech_thread.daemon = True
            speech_thread.start()
            return True
            
        except Exception as e:
            st.error(f"Text-to-speech error: {e}")
            return False
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
                self.is_speaking = False
            except Exception as e:
                st.error(f"Error stopping speech: {e}")
    
    def generate_audio_file(self, text: str) -> Optional[str]:
        """Generate audio file from text and return file path"""
        if self.engine is None:
            if not self.initialize_tts():
                return None
        
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.close()
            
            # Save speech to file
            self.engine.save_to_file(text, temp_file.name)
            self.engine.runAndWait()
            
            return temp_file.name
            
        except Exception as e:
            st.error(f"Error generating audio file: {e}")
            return None
    
    def create_audio_player(self, text: str) -> Optional[str]:
        """Create HTML audio player for the text"""
        audio_file = self.generate_audio_file(text)
        if audio_file and os.path.exists(audio_file):
            try:
                with open(audio_file, 'rb') as f:
                    audio_bytes = f.read()
                
                # Clean up temp file
                os.unlink(audio_file)
                
                # Create base64 encoded audio
                audio_b64 = base64.b64encode(audio_bytes).decode()
                audio_html = f"""
                <audio controls autoplay>
                    <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                """
                return audio_html
            except Exception as e:
                st.error(f"Error creating audio player: {e}")
                return None
        return None
