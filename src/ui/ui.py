import cv2
import numpy as np
import time
from datetime import datetime
from collections import deque

from ..core.config import UI_WINDOW_NAME, UI_WINDOW_WIDTH, UI_WINDOW_HEIGHT, get_greeting
from ..utils.utils import draw_text_with_background, resize_image

class UI:
    def __init__(self):
        """Initialize the UI"""
        self.window_name = UI_WINDOW_NAME
        self.width = UI_WINDOW_WIDTH
        self.height = UI_WINDOW_HEIGHT
        self.frame = None
        self.recognition_results = []
        self.messages = []
        self.max_messages = 5  # Maximum number of messages to display
        self.greeted_people = set()  # Track people who have been greeted
        
        # Registration UI state
        self.show_registration_dialog = False
        self.registration_status = ""
        self.registration_name = ""
        self.registration_info = ""
        
        # Log display
        self.log_messages = deque(maxlen=10)  # Chỉ giữ 10 dòng log gần nhất
        self.log_area_height = 200  # Chiều cao vùng log
        
    
    def update_frame(self, frame):
        """Update the current frame"""
        if frame is not None:
            # Resize frame to fit window
            self.frame = resize_image(frame.copy(), width=self.width)
    
    def update_recognition_results(self, face_results, voice_result=None):
        """Update recognition results"""
        self.recognition_results = face_results
        
        # Add voice recognition result if available
        if voice_result:
            # Add a message for voice recognition
            self.add_message(f"{voice_result['name']} said: {voice_result['text']}")
    
    def add_message(self, message):
        """Add a message to the UI"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append({
            'text': message,
            'timestamp': timestamp,
            'time': time.time()
        })
        
        # Keep only the most recent messages
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def render(self):
        """Render the UI"""
        if self.frame is None:
            # Create a blank frame if no camera frame is available
            self.frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Create a copy of the frame to draw on
        display_frame = self.frame.copy()
        
        # Draw face recognition results
        for result in self.recognition_results:
            name = result['name']
            confidence = result['confidence']
            top, right, bottom, left = result['location']

            # Draw a box around the face
            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Draw name label above the bounding box (clear, non-occluded)
            label_text = f"{name}"
            approx_text_h = int(0.7 * 30)
            label_y = top - (approx_text_h + 8)
            if label_y <= 0:
                label_y = bottom + 8
            label_x = left
            draw_text_with_background(display_frame, label_text, (label_x, label_y))

            # Greeting is now handled in main logic to ensure consistency
            # UI only displays recognition results without duplicate greetings
        
        # Draw messages
        self._draw_messages(display_frame)
        
        # Draw registration dialog if active
        if self.show_registration_dialog:
            self._draw_registration_dialog(display_frame)
        
        # Draw log area
        self._draw_log_area(display_frame)
        
        # Draw current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw_text_with_background(display_frame, current_time, (10, 30), 
                                bg_color=(50, 50, 50))
        
        # Show the frame
        cv2.imshow(self.window_name, display_frame)
    
    def _draw_messages(self, frame):
        """Draw messages on the frame"""
        # Calculate message area
        msg_area_height = 150
        msg_area_y = self.height - msg_area_height
        
        # Draw semi-transparent background for message area
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, msg_area_y), (self.width, self.height), 
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw messages
        y_pos = msg_area_y + 30
        for msg in reversed(self.messages):
            text = f"[{msg['timestamp']}] {msg['text']}"
            draw_text_with_background(frame, text, (10, y_pos), 
                                    bg_color=(50, 50, 50))
            y_pos += 30
    
    def reset_greeted_people(self):
        """Reset the list of greeted people"""
        self.greeted_people.clear()
    
    def get_text_input(self, prompt="Enter text: "):
        """Get text input from user (simplified version)"""
        # For now, return None as this would require a more complex UI
        # In a real implementation, you'd create an input dialog
        return None
    
    def show_registration_ui(self, status="Đang đăng ký người dùng mới...", name="", info=""):
        """Show registration dialog"""
        self.show_registration_dialog = True
        self.registration_status = status
        self.registration_name = name
        self.registration_info = info
        
    def hide_registration_ui(self):
        """Hide registration dialog"""
        self.show_registration_dialog = False
        self.registration_status = ""
        self.registration_name = ""
        self.registration_info = ""
        
    def update_registration_status(self, status, name="", info=""):
        """Update registration dialog content"""
        self.registration_status = status
        if name:
            self.registration_name = name
        if info:
            self.registration_info = info
            
    def _draw_registration_dialog(self, frame):
        """Draw registration dialog overlay"""
        # Dialog dimensions
        dialog_width = 400
        dialog_height = 200
        dialog_x = (self.width - dialog_width) // 2
        dialog_y = (self.height - dialog_height) // 2
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Draw dialog box
        cv2.rectangle(frame, (dialog_x, dialog_y), 
                     (dialog_x + dialog_width, dialog_y + dialog_height), 
                     (255, 255, 255), -1)
        cv2.rectangle(frame, (dialog_x, dialog_y), 
                     (dialog_x + dialog_width, dialog_y + dialog_height), 
                     (0, 0, 0), 2)
        
        # Draw title
        title = "ĐĂNG KÝ NGƯỜI DÙNG MỚI"
        draw_text_with_background(frame, title, (dialog_x + 20, dialog_y + 30), 
                                bg_color=(255, 255, 255), text_color=(0, 0, 0))
        
        # Draw status
        if self.registration_status:
            draw_text_with_background(frame, self.registration_status, 
                                    (dialog_x + 20, dialog_y + 70), 
                                    bg_color=(255, 255, 255), text_color=(0, 100, 0))
        
        # Draw name if available
        if self.registration_name:
            name_text = f"Tên: {self.registration_name}"
            draw_text_with_background(frame, name_text, 
                                    (dialog_x + 20, dialog_y + 100), 
                                    bg_color=(255, 255, 255), text_color=(0, 0, 0))
        
        # Draw additional info if available
        if self.registration_info:
            draw_text_with_background(frame, self.registration_info, 
                                    (dialog_x + 20, dialog_y + 130), 
                                    bg_color=(255, 255, 255), text_color=(0, 0, 100))
        
        # Draw instruction
        instruction = "Vui lòng nói tên và mục đích của bạn"
        draw_text_with_background(frame, instruction, 
                                (dialog_x + 20, dialog_y + 160), 
                                bg_color=(255, 255, 255), text_color=(100, 100, 100))
    
    def add_log_message(self, message):
        """Add a log message to display"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        self.log_messages.append(formatted_msg)
    
    def _draw_log_area(self, frame):
        """Draw log area at bottom of frame"""
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        height, width = frame.shape[:2]
        
        # Draw semi-transparent black background for log area
        log_y_start = height - self.log_area_height
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, log_y_start), (width, height), (0, 0, 0), -1)
        # Alpha blend: 0.7 = 70% transparent
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw border
        cv2.rectangle(frame, (0, log_y_start), (width, height), (100, 100, 100), 2)
        
        # Draw title using cv2 (English only)
        cv2.putText(frame, "SYSTEM LOG", (10, log_y_start + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Convert to PIL Image for Vietnamese text
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(frame_pil)
        
        # Try to load a font that supports Vietnamese
        try:
            # Windows fonts
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            try:
                # Linux fonts
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                # Fallback to default
                font = ImageFont.load_default()
        
        # Draw log messages
        y_offset = log_y_start + 50
        line_height = 20
        
        for i, log_msg in enumerate(self.log_messages):
            if y_offset + line_height > height - 10:
                break
            
            # Color based on log level (RGB for PIL)
            color = (255, 255, 255)  # White default
            if "ERROR" in log_msg or "❌" in log_msg:
                color = (255, 0, 0)  # Red
            elif "WARNING" in log_msg or "⚠️" in log_msg:
                color = (255, 255, 0)  # Yellow
            elif "INFO" in log_msg or "✅" in log_msg or "📝" in log_msg or "🎤" in log_msg or "🤖" in log_msg:
                color = (0, 255, 0)  # Green
            elif "DEBUG" in log_msg:
                color = (255, 0, 255)  # Magenta
            elif "🚀" in log_msg or "🔄" in log_msg:
                color = (255, 165, 0)  # Orange
            
            # Truncate long messages
            if len(log_msg) > 100:
                log_msg = log_msg[:97] + "..."
            
            # Draw text with PIL (supports Vietnamese)
            draw.text((10, y_offset), log_msg, font=font, fill=color)
            y_offset += line_height
        
        # Convert back to OpenCV format
        frame_cv = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
        frame[:] = frame_cv
    
    def close(self):
        """Close the UI window"""
        cv2.destroyWindow(self.window_name)