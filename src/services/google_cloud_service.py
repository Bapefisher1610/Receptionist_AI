import os
import json
import asyncio
from google.cloud import speech
from google.cloud import texttospeech
from google.oauth2 import service_account
import pyaudio
import wave
import threading
import queue
import time

class GoogleCloudService:
    def __init__(self, credentials_path=None):
        """Initialize Google Cloud Speech and TTS clients"""
        self.credentials_path = credentials_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            raise ValueError("Google Cloud credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS environment variable.")
        
        # Initialize clients
        credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
        self.speech_client = speech.SpeechClient(credentials=credentials)
        self.tts_client = texttospeech.TextToSpeechClient(credentials=credentials)
        
        # Audio configuration
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        
        # Audio stream
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
    def start_streaming_recognition(self, callback):
        """Start streaming speech recognition"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.callback = callback
        
        # Start audio stream
        self.stream = self.audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._audio_callback
        )
        
        # Start recognition thread
        self.recognition_thread = threading.Thread(target=self._recognition_loop)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
        
        self.stream.start_stream()
        print("Started Google Cloud streaming recognition")
        
    def stop_streaming_recognition(self):
        """Stop streaming speech recognition"""
        self.is_listening = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
        if hasattr(self, 'recognition_thread'):
            self.recognition_thread.join(timeout=1)
            
        print("Stopped Google Cloud streaming recognition")
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback"""
        if self.is_listening:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
        
    def _recognition_loop(self):
        """Main recognition loop"""
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code="vi-VN",
            enable_automatic_punctuation=True,
            model="latest_long"
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
            single_utterance=False
        )
        
        def request_generator():
            yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)
            
            while self.is_listening:
                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                    yield speech.StreamingRecognizeRequest(audio_content=chunk)
                except queue.Empty:
                    continue
                    
        try:
            requests = request_generator()
            responses = self.speech_client.streaming_recognize(requests)
            
            for response in responses:
                if not self.is_listening:
                    break
                    
                for result in response.results:
                    if result.is_final:
                        transcript = result.alternatives[0].transcript.strip()
                        confidence = result.alternatives[0].confidence
                        
                        if transcript and self.callback:
                            self.callback({
                                'text': transcript,
                                'confidence': confidence,
                                'is_final': True
                            })
                            
        except Exception as e:
            print(f"Recognition error: {e}")
            
    def synthesize_speech(self, text, output_file=None, voice_name="vi-VN-Neural2-A"):
        """Convert text to speech using Google Cloud TTS"""
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code="vi-VN",
                name=voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0
            )
            
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            if output_file:
                with open(output_file, "wb") as out:
                    out.write(response.audio_content)
                print(f"Audio saved to {output_file}")
            
            return response.audio_content
            
        except Exception as e:
            print(f"TTS error: {e}")
            return None
            
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'audio'):
            self.audio.terminate()