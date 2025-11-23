import os
import speech_recognition as sr
import numpy as np
import pickle
import time
import threading
import queue
from pathlib import Path

from ...core.config import (
    VOICES_DIR,
    VOICE_CONFIDENCE_THRESHOLD,
    VOICE_ENERGY_THRESHOLD,
    VOICE_PAUSE_THRESHOLD,
    VOICE_PHRASE_TIME_LIMIT,
    VOICE_TIMEOUT,
)
from ...utils.utils import get_timestamp

class VoiceRecognitionModule:
    def __init__(self, logger):
        """Initialize the voice recognition module"""
        self.logger = logger
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.listen_thread = None
        
        # Configure recognizer for better latency & noise handling
        self.recognizer.energy_threshold = VOICE_ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = VOICE_PAUSE_THRESHOLD
        self.recognizer.non_speaking_duration = VOICE_PAUSE_THRESHOLD
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # Voice recognition is not as straightforward as face recognition
        # For simplicity, we'll use speech-to-text and keyword matching
        # In a real system, you'd use a more sophisticated voice recognition system
        self.known_voice_patterns = {}
        self.load_voice_patterns()
    
    def load_voice_patterns(self):
        """Load known voice patterns"""
        patterns_file = VOICES_DIR / 'patterns.pkl'
        
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'rb') as f:
                    self.known_voice_patterns = pickle.load(f)
                print(f"Loaded {len(self.known_voice_patterns)} voice patterns")
            except Exception as e:
                print(f"Error loading voice patterns: {e}")
    
    def save_voice_patterns(self):
        """Save voice patterns to file"""
        patterns_file = VOICES_DIR / 'patterns.pkl'
        os.makedirs(VOICES_DIR, exist_ok=True)
        
        with open(patterns_file, 'wb') as f:
            pickle.dump(self.known_voice_patterns, f)
    
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
        
    def capture_voice_pattern(self, text_input, person_id=None):
        """Capture voice pattern from text input for registration"""
        if not text_input or not text_input.strip():
            return None
            
        # Clean and process the text
        cleaned_text = text_input.strip().lower()
        
        # Extract meaningful keywords from the text
        keywords = self._extract_keywords(cleaned_text)
        
        if not keywords:
            return None
            
        return {
            'text': cleaned_text,
            'keywords': keywords,
            'timestamp': get_timestamp()
        }
        
    def _extract_keywords(self, text):
        """Extract meaningful keywords from text for voice pattern matching"""
        # Remove common stop words in Vietnamese
        stop_words = {
            'tôi', 'là', 'của', 'và', 'có', 'được', 'một', 'này', 'đó', 'với', 
            'để', 'cho', 'từ', 'trong', 'trên', 'dưới', 'về', 'theo', 'như', 
            'khi', 'nếu', 'thì', 'sẽ', 'đã', 'đang', 'rồi', 'chưa', 'không',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        }
        
        # Split text into words and filter
        words = text.split()
        keywords = []
        
        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalnum())
            
            # Keep words that are meaningful
            if (len(clean_word) > 2 and 
                clean_word.lower() not in stop_words and
                clean_word.isalpha()):
                keywords.append(clean_word.lower())
                
        # Also keep the full text as a pattern
        keywords.append(text)
        
        return list(set(keywords))  # Remove duplicates
    
    def start_listening(self):
        """Start listening for voice in a separate thread"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
    
    def stop_listening(self):
        """Stop listening for voice"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
    
    def _listen_loop(self):
        """Background thread for continuous listening"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(
                        source,
                        timeout=VOICE_TIMEOUT,
                        phrase_time_limit=VOICE_PHRASE_TIME_LIMIT,
                    )
                    self.audio_queue.put(audio)
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                continue
            except Exception as e:
                print(f"Error in voice listening: {e}")
                time.sleep(1)  # Prevent tight loop in case of errors
    
    def process_audio(self):
        """Process any audio in the queue and return recognition results"""
        if self.audio_queue.empty():
            return None
        
        try:
            audio = self.audio_queue.get(block=False)
            return self.recognize_speech(audio)
        except queue.Empty:
            return None
        except Exception as e:
            print(f"Error processing audio: {e}")
            return None
    
    def recognize_speech(self, audio):
        """Recognize speech in audio and match against known patterns"""
        try:
            # Convert speech to text
            text = self.recognizer.recognize_google(audio, language="vi-VN")
            print(f"Recognized speech: {text}")
            
            # Match against known patterns
            best_match = None
            best_confidence = 0
            
            for person_id, pattern in self.known_voice_patterns.items():
                confidence = self._calculate_match_confidence(text, pattern['keywords'])
                
                if confidence > best_confidence and confidence >= VOICE_CONFIDENCE_THRESHOLD:
                    best_confidence = confidence
                    best_match = {
                        'person_id': person_id,
                        'name': pattern['name'],
                        'confidence': confidence,
                        'text': text
                    }
            
            # If we found a match, log it
            if best_match:
                self.logger.log_recognition(
                    best_match['person_id'],
                    best_match['name'],
                    "voice",
                    best_match['confidence']
                )
                
                return best_match
            
            # Return the recognized text even if no match
            return {
                'person_id': 'unknown',
                'name': 'Unknown',
                'confidence': 0,
                'text': text
            }
            
        except sr.UnknownValueError:
            # Speech was unintelligible
            return None
        except sr.RequestError as e:
            # Could not request results from service
            print(f"Could not request results from speech recognition service: {e}")
            return None
    
    def _calculate_match_confidence(self, text, keywords):
        """Calculate confidence score for matching text against keywords"""
        if not text or not keywords:
            return 0
        t = text.lower()
        matches = sum(1 for k in keywords if k and k.lower() in t)
        if matches > 0:
            return min(1.0, matches / max(1, len([k for k in keywords if k])))
        return 0

    def listen_for_command(self, timeout=None, phrase_time_limit=None, calibrate_duration=0.3):
        """Listen for voice command and return recognized text"""
        try:
            to = VOICE_TIMEOUT if timeout is None else timeout
            ptl = VOICE_PHRASE_TIME_LIMIT if phrase_time_limit is None else phrase_time_limit
            print(f"[VOICE] Listening for command (timeout: {to}s, limit: {ptl}s)...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=calibrate_duration)
                audio = self.recognizer.listen(
                    source,
                    timeout=to,
                    phrase_time_limit=ptl,
                )

            print("[VOICE] Audio captured, recognizing...")
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio, language='vi-VN')
                print(f"[VOICE] Recognized: '{text}'")
                return text.lower()
            except sr.UnknownValueError:
                print("[VOICE] Speech was unintelligible")
                return None
            except sr.RequestError as e:
                print(f"[VOICE] Recognition service error: {e}")
                self.logger.error(f"Voice recognition service error: {e}")
                return None

        except sr.WaitTimeoutError:
            print("[VOICE] No speech detected within timeout")
            return None
        except Exception as e:
            print(f"[VOICE] Voice command error: {e}")
            self.logger.error(f"Voice command error: {e}")
            return None