import pyttsx3
import threading
import time
import tempfile
import os
import queue
from pathlib import Path
from ...core.config import LANGUAGE, get_greeting

try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import requests
    ONLINE_AVAILABLE = True
except ImportError:
    ONLINE_AVAILABLE = False

class StreamingTTSModule:
    """Enhanced TTS Module for dynamic chatbot-like responses"""
    
    def __init__(self, engine_type="auto", cache_size=50):
        self.engine_type = engine_type
        self.engine = None
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.cache = {}  # Cache for frequently used phrases
        self.cache_size = cache_size
        self.last_greeting_time = {}
        self.greeting_cooldown = 30
        
        # Initialize pygame for audio
        if GTTS_AVAILABLE:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Initialize TTS engine based on type
        self._init_engine()
        
        # Start background worker thread
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()
        
        print(f"Streaming TTS Module ({self.engine_type}) initialized")
    
    def _init_engine(self):
        """Initialize TTS engine based on type"""
        if self.engine_type == "auto":
            self._init_best_available()
        elif self.engine_type == "gtts":
            self._init_gtts()
        elif self.engine_type == "pyttsx3":
            self._init_pyttsx3_vietnamese()
        else:
            self._init_pyttsx3()
    
    def _init_best_available(self):
        """Initialize best available TTS engine"""
        if GTTS_AVAILABLE and ONLINE_AVAILABLE:
            try:
                # Test internet connection
                requests.get('https://www.google.com', timeout=3)
                self.engine_type = "gtts"
                self._init_gtts()
                return
            except:
                pass
        
        # Fallback to pyttsx3
        self.engine_type = "pyttsx3"
        self._init_pyttsx3_vietnamese()
    
    def _init_gtts(self):
        """Initialize Google TTS"""
        if not GTTS_AVAILABLE:
            raise Exception("gTTS not available")
        # No specific initialization needed for gTTS
    
    def _init_pyttsx3_vietnamese(self):
        """Initialize pyttsx3 with Vietnamese optimization"""
        self.engine = pyttsx3.init()
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        
        # Try to find Vietnamese voice or female voice
        vietnamese_voice = None
        female_voice = None
        
        for voice in voices:
            voice_name = voice.name.lower()
            if 'vietnam' in voice_name or 'vi-' in voice.id.lower():
                vietnamese_voice = voice
                break
            elif 'female' in voice_name or 'zira' in voice_name or 'hazel' in voice_name:
                female_voice = voice
        
        # Set voice preference
        if vietnamese_voice:
            self.engine.setProperty('voice', vietnamese_voice.id)
        elif female_voice:
            self.engine.setProperty('voice', female_voice.id)
        
        # Optimize settings for Vietnamese
        self.engine.setProperty('rate', 180)  # Slower for better pronunciation
        self.engine.setProperty('volume', 0.9)
    
    def _init_pyttsx3(self):
        """Initialize standard pyttsx3"""
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('volume', 0.9)
    
    def speak_async(self, text, priority="normal"):
        """Add text to speech queue with priority"""
        if not text.strip():
            return
        
        # Check cache first
        cache_key = f"{self.engine_type}_{text}"
        if cache_key in self.cache:
            # Use cached audio if available
            self.speech_queue.put(("cached", self.cache[cache_key], priority))
        else:
            # Add to queue for processing
            self.speech_queue.put(("text", text, priority))
    
    def speak_immediate(self, text):
        """Speak text immediately, interrupting current speech"""
        self.stop_current_speech()
        self.speak_async(text, priority="high")
    
    def stop_current_speech(self):
        """Stop current speech"""
        if self.engine_type == "gtts":
            pygame.mixer.music.stop()
        elif self.engine and hasattr(self.engine, 'stop'):
            self.engine.stop()
        
        # Clear queue except high priority items
        temp_queue = queue.Queue()
        while not self.speech_queue.empty():
            try:
                item = self.speech_queue.get_nowait()
                if len(item) > 2 and item[2] == "high":
                    temp_queue.put(item)
            except queue.Empty:
                break
        
        self.speech_queue = temp_queue
        self.is_speaking = False
    
    def _speech_worker(self):
        """Background worker to process speech queue"""
        while True:
            try:
                item = self.speech_queue.get(timeout=1)
                
                if item[0] == "cached":
                    self._play_cached_audio(item[1])
                elif item[0] == "text":
                    self._process_and_speak(item[1])
                
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Speech worker error: {e}")
    
    def _process_and_speak(self, text):
        """Process and speak text"""
        self.is_speaking = True
        
        try:
            if self.engine_type == "gtts":
                self._speak_gtts_optimized(text)
            else:
                self._speak_pyttsx3(text)
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            self.is_speaking = False
    
    def _speak_gtts_optimized(self, text):
        """Optimized Google TTS with caching"""
        temp_file = None
        try:
            # Create TTS object
            tts = gTTS(text=text, lang='vi', slow=False)
            
            # Create unique temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                temp_file = tmp.name
            
            # Save and play
            tts.save(temp_file)
            
            # Cache small phrases for reuse
            if len(text) < 100 and len(self.cache) < self.cache_size:
                cache_key = f"{self.engine_type}_{text}"
                self.cache[cache_key] = temp_file
                temp_file = None  # Don't delete cached file
            
            pygame.mixer.music.load(temp_file or self.cache[cache_key])
            pygame.mixer.music.play()
            
            # Wait for completion
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"gTTS Error: {e}")
        finally:
            # Clean up non-cached files
            if temp_file and os.path.exists(temp_file):
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    time.sleep(0.3)
                    os.unlink(temp_file)
                except Exception:
                    threading.Timer(2.0, self._delayed_cleanup, args=[temp_file]).start()
    
    def _speak_pyttsx3(self, text):
        """Speak using pyttsx3"""
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def _play_cached_audio(self, audio_file):
        """Play cached audio file"""
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"Cached audio error: {e}")
    
    def _delayed_cleanup(self, temp_file):
        """Delayed cleanup for temporary files"""
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except Exception:
            pass
    
    def respond_to_query(self, query, context=None):
        """Generate and speak response to user query (chatbot-like)"""
        # This is where you'd integrate with your AI/chatbot logic
        # For now, providing a template
        
        query_lower = query.lower()
        
        # Quick responses for common queries
        if any(word in query_lower for word in ['xin chào', 'hello', 'chào']):
            response = "Xin chào! Tôi có thể giúp gì cho bạn?"
        elif any(word in query_lower for word in ['cảm ơn', 'thank']):
            response = "Không có gì! Tôi luôn sẵn sàng hỗ trợ bạn."
        elif any(word in query_lower for word in ['tạm biệt', 'bye', 'goodbye']):
            response = "Tạm biệt! Hẹn gặp lại bạn!"
        elif any(word in query_lower for word in ['giúp', 'help', 'hỗ trợ']):
            response = "Tôi có thể giúp bạn với nhiều việc. Bạn cần hỗ trợ gì cụ thể?"
        else:
            # Default response - integrate with your AI model here
            response = f"Tôi đã nghe: {query}. Đây là phản hồi tự động từ hệ thống AI."
        
        # Speak the response
        self.speak_async(response, priority="high")
        return response
    
    def clear_cache(self):
        """Clear audio cache"""
        for file_path in self.cache.values():
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass
        self.cache.clear()
    
    def get_queue_size(self):
        """Get current queue size"""
        return self.speech_queue.qsize()
    
    def is_busy(self):
        """Check if TTS is currently busy"""
        return self.is_speaking or not self.speech_queue.empty()
    
    def stop(self):
        """Stop TTS engine and cleanup"""
        self.stop_current_speech()
        self.clear_cache()
        
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass