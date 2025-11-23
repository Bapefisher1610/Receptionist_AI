# Cấu Trúc Dự Án

## 📁 Thư Mục Chính

```
Receptionist_AI/
├── main.py                 # Entry point - Chạy hệ thống
├── requirements.txt        # Dependencies
├── .env.example           # Template cấu hình
├── .env                   # Cấu hình (tạo từ .env.example)
├── README.md              # Hướng dẫn sử dụng
│
├── src/                   # Source code chính
│   ├── core/             # Core logic
│   ├── modules/          # Các module chức năng
│   ├── services/         # External services
│   ├── ui/               # User interface
│   └── utils/            # Utilities
│
├── tools/                # Tools & scripts
│   └── add_user.py       # Đăng ký người dùng mới
│
└── data/                 # Dữ liệu
    ├── faces/            # Dữ liệu khuôn mặt
    ├── voices/           # Dữ liệu giọng nói
    └── logs/             # System logs
```

## 🔧 Chi Tiết src/

### src/core/
- `config.py` - Cấu hình hệ thống
- `main_streaming.py` - Main system logic

### src/modules/
- `face_recognition/` - Module nhận diện khuôn mặt
- `voice_recognition/` - Module nhận diện giọng nói
- `ai_chatbot/` - AI chatbot integration
- `tts/` - Text-to-Speech

### src/services/
- `google_cloud_service.py` - Google Cloud integration
- `google_voice_recognition.py` - Google Voice API

### src/ui/
- `ui.py` - User interface logic

### src/utils/
- `logger.py` - Logging system
- `utils.py` - Helper functions

## 📊 Dữ Liệu

### data/faces/
```
faces/
├── encodings.pkl          # Cache của face encodings
└── [user_id]/            # Thư mục cho mỗi người
    ├── metadata.txt      # Tên người dùng
    └── *.jpg             # Ảnh khuôn mặt
```

### data/voices/
```
voices/
└── patterns.pkl          # Voice patterns
```

### data/logs/
```
logs/
└── *.log                 # System logs
```

## 🚀 Files Quan Trọng

### main.py
Entry point của hệ thống. Chạy file này để khởi động.

### src/core/main_streaming.py
Logic chính của hệ thống:
- Main loop
- Face recognition processing
- Voice command handling
- Registration process
- Camera management

### src/core/config.py
Tất cả cấu hình hệ thống:
- Face recognition parameters
- Voice recognition settings
- Paths
- Thresholds

### tools/add_user.py
Tool để đăng ký người dùng mới:
- Capture face images
- Record voice samples
- Save to database

## 🔄 Luồng Hoạt Động

### 1. Khởi Động
```
main.py
  → StreamingAIReceptionist.__init__()
  → load modules (face, voice, chatbot, ui)
  → start_camera()
  → run()
```

### 2. Main Loop
```
while running:
  → read frame from camera
  → process_face_recognition()
  → check_idle_timeout()
  → update UI
  → handle input
  → render
```

### 3. Nhận Diện
```
process_face_recognition()
  → detect_faces_with_encodings()
  → compare with database
  → check if different person
  → greet or register
```

### 4. Đăng Ký
```
launch_registration_process()
  → release camera
  → run add_user.py
  → capture images
  → record voice
  → save to database
  → restart camera
  → reload encodings
```

## 📝 Files Cấu Hình

### .env
Cấu hình runtime (không commit vào git):
```env
FACE_RECOGNITION_TOLERANCE=0.50
MIN_CONFIDENCE_THRESHOLD=0.55
LANGUAGE=vi
```

### .env.example
Template cấu hình (commit vào git):
```env
FACE_RECOGNITION_TOLERANCE=0.50
MIN_CONFIDENCE_THRESHOLD=0.55
```

## 🗑️ Files Đã Xóa

Các files sau đã được xóa vì không cần thiết:
- `test_system.py` - Test file
- `test_recognition.py` - Test file
- `reset_database.py` - Utility (có thể tạo lại khi cần)
- `FIX_UNKNOWN.md` - Documentation trùng lặp
- `LOGIC_MOI.md` - Documentation trùng lặp
- `HUONG_DAN_SU_DUNG.md` - Đã hợp nhất vào README
- `HUONG_DAN_SUA_LOI.md` - Documentation trùng lặp
- `SUA_LOI_HIEN_THI.md` - Documentation trùng lặp
- `project_overview.md` - Đã hợp nhất vào README
- `src/modules/auto_registration/` - Module không còn dùng

## 📦 Dependencies Chính

Xem `requirements.txt` để biết đầy đủ:
- `opencv-python` - Computer vision
- `face-recognition` - Face recognition
- `SpeechRecognition` - Voice recognition
- `pyttsx3` - Text-to-speech
- `google-cloud-speech` - Google Cloud Speech API
- `google-cloud-texttospeech` - Google Cloud TTS

## 🎯 Điểm Vào (Entry Points)

### Chạy Hệ Thống
```bash
python main.py
```

### Đăng Ký Người Dùng
```bash
python tools/add_user.py
```

---

**Cấu trúc này được tối ưu hóa để dễ bảo trì và mở rộng.**
