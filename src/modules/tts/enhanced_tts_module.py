import pyttsx3
import threading
import time
import tempfile
import os
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

class EnhancedTTSModule:
    def __init__(self, engine_type="auto"):
        self.engine_type = engine_type
        self.is_speaking = False
        self.last_greeting_time = {}
        self.greeting_cooldown = 10  # seconds
        
        # Initialize based on engine type
        if engine_type == "auto":
            self._init_best_available()
        elif engine_type == "pyttsx3":
            self._init_pyttsx3()
        elif engine_type == "gtts":
            self._init_gtts()
        
    def _init_best_available(self):
        """Initialize the best available TTS engine"""
        # Try Vietnamese voices first
        if self._init_pyttsx3_vietnamese():
            self.engine_type = "pyttsx3_vietnamese"
        elif GTTS_AVAILABLE and ONLINE_AVAILABLE:
            self._init_gtts()
            self.engine_type = "gtts"
        else:
            self._init_pyttsx3()
            self.engine_type = "pyttsx3"
    
    def _init_pyttsx3_vietnamese(self):
        """Try to initialize pyttsx3 with Vietnamese voice"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            
            # Look for Vietnamese voices
            vietnamese_voices = []
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower()
                
                if any(keyword in voice_name for keyword in ['vietnamese', 'vietnam', 'vi-vn', 'an']):
                    vietnamese_voices.append(voice)
            
            if vietnamese_voices:
                # Use the first Vietnamese voice found
                self.engine.setProperty('voice', vietnamese_voices[0].id)
                self.engine.setProperty('rate', 130)  # Slower for Vietnamese
                self.engine.setProperty('volume', 0.95)
                print(f"🎤 Using Vietnamese voice: {vietnamese_voices[0].name}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to initialize Vietnamese pyttsx3: {e}")
            return False
    
    def _init_pyttsx3(self):
        """Initialize standard pyttsx3"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            
            # Find best female voice for Vietnamese
            female_voice = None
            for voice in voices:
                voice_name = voice.name.lower()
                if any(keyword in voice_name for keyword in ['female', 'woman', 'zira', 'hazel']):
                    female_voice = voice.id
                    break
            
            if female_voice:
                self.engine.setProperty('voice', female_voice)
                print(f"🎤 Using female voice for Vietnamese")
            
            # Optimize for Vietnamese
            self.engine.setProperty('rate', 120)  # Very slow for clarity
            self.engine.setProperty('volume', 1.0)  # Max volume
            
            print("Enhanced TTS Module (pyttsx3) initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize pyttsx3: {e}")
            self.engine = None
    
    def _init_gtts(self):
        """Initialize Google TTS"""
        if GTTS_AVAILABLE:
            try:
                pygame.mixer.init()
                print("Enhanced TTS Module (gTTS) initialized")
            except Exception as e:
                print(f"❌ Failed to initialize gTTS: {e}")
        else:
            print("❌ gTTS not available")
    
    def speak_async(self, text):
        """Speak text using the best available method"""
        if self.is_speaking:
            return
        
        def speak_thread():
            try:
                self.is_speaking = True
                print(f"Speaking ({self.engine_type}): {text}")
                
                if self.engine_type.startswith("pyttsx3"):
                    self._speak_pyttsx3(text)
                elif self.engine_type == "gtts":
                    self._speak_gtts(text)
                    
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                self.is_speaking = False
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
    
    def _speak_pyttsx3(self, text):
        """Speak using pyttsx3"""
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def _speak_gtts(self, text):
        """Speak using Google TTS"""
        temp_file = None
        try:
            # Create TTS object with Vietnamese
            tts = gTTS(text=text, lang='vi', slow=False)
            
            # Create unique temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                temp_file = tmp.name
            
            # Save to temporary file
            tts.save(temp_file)
            
            # Play the file
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
        except Exception as e:
            print(f"gTTS Error: {e}")
        finally:
            # Clean up temporary file with better handling
            if temp_file and os.path.exists(temp_file):
                try:
                    # Stop music and unload to release file handle completely
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    time.sleep(0.5)  # Longer delay to ensure file is fully released
                    os.unlink(temp_file)
                except Exception:
                    # If immediate deletion fails, schedule for later cleanup
                    # This is common on Windows due to file locking
                    threading.Timer(2.0, self._delayed_cleanup, args=[temp_file]).start()
    
    def greet_person(self, person_id, person_name, recognition_type="face"):
        """Greet a person with cooldown"""
        current_time = time.time()
        
        if person_id in self.last_greeting_time:
            if current_time - self.last_greeting_time[person_id] < self.greeting_cooldown:
                return
        
        self.last_greeting_time[person_id] = current_time
        
        if person_name and person_name != "Unknown":
            greeting = get_greeting('welcome', person_name)
        else:
            greeting = get_greeting('welcome_unknown')
        
        if recognition_type == "voice":
            greeting = f"Tôi đã nhận ra giọng nói của bạn. {greeting}"
        elif recognition_type == "face":
            greeting = f"Tôi đã nhận ra khuôn mặt của bạn. {greeting}"
        
        self.speak_async(greeting)
    
    def speak_help(self):
        """Speak help message"""
        help_message = get_greeting('help')
        self.speak_async(help_message)
    
    def speak_goodbye(self, person_name=None):
        """Speak goodbye message"""
        if person_name and person_name != "Unknown":
            goodbye = get_greeting('goodbye', person_name)
        else:
            goodbye = "Tạm biệt! Hẹn gặp lại."
        
        self.speak_async(goodbye)
    
    def _delayed_cleanup(self, temp_file):
        """Delayed cleanup for temporary files"""
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except Exception:
            # If still can't delete, try one more time after longer delay
            try:
                threading.Timer(5.0, lambda: os.path.exists(temp_file) and os.unlink(temp_file)).start()
            except:
                pass  # Give up silently
    
    def stop(self):
        """Stop TTS engine"""
        try:
            if hasattr(self, 'engine') and self.engine:
                self.engine.stop()
            if GTTS_AVAILABLE:
                pygame.mixer.quit()
        except:
            pass