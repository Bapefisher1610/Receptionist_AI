import os
import dotenv
from pathlib import Path

# Load environment variables from .env file
dotenv.load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Go up to project root
DATA_DIR = BASE_DIR / 'data'

# Directories for data storage
FACES_DIR = DATA_DIR / 'faces'
VOICES_DIR = DATA_DIR / 'voices'
LOGS_DIR = DATA_DIR / 'logs'
RESOURCES_DIR = BASE_DIR / 'resources'

# Ensure directories exist
for directory in [FACES_DIR, VOICES_DIR, LOGS_DIR, RESOURCES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration settings (with defaults)
LOG_INTERVAL = int(os.getenv('LOG_INTERVAL', 30))  # Minimum seconds between logs for the same person
LANGUAGE = os.getenv('LANGUAGE', 'vi')  # Default language

# Face recognition settings
FACE_RECOGNITION_TOLERANCE = float(os.getenv('FACE_RECOGNITION_TOLERANCE', 0.50))  # 0.50 = cân bằng (0.6 = default, quá lỏng)
FACE_RECOGNITION_MODEL = os.getenv('FACE_RECOGNITION_MODEL', 'hog')  # set 'cnn' via env for higher accuracy
FACE_MATCH_MARGIN = float(os.getenv('FACE_MATCH_MARGIN', 0.06))
STRICT_FOLDER_EXISTENCE = os.getenv('STRICT_FOLDER_EXISTENCE', 'true').lower() == 'true'
MIN_FACE_DISTANCE = float(os.getenv('MIN_FACE_DISTANCE', 100))  # Khoảng cách tối thiểu giữa 2 khuôn mặt (pixels)
MIN_CONFIDENCE_THRESHOLD = float(os.getenv('MIN_CONFIDENCE_THRESHOLD', 0.55))  # 0.55 = cân bằng
MIN_FACE_SIZE = int(os.getenv('MIN_FACE_SIZE', 80))  # Kích thước tối thiểu của khuôn mặt (pixels)
FACE_DETECTION_UPSAMPLE = int(os.getenv('FACE_DETECTION_UPSAMPLE', 1))  # Số lần upsample khi detect (1=nhanh, 2=chính xác hơn)
ENABLE_PREPROCESSING = os.getenv('ENABLE_PREPROCESSING', 'false').lower() == 'true'  # Tắt preprocessing mặc định
FACE_CHANGE_THRESHOLD = float(os.getenv('FACE_CHANGE_THRESHOLD', 0.55))  # Ngưỡng để xác định người KHÁC (distance)

# Voice recognition settings
VOICE_CONFIDENCE_THRESHOLD = float(os.getenv('VOICE_CONFIDENCE_THRESHOLD', 0.7))
VOICE_PROCESSING_INTERVAL = 0.2  # seconds
VOICE_ENERGY_THRESHOLD = int(os.getenv('VOICE_ENERGY_THRESHOLD', 450))
VOICE_PAUSE_THRESHOLD = 0.5  # seconds
VOICE_PHRASE_TIME_LIMIT = 3  # seconds
VOICE_TIMEOUT = 0.5  # seconds

# Registration voice tuning
REGISTER_VOICE_TIMEOUT = float(os.getenv('REGISTER_VOICE_TIMEOUT', 2.0))
REGISTER_VOICE_PHRASE_TIME_LIMIT = float(os.getenv('REGISTER_VOICE_PHRASE_TIME_LIMIT', 6.0))
REGISTER_VOICE_CALIBRATE_DURATION = float(os.getenv('REGISTER_VOICE_CALIBRATE_DURATION', 1.0))

# Google Cloud Settings
GOOGLE_CLOUD_CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
GOOGLE_CLOUD_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
GOOGLE_CLOUD_REGION = os.getenv('GOOGLE_CLOUD_REGION', 'asia-southeast1')  # Gần VN để giảm latency
USE_GOOGLE_CLOUD_VOICE = os.getenv('USE_GOOGLE_CLOUD_VOICE', 'false').lower() == 'true'

# UI settings
UI_WINDOW_NAME = os.getenv('UI_WINDOW_NAME', 'AI Receptionist')
UI_WINDOW_WIDTH = int(os.getenv('UI_WINDOW_WIDTH', 800))
UI_WINDOW_HEIGHT = int(os.getenv('UI_WINDOW_HEIGHT', 600))

# Performance settings
TARGET_FPS = int(os.getenv('TARGET_FPS', 60))  # Target FPS for smoother performance

# Greeting messages
GREETINGS = {
    'vi': {
        'welcome': 'Xin chào {name}! Chúc bạn một ngày tốt lành.',
        'welcome_unknown': 'Xin chào quý khách! Tôi có thể giúp gì cho bạn?',
        'goodbye': 'Tạm biệt {name}! Hẹn gặp lại.',
        'help': 'Tôi là trợ lý ảo. Tôi có thể giúp bạn với các thông tin và hướng dẫn.',
    },
    'en': {
        'welcome': 'Hello {name}! Have a nice day.',
        'welcome_unknown': 'Hello! How can I help you?',
        'goodbye': 'Goodbye {name}! See you later.',
        'help': 'I am a virtual assistant. I can help you with information and guidance.',
    }
}

# Get greeting message based on current language setting
def get_greeting(message_type, name=None):
    messages = GREETINGS.get(LANGUAGE, GREETINGS['en'])
    message = messages.get(message_type, '')
    if name:
        return message.format(name=name)
    return message