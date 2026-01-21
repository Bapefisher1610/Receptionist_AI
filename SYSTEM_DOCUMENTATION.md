# 📚 TÀI LIỆU HỆ THỐNG AI RECEPTIONIST - TỔNG QUAN TOÀN DIỆN

> **Phiên bản:** 2.0  
> **Ngày cập nhật:** 06/12/2025  
> **Tác giả:** AI Receptionist Development Team

---

## 📋 MỤC LỤC

1. [Tổng Quan Hệ Thống](#1-tổng-quan-hệ-thống)
2. [Kiến Trúc Hệ Thống](#2-kiến-trúc-hệ-thống)
3. [Các Module Chính](#3-các-module-chính)
4. [Quy Trình Hoạt Động](#4-quy-trình-hoạt-động)
5. [Cấu Hình Chi Tiết](#5-cấu-hình-chi-tiết)
6. [API và Interfaces](#6-api-và-interfaces)
7. [Dữ Liệu và Lưu Trữ](#7-dữ-liệu-và-lưu-trữ)
8. [Bảo Mật và Quyền Riêng Tư](#8-bảo-mật-và-quyền-riêng-tư)
9. [Performance và Tối Ưu](#9-performance-và-tối-ưu)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1. Giới Thiệu

**AI Receptionist** là một hệ thống lễ tân thông minh sử dụng công nghệ AI để:
- Nhận diện khuôn mặt theo thời gian thực
- Tương tác bằng giọng nói tự nhiên
- Trả lời câu hỏi và hỗ trợ khách hàng
- Tự động đăng ký người dùng mới
- Ghi log và theo dõi hoạt động

### 1.2. Mục Đích Sử Dụng

- **Văn phòng**: Quản lý ra vào, chào đón nhân viên
- **Khách sạn**: Tiếp đón khách, cung cấp thông tin
- **Cửa hàng**: Nhận diện khách quen, hỗ trợ mua sắm
- **Bệnh viện**: Hướng dẫn bệnh nhân, quản lý lịch hẹn
- **Trường học**: Quản lý học sinh, phụ huynh

### 1.3. Tính Năng Chính

#### ✅ Nhận Diện Khuôn Mặt
- Độ chính xác: ~95% (điều kiện tốt)
- Thời gian phản hồi: < 1 giây
- Hỗ trợ nhiều khuôn mặt cùng lúc
- Tự động phát hiện người mới

#### ✅ Nhận Diện Giọng Nói
- Hỗ trợ tiếng Việt và tiếng Anh
- Độ chính xác: ~90%
- Xử lý nhiễu thông minh
- Tích hợp Google Speech API

#### ✅ AI Chatbot
- Phản hồi thông minh
- Học từ ngữ cảnh
- Đa ngôn ngữ
- Streaming TTS

#### ✅ Tự Động Đăng Ký
- Phát hiện người lạ
- Quy trình đăng ký nhanh (chỉ 5 ảnh)
- Tự động cập nhật database
- Nhận diện ngay lập tức

### 1.4. Công Nghệ Sử Dụng

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| Python | 3.8+ | Ngôn ngữ chính |
| OpenCV | 4.8.1 | Xử lý hình ảnh |
| face_recognition | 1.3.0 | Nhận diện khuôn mặt |
| dlib | 19.24.1 | Machine learning |
| SpeechRecognition | 3.10.0 | Nhận diện giọng nói |
| pyttsx3 | 2.90 | Text-to-Speech offline |
| gTTS | Latest | Text-to-Speech online |
| pygame | Latest | Phát audio |
| Google Cloud APIs | Latest | Speech & TTS nâng cao |

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1. Sơ Đồ Tổng Quan

```
┌─────────────────────────────────────────────────────────────┐
│                    AI RECEPTIONIST SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Camera     │───▶│ Face Module  │───▶│  Recognition │  │
│  │   Input      │    │  Processing  │    │   Database   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Microphone  │───▶│ Voice Module │───▶│  AI Chatbot  │  │
│  │   Input      │    │  Processing  │    │   Response   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │     UI       │◀───│  Main Loop   │───▶│   Logging    │  │
│  │   Display    │    │  Controller  │    │   System     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2. Cấu Trúc Thư Mục

```
Receptionist_AI/
│
├── main.py                          # Entry point chính
├── requirements.txt                 # Dependencies
├── .env.example                     # Cấu hình mẫu
├── .env                            # Cấu hình thực tế (không commit)
│
├── src/                            # Source code chính
│   ├── __init__.py
│   │
│   ├── core/                       # Core logic
│   │   ├── __init__.py
│   │   ├── config.py              # Cấu hình toàn cục
│   │   ├── main_streaming.py     # Main system controller
│   │   └── inline_registration.py # Đăng ký người dùng
│   │
│   ├── modules/                    # Các module chức năng
│   │   ├── __init__.py
│   │   │
│   │   ├── face_recognition/      # Nhận diện khuôn mặt
│   │   │   ├── __init__.py
│   │   │   └── face_recognition_module.py
│   │   │
│   │   ├── voice_recognition/     # Nhận diện giọng nói
│   │   │   ├── __init__.py
│   │   │   └── voice_recognition_module.py
│   │   │
│   │   ├── ai_chatbot/           # AI Chatbot
│   │   │   ├── __init__.py
│   │   │   └── ai_chatbot_integration.py
│   │   │
│   │   └── tts/                  # Text-to-Speech
│   │       ├── __init__.py
│   │       ├── streaming_tts_module.py
│   │       └── enhanced_tts_module.py
│   │
│   ├── ui/                        # User Interface
│   │   ├── __init__.py
│   │   └── ui.py
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── logger.py             # Logging system
│       └── utils.py              # Helper functions
│
├── tools/                         # Tools và scripts
│   └── add_user.py               # Tool đăng ký thủ công
│
├── data/                          # Dữ liệu hệ thống
│   ├── faces/                    # Dữ liệu khuôn mặt
│   │   ├── [user_id]/           # Thư mục mỗi người
│   │   │   ├── metadata.txt     # Tên người dùng
│   │   │   └── *.jpg            # Ảnh khuôn mặt
│   │   └── encodings.pkl        # Face encodings cache
│   │
│   ├── voices/                   # Dữ liệu giọng nói
│   │   └── patterns.pkl         # Voice patterns
│   │
│   └── logs/                     # Logs
│       ├── system_YYYYMMDD.log
│       ├── reception_YYYYMMDD.log
│       └── detailed_YYYYMMDD.log
│
├── docs/                          # Tài liệu
│   ├── README_GOOGLE_CLOUD.md
│   └── README_STREAMING.md
│
└── tests/                         # Tests (future)
```

---

## 3. CÁC MODULE CHÍNH

### 3.1. Face Recognition Module

**File:** `src/modules/face_recognition/face_recognition_module.py`

#### Chức năng:
- Load và quản lý face encodings
- Detect faces trong frame
- So sánh và nhận diện
- Thêm người dùng mới
- Lọc duplicate faces

#### Thuật toán:
```python
# 1. Face Detection
face_locations = face_recognition.face_locations(frame, model='hog')

# 2. Face Encoding
face_encodings = face_recognition.face_encodings(frame, face_locations)

# 3. Face Comparison
distances = face_recognition.face_distance(known_encodings, face_encoding)

# 4. Decision Making
if distance <= TOLERANCE and confidence >= MIN_CONFIDENCE:
    # Matched!
```

#### Cấu hình quan trọng:

```python
FACE_RECOGNITION_TOLERANCE = 0.55      # Ngưỡng distance (0.0-1.0)
MIN_CONFIDENCE_THRESHOLD = 0.50        # Ngưỡng confidence (0.0-1.0)
FACE_RECOGNITION_MODEL = 'hog'         # 'hog' hoặc 'cnn'
MIN_FACE_SIZE = 80                     # Kích thước tối thiểu (pixels)
FACE_DETECTION_UPSAMPLE = 1            # Số lần upsample
ENABLE_PREPROCESSING = False           # Tiền xử lý ảnh
```

#### Methods chính:

**`load_known_faces()`**
- Load face encodings từ file hoặc images
- Cache vào `encodings.pkl` để tăng tốc

**`recognize_faces(frame)`**
- Nhận diện tất cả khuôn mặt trong frame
- Trả về list các face data với confidence

**`add_face(face_image, person_id, person_name)`**
- Thêm khuôn mặt mới vào database
- Lưu ảnh và metadata
- Cập nhật encodings

**`_remove_duplicate_faces(results)`**
- Loại bỏ khuôn mặt trùng lặp
- Giữ face có confidence cao nhất

### 3.2. Voice Recognition Module

**File:** `src/modules/voice_recognition/voice_recognition_module.py`

#### Chức năng:
- Nhận diện giọng nói thành text
- Pattern matching với voice patterns
- Quản lý voice patterns database
- Background listening

#### Engine:
- **Google Speech Recognition API** (mặc định)
- **Google Cloud Speech API** (tùy chọn)

#### Cấu hình:
```python
VOICE_ENERGY_THRESHOLD = 450           # Ngưỡng năng lượng
VOICE_PAUSE_THRESHOLD = 0.5            # Thời gian pause (s)
VOICE_PHRASE_TIME_LIMIT = 3            # Thời gian tối đa (s)
VOICE_TIMEOUT = 0.5                    # Timeout (s)
VOICE_CONFIDENCE_THRESHOLD = 0.7       # Ngưỡng confidence
```

#### Methods chính:

**`listen_for_command(timeout, phrase_time_limit)`**
- Lắng nghe và nhận diện giọng nói
- Trả về text hoặc None

**`recognize_speech(audio)`**
- Chuyển audio thành text
- Match với known patterns
- Trả về person_id nếu match

**`add_voice_pattern(person_id, person_name, keywords)`**
- Thêm voice pattern mới
- Lưu vào `patterns.pkl`

### 3.3. TTS (Text-to-Speech) Module

**File:** `src/modules/tts/streaming_tts_module.py`

#### Chức năng:
- Chuyển text thành giọng nói
- Streaming audio playback
- Queue management với priority
- Caching audio files

#### Engines:

**1. Auto Selection (Thông minh)**
```python
if internet_available and gTTS_available:
    use gTTS  # Chất lượng cao
else:
    use pyttsx3  # Offline fallback
```

**2. Google TTS (gTTS)**
- Giọng nói tự nhiên
- Hỗ trợ tiếng Việt tốt
- Cần internet

**3. pyttsx3**
- Hoạt động offline
- Phản hồi nhanh
- Giọng ít tự nhiên hơn

#### Methods chính:

**`speak_async(text, priority)`**
- Thêm vào queue
- Xử lý background

**`speak_immediate(text)`**
- Ngắt giọng hiện tại
- Nói ngay lập tức

**`stop_current_speech()`**
- Dừng giọng nói
- Clear queue

### 3.4. AI Chatbot Module

**File:** `src/modules/ai_chatbot/ai_chatbot_integration.py`

#### Chức năng:
- Phân tích intent từ input
- Generate response phù hợp
- Quản lý conversation history
- Tích hợp TTS

#### Knowledge Base:

```python
knowledge_base = {
    "greetings": {
        "patterns": ["xin chào", "hello", "chào"],
        "responses": ["Tôi có thể giúp gì cho bạn?", ...]
    },
    "thanks": {...},
    "goodbye": {...},
    "time": {...},
    "weather": {...},
    "help": {...},
    "name": {...}
}
```

#### Methods chính:

**`process_input(user_input)`**
- Phân tích intent
- Generate response
- Thêm personality

**`speak_response(user_input, priority)`**
- Process và nói response

**`speak_direct(message, priority)`**
- Nói trực tiếp không qua AI

### 3.5. Inline Registration Module

**File:** `src/core/inline_registration.py`

#### Chức năng:
- Đăng ký người dùng mới inline
- Chụp 5 ảnh tự động
- Quản lý registration state
- Tự động reload database

#### Quy trình:
```
1. start() → Khởi tạo đăng ký
2. get_name → Nhận tên qua giọng nói
3. capture_face → Chụp 5 ảnh (1.2s/ảnh)
4. completed → Lưu và reload
5. reset() → Dọn dẹp
```

#### State Machine:
```python
state = {
    'step': 'get_name',  # get_name → capture_face → completed
    'name': '',
    'face_count': 0,
    'max_faces': 5
}
```

#### Methods chính:

**`start()`**
- Bắt đầu đăng ký
- Tạo user_id và thư mục

**`process(frame, detected_faces)`**
- Xử lý từng step
- Kiểm tra người quen (hủy nếu cần)

**`handle_voice_input(text)`**
- Xử lý input giọng nói
- Trích xuất tên

**`complete()`**
- Lưu metadata
- Đánh dấu hoàn tất

---

## 4. QUY TRÌNH HOẠT ĐỘNG

### 4.1. Main Loop

**File:** `src/core/main_streaming.py`

```python
while running:
    # 1. Capture frame
    ret, frame = camera.read()
    
    # 2. Face recognition
    faces = face_module.recognize_faces(frame)
    
    # 3. Process faces
    process_face_recognition(faces)
    
    # 4. Handle registration
    if registration.is_active:
        should_cancel = registration.process(frame, faces)
        if should_cancel:
            registration.cancel()
    
    # 5. Update UI
    ui.update_frame(frame)
    ui.render()
    
    # 6. Handle keyboard input
    key = cv2.waitKey(1)
```

### 4.2. Nhận Diện Người Quen

```
Camera → Detect Face → Extract Encoding
    ↓
Compare with Database
    ↓
distance <= TOLERANCE?
    ↓ YES
confidence >= MIN_CONFIDENCE?
    ↓ YES
MATCHED! → Log → Greet
```

### 4.3. Phát Hiện Người Mới

```
Camera → Detect Face → Extract Encoding
    ↓
Compare with Database
    ↓
No Match (Unknown)
    ↓
Different from current_face?
    ↓ YES
New Person Detected!
    ↓
Start Registration
```

### 4.4. Quy Trình Đăng Ký

```
1. Detect Unknown Face
    ↓
2. Speak: "Xin chào! Bạn là người mới..."
    ↓
3. Speak: "Vui lòng nói tên của bạn"
    ↓
4. Listen for Name
    ↓
5. Extract Name from Speech
    ↓
6. Speak: "Xin chào [Tên]! Bây giờ chụp ảnh..."
    ↓
7. Auto Capture 5 Photos (1.2s interval)
    ↓
8. Save Photos + Metadata
    ↓
9. Update encodings.pkl
    ↓
10. Reload Face Database
    ↓
11. Speak: "Hoàn tất! Đăng ký thành công!"
    ↓
12. Reset Registration State
```

### 4.5. Voice Command Processing

```
Microphone → Listen
    ↓
Capture Audio
    ↓
Google Speech API
    ↓
Text Output
    ↓
If Registration Active:
    → Handle Registration Input
Else:
    → AI Chatbot Process
    ↓
Generate Response
    ↓
TTS Speak Response
```

---

## 5. CẤU HÌNH CHI TIẾT

### 5.1. File .env

```bash
# ============================================
# FACE RECOGNITION SETTINGS
# ============================================

# Tolerance: Ngưỡng distance để chấp nhận match
# 0.6 = default (cân bằng)
# 0.5 = chặt (ít false positive)
# 0.7 = lỏng (dễ nhận diện nhưng có thể nhầm)
FACE_RECOGNITION_TOLERANCE=0.55

# Confidence tối thiểu (0.0 - 1.0)
# Càng cao càng chặt chẽ
MIN_CONFIDENCE_THRESHOLD=0.50

# Model: 'hog' (nhanh, CPU) hoặc 'cnn' (chính xác, GPU)
FACE_RECOGNITION_MODEL=hog

# Kích thước khuôn mặt tối thiểu (pixels)
MIN_FACE_SIZE=80

# Số lần upsample khi detect
# 1 = nhanh, 2 = chính xác hơn
FACE_DETECTION_UPSAMPLE=1

# Bật preprocessing (cải thiện ánh sáng)
# true/false
ENABLE_PREPROCESSING=false

# Ngưỡng để xác định người KHÁC
FACE_CHANGE_THRESHOLD=0.55

# ============================================
# VOICE RECOGNITION SETTINGS
# ============================================

# Ngưỡng năng lượng âm thanh
VOICE_ENERGY_THRESHOLD=450

# Thời gian pause để kết thúc câu (seconds)
VOICE_PAUSE_THRESHOLD=0.5

# Thời gian tối đa cho một câu (seconds)
VOICE_PHRASE_TIME_LIMIT=3

# Timeout chờ âm thanh (seconds)
VOICE_TIMEOUT=0.5

# Ngưỡng confidence
VOICE_CONFIDENCE_THRESHOLD=0.7

# ============================================
# REGISTRATION SETTINGS
# ============================================

# Timeout cho voice input khi đăng ký
REGISTER_VOICE_TIMEOUT=2.0

# Thời gian tối đa cho câu khi đăng ký
REGISTER_VOICE_PHRASE_TIME_LIMIT=6.0

# Thời gian calibrate microphone
REGISTER_VOICE_CALIBRATE_DURATION=1.0

# ============================================
# GOOGLE CLOUD SETTINGS (Optional)
# ============================================

# Path to credentials JSON file
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Project ID
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Region (gần VN để giảm latency)
GOOGLE_CLOUD_REGION=asia-southeast1

# Sử dụng Google Cloud Voice (true/false)
USE_GOOGLE_CLOUD_VOICE=false

# ============================================
# SYSTEM SETTINGS
# ============================================

# Ngôn ngữ: 'vi' hoặc 'en'
LANGUAGE=vi

# Khoảng thời gian tối thiểu giữa 2 log (seconds)
LOG_INTERVAL=30

# Target FPS
TARGET_FPS=60

# UI Settings
UI_WINDOW_NAME=AI Receptionist
UI_WINDOW_WIDTH=800
UI_WINDOW_HEIGHT=600
```

### 5.2. Config.py Structure

**File:** `src/core/config.py`

```python
# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
FACES_DIR = DATA_DIR / 'faces'
VOICES_DIR = DATA_DIR / 'voices'
LOGS_DIR = DATA_DIR / 'logs'
RESOURCES_DIR = BASE_DIR / 'resources'

# Load from .env
FACE_RECOGNITION_TOLERANCE = float(os.getenv('FACE_RECOGNITION_TOLERANCE', 0.55))
MIN_CONFIDENCE_THRESHOLD = float(os.getenv('MIN_CONFIDENCE_THRESHOLD', 0.50))
# ... etc
```

---

## 6. API VÀ INTERFACES

### 6.1. Face Recognition API

```python
# Initialize
face_module = FaceRecognitionModule(logger)

# Load faces
face_module.load_known_faces()

# Recognize
faces = face_module.recognize_faces(frame)
# Returns: [{'name': str, 'person_id': str, 'confidence': float, 'location': tuple}]

# Add new face
success = face_module.add_face(face_image, person_id, person_name)
```

### 6.2. Voice Recognition API

```python
# Initialize
voice_module = VoiceRecognitionModule(logger)

# Listen
text = voice_module.listen_for_command(timeout=2, phrase_time_limit=4)
# Returns: str or None

# Add pattern
voice_module.add_voice_pattern(person_id, person_name, keywords)
```

### 6.3. TTS API

```python
# Initialize
tts = StreamingTTSModule(engine_type="auto")

# Speak async
tts.speak_async("Xin chào!", priority="normal")

# Speak immediate (interrupt)
tts.speak_immediate("Khẩn cấp!")

# Stop
tts.stop_current_speech()

# Check status
is_busy = tts.is_busy()
```

### 6.4. AI Chatbot API

```python
# Initialize
chatbot = AIReceptionistChatbot(tts_engine="auto")

# Process and speak
response = chatbot.speak_response(user_input, priority="normal")

# Direct speak
chatbot.speak_direct("Hello!", priority="high")

# Interrupt
chatbot.interrupt_and_respond("Urgent message!")
```

### 6.5. Registration API

```python
# Initialize
registration = InlineRegistration(face_module, voice_module, logger, ui)

# Start
success = registration.start()

# Process
should_cancel = registration.process(frame, detected_faces)

# Handle voice
response = registration.handle_voice_input(text)

# Complete
success = registration.complete()

# Cancel
registration.cancel()

# Reset
registration.reset()
```

---

## 7. DỮ LIỆU VÀ LƯU TRỮ

### 7.1. Face Data Structure

```
data/faces/
├── [user_id_1]/              # UUID 8 ký tự
│   ├── metadata.txt          # Tên người dùng (UTF-8)
│   ├── 1234567890.jpg       # Ảnh 1 (timestamp)
│   ├── 1234567891.jpg       # Ảnh 2
│   ├── 1234567892.jpg       # Ảnh 3
│   ├── 1234567893.jpg       # Ảnh 4
│   └── 1234567894.jpg       # Ảnh 5
├── [user_id_2]/
│   └── ...
└── encodings.pkl             # Cache tất cả encodings
```

**encodings.pkl format:**
```python
{
    'encodings': [array1, array2, ...],  # Face encodings (128-d vectors)
    'names': ['Name1', 'Name2', ...],    # Tên tương ứng
    'ids': ['id1', 'id2', ...]           # User IDs
}
```

### 7.2. Voice Data Structure

```
data/voices/
└── patterns.pkl              # Voice patterns
```

**patterns.pkl format:**
```python
{
    'user_id_1': {
        'name': 'Name1',
        'keywords': ['keyword1', 'keyword2', ...]
    },
    'user_id_2': {...}
}
```

### 7.3. Logs Structure

```
data/logs/
├── system_20251206.log       # System events
├── reception_20251206.log    # Recognition events (CSV)
└── detailed_20251206.log     # Detailed logs (JSON)
```

**reception log format (CSV):**
```csv
timestamp,person_id,person_name,recognition_type,confidence,action
2025-12-06 15:30:45,abc123,John,face,0.95,detected
```

**detailed log format (JSON):**
```json
{
  "logs": [
    {
      "timestamp": "2025-12-06 15:30:45",
      "person_id": "abc123",
      "person_name": "John",
      "recognition_type": "face",
      "confidence": 0.95,
      "action": "detected"
    }
  ]
}
```

---

## 8. BẢO MẬT VÀ QUYỀN RIÊNG TƯ

### 8.1. Lưu Trữ Dữ Liệu

- **Local Storage**: Tất cả dữ liệu lưu local
- **No Cloud Upload**: Không upload ảnh/video lên cloud
- **Encrypted**: Có thể mã hóa thư mục data/

### 8.2. API Keys

- Google Speech API: Miễn phí với giới hạn
- Google Cloud: Cần credentials (tùy chọn)
- Không lưu API keys trong code

### 8.3. GDPR Compliance

- **Right to Access**: User có thể xem dữ liệu
- **Right to Delete**: Xóa thư mục user_id
- **Right to Portability**: Export dữ liệu
- **Consent**: Cần consent trước khi đăng ký

### 8.4. Best Practices

```python
# 1. Không commit .env
.gitignore:
.env
data/

# 2. Mã hóa sensitive data
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)

# 3. Giới hạn quyền truy cập
os.chmod('data/', 0o700)

# 4. Audit logs
logger.log_system_event('access', f'User {user_id} accessed')
```

---

## 9. PERFORMANCE VÀ TỐI ƯU

### 9.1. Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Face Recognition | < 1s | ~0.5s |
| Voice Recognition | < 3s | ~2s |
| TTS Response | < 2s | ~1s |
| FPS | 30-60 | 40-50 |
| CPU Usage | < 50% | 30-40% |
| RAM Usage | < 1GB | 500-800MB |

### 9.2. Optimization Techniques

#### Face Recognition:
```python
# 1. Resize frame
small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

# 2. Use HOG instead of CNN
model = 'hog'  # 10x faster

# 3. Cache encodings
encodings.pkl  # Load once, use many times

# 4. Skip frames
if frame_count % 2 == 0:  # Process every 2nd frame
    recognize_faces()
```

#### Voice Recognition:
```python
# 1. Adjust energy threshold
recognizer.energy_threshold = 450

# 2. Dynamic threshold
recognizer.dynamic_energy_threshold = True

# 3. Shorter timeout
timeout = 0.5  # seconds
```

#### TTS:
```python
# 1. Cache audio files
self.cache = {}  # Frequently used phrases

# 2. Background processing
threading.Thread(target=speak_worker)

# 3. Queue management
priority_queue = queue.PriorityQueue()
```

### 9.3. Hardware Requirements

**Minimum:**
- CPU: Intel i3 / AMD Ryzen 3
- RAM: 4GB
- Webcam: 720p
- Microphone: Any

**Recommended:**
- CPU: Intel i5 / AMD Ryzen 5
- RAM: 8GB
- Webcam: 1080p
- Microphone: Noise-cancelling
- GPU: Optional (for CNN model)

---

## 10. TROUBLESHOOTING

### 10.1. Không Nhận Diện Được

**Triệu chứng:** Luôn hiện "Unknown"

**Nguyên nhân & Giải pháp:**

1. **Ánh sáng kém**
   - Kiểm tra: Đủ sáng, không quá tối/chói
   - Giải pháp: Bật đèn, tránh backlight

2. **Tolerance quá chặt**
   ```bash
   # .env
   FACE_RECOGNITION_TOLERANCE=0.60  # Tăng lên
   MIN_CONFIDENCE_THRESHOLD=0.45    # Giảm xuống
   ```

3. **Ảnh đăng ký kém chất lượng**
   - Đăng ký lại với ảnh tốt hơn
   - Nhiều góc độ khác nhau

4. **Cache cũ**
   ```bash
   # Xóa cache
   del data/faces/encodings.pkl
   # Restart app
   ```

### 10.2. Nhận Diện Sai

**Triệu chứng:** Nhận diện nhầm người

**Giải pháp:**

1. **Tăng độ chặt chẽ**
   ```bash
   FACE_RECOGNITION_TOLERANCE=0.45
   MIN_CONFIDENCE_THRESHOLD=0.60
   ```

2. **Xóa người bị nhầm**
   ```bash
   # Xóa thư mục
   rm -rf data/faces/[wrong_user_id]
   # Reload
   ```

3. **Kiểm tra duplicate**
   - Một người có nhiều ID
   - Merge hoặc xóa duplicate

### 10.3. Camera Không Hoạt Động

**Triệu chứng:** "Cannot open camera"

**Giải pháp:**

1. **App khác đang dùng camera**
   - Đóng Zoom, Skype, etc.
   - Restart app

2. **Quyền truy cập**
   - Windows: Settings → Privacy → Camera
   - Mac: System Preferences → Security → Camera

3. **Driver**
   - Cập nhật camera driver
   - Thử camera khác

### 10.4. Không Nghe Được Giọng Nói

**Triệu chứng:** "Speech was unintelligible"

**Giải pháp:**

1. **Microphone không hoạt động**
   - Kiểm tra kết nối
   - Test microphone

2. **Nhiễu quá lớn**
   ```bash
   VOICE_ENERGY_THRESHOLD=600  # Tăng lên
   ```

3. **Nói không rõ**
   - Nói to hơn
   - Nói chậm hơn
   - Giảm tiếng ồn

4. **Internet**
   - Google Speech API cần internet
   - Kiểm tra kết nối

### 10.5. TTS Không Phát Âm

**Triệu chứng:** Không có giọng nói

**Giải pháp:**

1. **Loa tắt tiếng**
   - Kiểm tra volume
   - Unmute

2. **Engine lỗi**
   ```python
   # Thử engine khác
   tts = StreamingTTSModule(engine_type="pyttsx3")
   ```

3. **pygame lỗi**
   ```bash
   pip uninstall pygame
   pip install pygame
   ```

### 10.6. Performance Kém

**Triệu chứng:** FPS thấp, lag

**Giải pháp:**

1. **Giảm resolution**
   ```python
   camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   ```

2. **Skip frames**
   ```python
   if frame_count % 3 == 0:  # Process every 3rd frame
       recognize_faces()
   ```

3. **Đóng app khác**
   - Giải phóng CPU/RAM
   - Đóng browser tabs

4. **Upgrade hardware**
   - Thêm RAM
   - CPU mạnh hơn

### 10.7. Đăng Ký Bị Hủy

**Triệu chứng:** "Phát hiện người quen - Hủy đăng ký"

**Giải pháp:**

1. **Người khác vào frame**
   - Đảm bảo chỉ 1 người
   - Đăng ký lại

2. **Nhận diện nhầm**
   - Tăng tolerance tạm thời
   - Đăng ký xong mới giảm

### 10.8. Lỗi Import

**Triệu chứng:** "ModuleNotFoundError"

**Giải pháp:**

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Hoặc cài từng package
pip install opencv-python
pip install face-recognition
pip install SpeechRecognition
pip install pyttsx3
```

### 10.9. Encoding Error

**Triệu chứng:** "UnicodeDecodeError"

**Giải pháp:**

```python
# Đảm bảo UTF-8
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# Windows: Chcp 65001
```

### 10.10. Log Files Quá Lớn

**Giải pháp:**

```bash
# Xóa log cũ
rm data/logs/*_202411*.log

# Hoặc archive
tar -czf logs_backup.tar.gz data/logs/
rm data/logs/*.log
```

---

## 📞 HỖ TRỢ VÀ LIÊN HỆ

### Báo Lỗi
- Tạo issue trên GitHub
- Mô tả chi tiết vấn đề
- Attach logs nếu có

### Đóng Góp
- Fork repository
- Tạo feature branch
- Submit pull request

### Tài Liệu Thêm
- `docs/README_GOOGLE_CLOUD.md` - Google Cloud setup
- `docs/README_STREAMING.md` - Streaming architecture
- `README.md` - Quick start guide

---

**© 2025 AI Receptionist Development Team**  
**Version:** 2.0  
**Last Updated:** 06/12/2025
