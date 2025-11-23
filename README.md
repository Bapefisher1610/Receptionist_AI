# Lễ Tân AI (AI Receptionist)

Hệ thống lễ tân AI với khả năng nhận diện khuôn mặt và giọng nói theo thời gian thực.

## ✨ Tính Năng

- 🎭 **Nhận diện khuôn mặt** - Tự động nhận diện và chào hỏi người quen
- 🎤 **Nhận diện giọng nói** - Tương tác bằng giọng nói tự nhiên
- 🤖 **AI Chatbot** - Trả lời câu hỏi và hỗ trợ khách hàng
- 📝 **Ghi log thông minh** - Chỉ ghi khi có thay đổi
- 🌐 **Đa ngôn ngữ** - Hỗ trợ tiếng Việt và tiếng Anh
- 🔄 **Tự động đăng ký** - Phát hiện người mới và mở form đăng ký

## 🚀 Cài Đặt

### Yêu Cầu Hệ Thống

- Python 3.8 hoặc cao hơn
- Webcam
- Microphone
- Loa (cho phản hồi bằng giọng nói)

### Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### Cấu Hình (Tùy Chọn)

Tạo file `.env` để tùy chỉnh:

```bash
copy .env.example .env
```

Chỉnh sửa các tham số trong `.env`:

```env
# Nhận diện khuôn mặt
FACE_RECOGNITION_TOLERANCE=0.50
MIN_CONFIDENCE_THRESHOLD=0.55

# Ngôn ngữ
LANGUAGE=vi
```

## 📖 Sử Dụng

### Chạy Hệ Thống

```bash
python main.py
```

### Đăng Ký Người Dùng Mới

Khi hệ thống phát hiện người lạ, sẽ tự động mở form đăng ký.

Hoặc chạy thủ công:

```bash
python tools/add_user.py
```

**Quy trình đăng ký:**
1. Nhập tên người dùng
2. Chụp 5 ảnh khuôn mặt (nhấn SPACE)
3. Ghi âm 3 câu giọng nói
4. Hoàn tất!

### Phím Tắt

| Phím | Chức năng |
|------|-----------|
| `Q` hoặc `ESC` | Thoát hệ thống |
| `S` | Dừng giọng nói |
| `H` | Hiển thị trợ giúp |
| `R` | Reload danh sách người dùng |
| `C` | Xóa cache nhận diện |

## 🎯 Cách Hoạt Động

### Nhận Diện Người Quen

```
Camera phát hiện khuôn mặt
    ↓
So sánh với database
    ↓
Nhận diện thành công
    ↓
"Xin chào [Tên]!"
```

### Phát Hiện Người Mới

```
Camera phát hiện khuôn mặt
    ↓
Không khớp với database
    ↓
Phát hiện người KHÁC
    ↓
Tự động mở form đăng ký
    ↓
Người dùng đăng ký
    ↓
Hệ thống nhận diện ngay lập tức
```

## ⚙️ Cấu Hình Nâng Cao

### Điều Chỉnh Độ Chính Xác

Nếu hệ thống không nhận diện được hoặc nhận diện sai, điều chỉnh trong `.env`:

```env
# Dễ nhận diện hơn (có thể nhầm)
FACE_RECOGNITION_TOLERANCE=0.60
MIN_CONFIDENCE_THRESHOLD=0.45

# Chặt chẽ hơn (ít nhầm)
FACE_RECOGNITION_TOLERANCE=0.45
MIN_CONFIDENCE_THRESHOLD=0.60
```

### Bật Preprocessing (Cải thiện ánh sáng)

```env
ENABLE_PREPROCESSING=true
```

### Sử Dụng Model CNN (Chính xác hơn)

```env
FACE_RECOGNITION_MODEL=cnn
```

**Lưu ý:** CNN chậm hơn và cần GPU.

## 📁 Cấu Trúc Dự Án

```
├── main.py                 # Entry point
├── src/
│   ├── core/              # Core logic
│   │   ├── config.py      # Cấu hình
│   │   └── main_streaming.py  # Main system
│   ├── modules/           # Các module chức năng
│   │   ├── face_recognition/
│   │   ├── voice_recognition/
│   │   ├── ai_chatbot/
│   │   └── tts/
│   ├── services/          # External services
│   ├── ui/                # User interface
│   └── utils/             # Utilities
├── tools/
│   └── add_user.py        # Tool đăng ký người dùng
├── data/
│   ├── faces/             # Dữ liệu khuôn mặt
│   ├── voices/            # Dữ liệu giọng nói
│   └── logs/              # Logs
└── requirements.txt       # Dependencies
```

## 🐛 Xử Lý Sự Cố

### Không Nhận Diện Được

1. Kiểm tra ánh sáng (đủ sáng, không quá tối/chói)
2. Nhìn thẳng vào camera
3. Nhấn `R` để reload database
4. Điều chỉnh tolerance trong `.env`

### Nhận Diện Sai

1. Tăng `MIN_CONFIDENCE_THRESHOLD`
2. Giảm `FACE_RECOGNITION_TOLERANCE`
3. Đăng ký lại với ảnh chất lượng tốt hơn

### Camera Không Hoạt Động

1. Đảm bảo không có app nào khác đang dùng camera
2. Kiểm tra quyền truy cập camera
3. Restart hệ thống

### Không Nghe Được Giọng Nói

1. Kiểm tra microphone đã kết nối
2. Tăng `VOICE_ENERGY_THRESHOLD`
3. Nói to và rõ ràng hơn
4. Giảm tiếng ồn xung quanh

## 💡 Tips

### Để Nhận Diện Tốt Nhất

- ✅ Ánh sáng đủ, không quá tối/chói
- ✅ Nhìn thẳng vào camera
- ✅ Khoảng cách 50-100cm
- ✅ Không đeo khẩu trang, kính đen
- ✅ Background đơn giản

### Khi Đăng Ký

- ✅ Chụp từ nhiều góc độ
- ✅ Biểu cảm tự nhiên
- ✅ Ánh sáng đều
- ✅ Nói rõ ràng khi ghi âm

## 📊 Thông Số Kỹ Thuật

### Độ Chính Xác

- Face Recognition: ~95% (điều kiện tốt)
- Voice Recognition: ~90%
- Response Time: < 3 giây

### Hiệu Suất

- FPS: 30-60 (tùy hardware)
- CPU Usage: 30-50%
- RAM Usage: 500MB-1GB

## 🔐 Bảo Mật & Quyền Riêng Tư

- Dữ liệu được lưu trữ local
- Không upload lên cloud (trừ Google Speech API)
- Có thể hoạt động offline (trừ voice recognition)

## 📝 License

MIT License

## 🤝 Đóng Góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## 📧 Liên Hệ

Nếu có vấn đề hoặc câu hỏi, vui lòng tạo issue trên GitHub.

---

**Phiên bản:** 2.0  
**Cập nhật:** 2025-11-21
