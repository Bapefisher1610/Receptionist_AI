import os
import cv2
import datetime
import numpy as np
import pickle
from pathlib import Path
from ..core.config import LOGS_DIR, FACES_DIR, VOICES_DIR

def get_timestamp():
    """Return current timestamp in a formatted string"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_date_for_filename():
    """Return current date in a format suitable for filenames"""
    return datetime.datetime.now().strftime("%Y%m%d")

def time_difference_in_seconds(time1, time2):
    """Calculate time difference in seconds between two datetime objects"""
    if not time1 or not time2:
        return float('inf')  # Return infinity if either time is None
    
    if isinstance(time1, str):
        time1 = datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
    
    if isinstance(time2, str):
        time2 = datetime.datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
        
    return abs((time2 - time1).total_seconds())

def resize_image(image, width=None, height=None):
    """Resize image while maintaining aspect ratio"""
    if image is None:
        return None
    h, w = image.shape[:2]
    if width is None and height is None:
        return image.copy()
    if width is None:
        aspect_ratio = height / float(h)
        dim = (int(w * aspect_ratio), height)
    elif height is None:
        aspect_ratio = width / float(w)
        dim = (width, int(h * aspect_ratio))
    else:
        dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    

def create_log_file_path(log_type):
    """Create a log file path based on the current date and log type"""
    date_str = get_date_for_filename()
    log_file = LOGS_DIR / f"{log_type}_{date_str}.log"
    
    # Ensure the logs directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    return log_file

def load_image_from_path(image_path):
    """Load an image from a file path"""
    if not os.path.exists(image_path):
        return None
    
    image = cv2.imread(str(image_path))
    if image is None:
        return None
    
    # Convert from BGR to RGB (face_recognition uses RGB)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def draw_text_with_background(image, text, position, font_scale=0.7, thickness=1, 
                             font=cv2.FONT_HERSHEY_SIMPLEX, text_color=(255, 255, 255),
                             bg_color=(0, 0, 0), padding=5):
    """Draw text with a background on an image using Pillow for Unicode support"""
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    
    # Convert OpenCV image to PIL image
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # Try to load a TrueType font that supports Vietnamese
    try:
        # Try to use a system font that supports Vietnamese
        font_size = int(font_scale * 30)  # Convert scale to approximate font size
        try:
            # Try Arial first (common font with good Unicode support)
            pil_font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Try Times New Roman as fallback
                pil_font = ImageFont.truetype("times.ttf", font_size)
            except:
                # Use default font as last resort
                pil_font = ImageFont.load_default()
    except Exception as e:
        print(f"Font loading error: {e}")
        pil_font = ImageFont.load_default()
    
    # Get text size with the selected font
    text_bbox = draw.textbbox((0, 0), text, font=pil_font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    # Calculate background rectangle coordinates
    x, y = position
    
    # Draw background rectangle
    draw.rectangle([x - padding, y - padding, x + text_w + padding, y + text_h + padding], 
                  fill=bg_color)
    
    # Draw text
    draw.text((x, y), text, font=pil_font, fill=text_color)
    
    # Convert back to OpenCV image
    result_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Copy the result back to the original image
    image[:] = result_img
    
    return image

def load_face_encodings():
    """Load face encodings from pickle file"""
    encodings_file = FACES_DIR / 'encodings.pkl'
    
    if encodings_file.exists():
        try:
            with open(encodings_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading face encodings: {e}")
            return {}
    else:
        print(f"Face encodings file not found: {encodings_file}")
        return {}

def load_voice_patterns():
    """Load voice patterns from pickle file"""
    patterns_file = VOICES_DIR / 'patterns.pkl'
    
    if patterns_file.exists():
        try:
            with open(patterns_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading voice patterns: {e}")
            return {}
    else:
        print(f"Voice patterns file not found: {patterns_file}")
        return {}