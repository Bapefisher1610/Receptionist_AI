# Lễ Tân AI (AI Receptionist)

Hệ thống lễ tân AI với khả năng nhận diện khuôn mặt và giọng nói theo thời gian thực, ghi log theo cách tối ưu.

## Tính năng

- Nhận diện khuôn mặt theo thời gian thực
- Nhận diện giọng nói theo thời gian thực
- Ghi log thông minh (không ghi liên tục, chỉ ghi khi có thay đổi)
- Giao diện người dùng thân thiện
- Hỗ trợ đa ngôn ngữ

## Yêu cầu hệ thống

- Python 3.8 hoặc cao hơn
- Webcam
- Microphone
- Loa (cho phản hồi bằng giọng nói)

## Cài đặt

1. Clone repository này:
```
git clone https://github.com/your-username/Receptionisr_AI.git
cd Receptionisr_AI
```

2. Cài đặt các thư viện cần thiết:
```
pip install -r requirements.txt
```

3. Tạo file `.env` và cấu hình các thông số (tùy chọn):
```
LOG_INTERVAL=30  # Thời gian tối thiểu giữa các lần ghi log (giây)
LANGUAGE=vi      # Ngôn ngữ mặc định (vi, en, ...)
```

4. Chạy ứng dụng:
```
python main.py
```

## Cấu hình

### Thêm người dùng mới

Để thêm người dùng mới vào hệ thống nhận diện:

1. Chạy công cụ thêm người dùng:
```
python add_user.py
```

2. Làm theo hướng dẫn trên màn hình để chụp ảnh và ghi âm giọng nói của người dùng mới.

## Cấu trúc dự án

```
├── main.py                 # Điểm khởi đầu của ứng dụng
├── face_recognition.py     # Module nhận diện khuôn mặt
├── voice_recognition.py    # Module nhận diện giọng nói
├── logger.py               # Module ghi log
├── ui.py                   # Giao diện người dùng
├── add_user.py             # Công cụ thêm người dùng mới
├── utils.py                # Các tiện ích
├── config.py               # Cấu hình ứng dụng
├── data/                   # Thư mục chứa dữ liệu
│   ├── faces/              # Dữ liệu khuôn mặt
│   ├── voices/             # Dữ liệu giọng nói
│   └── logs/               # Nhật ký hệ thống
└── resources/              # Tài nguyên (hình ảnh, âm thanh, ...)
```

## Giấy phép

MIT License