"""
Voice Interface Component for Maya Chatbot
Handles speech-to-text and microphone functionality with TTS response
"""

import threading
import time

import soundfile as sf
import speech_recognition as sr
import streamlit as st
import torch
from transformers import AutoTokenizer, VitsModel


class VoiceInterface:
    """Handles voice recording and speech-to-text conversion"""

    def __init__(self, chatbot=None):
        self.recognizer = sr.Recognizer()
        # Set pause threshold to 2 seconds
        self.recognizer.pause_threshold = 2.0
        self.microphone = None
        self.is_recording = False
        self.recording_thread = None
        self.processing = False  # Flag to prevent duplicate processing
        self.chatbot = chatbot  # Reference to the chatbot instance

        # Initialize TTS model and tokenizer
        self.tts_model = None
        self.tts_tokenizer = None
        self._initialize_tts()

    def _initialize_tts(self):
        """Initialize the Hugging Face TTS model and tokenizer"""
        try:
            print('Loading TTS model...')
            self.tts_model = VitsModel.from_pretrained('./mms-tts-eng-local')
            self.tts_tokenizer = AutoTokenizer.from_pretrained(
                './mms-tts-eng-local'
            )
            print('TTS model loaded successfully!')
        except Exception as e:
            print(f'Failed to load TTS model: {e}')
            self.tts_model = None
            self.tts_tokenizer = None

    def initialize_microphone(self) -> bool:
        """Initialize microphone and return success status"""
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            return True
        except Exception as e:
            st.error(f'Failed to initialize microphone: {e}')
            return False

    def start_continuous_recording(self):
        """Start continuous voice activity detection and recording"""
        if self.microphone is None:
            if not self.initialize_microphone():
                return False

        self.is_recording = True
        self.recording_thread = threading.Thread(
            target=self._continuous_voice_detection
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()
        return True

    def _continuous_voice_detection(self):
        """Continuous voice activity detection with automatic transcription"""
        try:
            if self.microphone is None:
                print("Microphone not initialized")
                return

            with self.microphone as source:
                # Adjust for ambient noise once
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

                while self.is_recording:
                    try:
                        # Skip if already processing audio
                        if self.processing:
                            time.sleep(0.1)  # Wait before checking again
                            continue

                        # Listen for speech with 2 second pause detection
                        self.recognizer.energy_threshold = 300
                        self.recognizer.dynamic_energy_threshold = True

                        # Listen for audio with 2 second pause for end detection
                        audio = self.recognizer.listen(
                            source, timeout=None, phrase_time_limit=None
                        )

                        # Process audio directly without threading to avoid duplicates
                        self._process_audio_sync(audio)

                    except Exception as e:
                        print(f'Voice detection error: {e}')
                        time.sleep(0.1)

        except Exception as e:
            print(f'Continuous recording error: {e}')

    def _process_audio_sync(self, audio):
        """Process audio synchronously and call chatbot with user voice input"""
        if self.processing:
            return

        self.processing = True
        try:
            # Transcribe the audio
            text = self.recognizer.recognize_google(audio) # type: ignore
            if text and len(text.strip()) > 0:
                user_question = text.strip()
                # Log what user said
                print(f'User said: {user_question}')

                # Process the voice input through the chatbot if available
                if self.chatbot:
                    try:
                        response, structured_data = (
                            self.chatbot.voice_process_message(user_question)
                        )
                        print(f'Chatbot response: {response}')

                        # Convert response to speech using TTS
                        self._speak_response(response)

                    except Exception as e:
                        print(f'Error processing message through chatbot: {e}')

        except sr.UnknownValueError:
            # Speech was unintelligible, ignore
            pass
        except sr.RequestError as e:
            print(f'Speech recognition error: {e}')
        except Exception as e:
            print(f'Audio processing error: {e}')
        finally:
            self.processing = False
            # Add small delay to prevent immediate re-listening
            time.sleep(0.2)

    def _speak_response(self, text):
        """Convert text response to speech using Hugging Face TTS model"""
        if not self.tts_model or not self.tts_tokenizer:
            print('TTS model not available, skipping speech synthesis')
            return

        try:
            # Clean the text for TTS (remove markdown formatting)
            clean_text = self._clean_text_for_tts(text)
            print(f'Converting to speech: {clean_text[:100]}...')

            # Tokenize the input text
            inputs = self.tts_tokenizer(clean_text, return_tensors='pt')

            # Generate waveform using the model
            with torch.no_grad():
                output = self.tts_model(**inputs).waveform

            # Save the audio to a file
            output_audio = output.squeeze().numpy()
            sampling_rate = self.tts_model.config.sampling_rate

            # Save to temporary file and play
            temp_file = 'temp_response.wav'
            sf.write(temp_file, output_audio, sampling_rate)
            print(f'Audio saved to {temp_file}')

            # Play the audio (you might need to add audio playback functionality)
            self._play_audio(temp_file)

        except Exception as e:
            print(f'Error in TTS conversion: {e}')

    def _clean_text_for_tts(self, text):
        """Clean text for TTS by removing markdown and special characters"""
        # Remove markdown formatting
        import re

        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove markdown bold/italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        # Remove markdown links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove bullet points
        text = re.sub(r'^[•\-\*]\s+', '', text, flags=re.MULTILINE)
        # Remove emojis and special characters
        text = re.sub(r'[📚🎯📊⏱️⚠️🛠️📋💡📂🔗🤖✨🔢🏗️]', '', text)
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Limit length for TTS (most TTS models have character limits)
        if len(text) > 500:
            text = text[:500] + '...'

        return text

    def _play_audio(self, audio_file):
        """Play audio file (placeholder - implement based on your needs)"""
        try:
            # For Windows, you can use winsound
            import winsound

            winsound.PlaySound(audio_file, winsound.SND_FILENAME)  # type: ignore
        except ImportError:
            # For cross-platform, you could use pygame or other libraries
            print(f'Audio file ready: {audio_file}')
            print('Note: Audio playback requires additional setup')

    def set_chatbot(self, chatbot):
        """Set the chatbot instance for processing voice input"""
        self.chatbot = chatbot

    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=2)


def check_microphone_permission() -> bool:
    """Check if microphone access is available"""
    try:
        # Try to create a microphone instance
        mic = sr.Microphone()
        with mic:
            pass
        return True
    except Exception:
        return False
