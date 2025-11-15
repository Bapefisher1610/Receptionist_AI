import os
import time
import threading
import queue
import pickle
from pathlib import Path

from .google_cloud_service import GoogleCloudService
from ..core.config import VOICES_DIR, VOICE_CONFIDENCE_THRESHOLD
from ..utils.utils import get_timestamp

class GoogleVoiceRecognitionModule:
    def __init__(self, logger, credentials_path=None):
        """Initialize Google Cloud voice recognition module"""
        self.logger = logger
        self.known_voice_patterns = {}
        self.patterns_file = VOICES_DIR / 'patterns.pkl'
        
        # Initialize Google Cloud service
        try:
            self.google_service = GoogleCloudService(credentials_path)
            print("Google Cloud Speech service initialized")
        except Exception as e:
            print(f"Failed to initialize Google Cloud service: {e}")
            self.google_service = None
            
        # Load existing voice patterns
        self.load_voice_patterns()
        
        # Recognition state
        self.is_listening = False
        self.last_recognition_time = 0
        self.recognition_cooldown = 1.0  # 1 second cooldown between recognitions
        
    def load_voice_patterns(self):
        """Load known voice patterns from file"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'rb') as f:
                    self.known_voice_patterns = pickle.load(f)
                print(f"Loaded {len(self.known_voice_patterns)} voice patterns")
            except Exception as e:
                print(f"Error loading voice patterns: {e}")
                self.known_voice_patterns = {}
        else:
            self.known_voice_patterns = {}
            
    def save_voice_patterns(self):
        """Save voice patterns to file"""
        try:
            with open(self.patterns_file, 'wb') as f:
                pickle.dump(self.known_voice_patterns, f)
        except Exception as e:
            print(f"Error saving voice patterns: {e}")
            
    def add_voice_pattern(self, person_id, person_name, keywords):
        """Add a new voice pattern or update existing one"""
        if not keywords:
            return False
            
        # If person already exists, merge keywords
        if person_id in self.known_voice_patterns:
            existing_keywords = self.known_voice_patterns[person_id]['keywords']
            # Add new keywords that don't already exist
            for keyword in keywords:
                if keyword not in existing_keywords:
                    existing_keywords.append(keyword)
            self.known_voice_patterns[person_id]['keywords'] = existing_keywords
        else:
            # Store new keywords for this person
            self.known_voice_patterns[person_id] = {
                'name': person_name,
                'keywords': keywords
            }
            
        # Save updated patterns
        self.save_voice_patterns()
        print(f"📝 Updated voice patterns for {person_name}: {self.known_voice_patterns[person_id]['keywords']}")
        
        return True
        
    def start_listening(self):
        """Start listening for voice using Google Cloud"""
        if not self.google_service:
            print("Google Cloud service not available")
            return False
            
        if self.is_listening:
            return True
            
        try:
            self.is_listening = True
            self.google_service.start_streaming_recognition(self._on_speech_recognized)
            return True
        except Exception as e:
            print(f"Error starting Google Cloud recognition: {e}")
            self.is_listening = False
            return False
            
    def stop_listening(self):
        """Stop listening for voice"""
        if self.google_service and self.is_listening:
            self.google_service.stop_streaming_recognition()
        self.is_listening = False
        
    def _on_speech_recognized(self, result):
        """Callback when speech is recognized"""
        if not result or not result.get('is_final'):
            return
            
        current_time = time.time()
        if current_time - self.last_recognition_time < self.recognition_cooldown:
            return
            
        text = result.get('text', '').strip()
        confidence = result.get('confidence', 0)
        
        if text:
            print(f"Recognized speech: {text}")
            self.last_recognition_time = current_time
            
            # Try to match with known patterns
            matched_result = self._match_voice_pattern(text, confidence)
            if matched_result:
                self.logger.log_recognition(
                    matched_result['person_id'],
                    matched_result['name'],
                    "voice",
                    matched_result['confidence']
                )
                
    def _match_voice_pattern(self, text, base_confidence):
        """Match recognized text against known voice patterns"""
        if not text or not self.known_voice_patterns:
            return {
                'person_id': 'unknown',
                'name': 'Unknown',
                'confidence': base_confidence,
                'text': text
            }
            
        best_match = None
        best_confidence = 0
        
        # Check each known pattern
        for person_id, pattern in self.known_voice_patterns.items():
            keywords = pattern.get('keywords', [])
            match_confidence = self._calculate_match_confidence(text, keywords)
            
            # Combine with base confidence from Google Cloud
            combined_confidence = (match_confidence + base_confidence) / 2
            
            if combined_confidence > best_confidence and combined_confidence >= VOICE_CONFIDENCE_THRESHOLD:
                best_confidence = combined_confidence
                best_match = {
                    'person_id': person_id,
                    'name': pattern['name'],
                    'confidence': combined_confidence,
                    'text': text
                }
                
        if best_match:
            return best_match
            
        # Return unknown result
        return {
            'person_id': 'unknown',
            'name': 'Unknown',
            'confidence': base_confidence,
            'text': text
        }
        
    def _calculate_match_confidence(self, text, keywords):
        """Calculate confidence score for matching text against keywords"""
        if not text or not keywords:
            return 0
            
        # Convert to lowercase for case-insensitive matching
        text = text.lower()
        
        # Count how many keywords are in the text
        matches = sum(1 for keyword in keywords if keyword.lower() in text)
        
        # Calculate confidence based on percentage of matched keywords
        if matches > 0:
            return min(1.0, matches / len(keywords))
            
        return 0
        
    def process_audio(self):
        """Process audio (compatibility method for existing code)"""
        # This method is kept for compatibility with existing main.py
        # The actual processing is done in the callback
        return None
        
    def listen_for_command(self, timeout=3):
        """Listen for voice command using Google recognition (Cloud preferred, Basic fallback)"""
        try:
            # Use speech recognition library
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            microphone = sr.Microphone()

            with microphone as source:
                print("[VOICE] Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print(f"[VOICE] Listening for command (timeout: {timeout}s)...")
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

            print("[VOICE] Processing audio...")
            # Debug: Check audio data
            if hasattr(audio, 'frame_data') and audio.frame_data:
                print(f"[VOICE] Audio data length: {len(audio.frame_data)} bytes")
            else:
                print("[VOICE] Warning: No audio frame data detected")

            # Try Google Cloud first if available, otherwise use basic Google recognition
            if self.google_service:
                try:
                    # Try Google Cloud first for better accuracy
                    text = recognizer.recognize_google_cloud(audio, language="vi-VN")
                    print(f"[VOICE] Google Cloud recognized: '{text}'")
                    return text.lower()
                except Exception as e:
                    print(f"[VOICE] Google Cloud failed: {e}, trying basic recognition...")
                    # Fall through to basic recognition

            # Basic Google recognition (always available)
            try:
                text = recognizer.recognize_google(audio, language="vi-VN")
                print(f"[VOICE] Basic Google recognized: '{text}'")
                return text.lower()
            except Exception as e2:
                print(f"[VOICE] Basic Google recognition failed: {type(e2).__name__}: {e2}")
                # Try with English as fallback
                try:
                    print("[VOICE] Trying English recognition as fallback...")
                    text = recognizer.recognize_google(audio, language="en-US")
                    print(f"[VOICE] English fallback recognized: '{text}'")
                    return text.lower()
                except Exception as e3:
                    print(f"[VOICE] English fallback also failed: {type(e3).__name__}: {e3}")
                    return None

        except sr.WaitTimeoutError:
            print("[VOICE] No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            print("[VOICE] Speech was unintelligible")
            return None
        except sr.RequestError as e:
            print(f"[VOICE] Recognition service error: {e}")
            return None
        except Exception as e:
            print(f"[VOICE] Voice command error: {e}")
            return None

    def synthesize_speech(self, text, output_file=None):
        """Synthesize speech using Google Cloud TTS"""
        if not self.google_service:
            print("Google Cloud service not available for TTS")
            return None

        return self.google_service.synthesize_speech(text, output_file)