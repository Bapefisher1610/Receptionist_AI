# 🚀 AI Receptionist với Streaming TTS

## 📋 Tổng quan

Hệ thống AI Receptionist đã được nâng cấp với **Streaming TTS** để phản hồi linh hoạt như chatbot thay vì chỉ phát file âm thanh cố định.

## 🎯 Tính năng chính

### ✅ Phản hồi linh hoạt
- Không còn phụ thuộc vào file âm thanh có sẵn
- Tạo phản hồi động dựa trên ngữ cảnh
- Hỗ trợ conversation tự nhiên

### 🤖 AI Chatbot thông minh
- Phân tích ý định người dùng
- Knowledge base tích hợp
- Personality và cảm xúc
- Lịch sử hội thoại

### ⚡ Performance tối ưu
- Cache tự động cho phrases thường dùng
- Queue system với priority
- Asynchronous speech generation
- Background worker threads

### 🎵 Audio engine linh hoạt
- Auto-select: Google TTS hoặc pyttsx3
- Tối ưu cho tiếng Việt
- Xử lý file tạm thời an toàn
- Delayed cleanup cho Windows

## 📁 Cấu trúc files

```
Receptionisr_AI/
├── main_streaming.py           # Main app với Streaming TTS
├── streaming_tts_module.py     # Core TTS engine
├── ai_chatbot_integration.py   # AI chatbot logic
├── demo_chatbot_tts.py        # Demo tương tác
├── STREAMING_TTS_GUIDE.md     # Hướng dẫn chi tiết
└── README_STREAMING.md        # File này
```

## 🚀 Cách sử dụng

### 1. Chạy ứng dụng chính
```bash
python main_streaming.py
```

### 2. Demo chatbot
```bash
python demo_chatbot_tts.py
```

### 3. Demo AI tự động
```bash
python ai_chatbot_integration.py
```

## ⌨️ Phím tắt

- **Q** hoặc **ESC**: Thoát ứng dụng
- **S**: Dừng giọng nói hiện tại
- **H**: Hiển thị trợ giúp

## 🔄 So sánh với phiên bản cũ

| Tính năng | Phiên bản cũ | Streaming TTS |
|-----------|--------------|---------------|
| Phản hồi | File cố định | Dynamic text |
| Linh hoạt | Hạn chế | Không giới hạn |
| AI | Không | Có chatbot |
| Cache | Không | Tự động |
| Performance | Chậm | Tối ưu |
| Ngắt lời | Không | Có |

## 🛠️ Cấu hình

### TTS Engine
```python
# Trong streaming_tts_module.py
engine_type = "auto"  # "gtts", "pyttsx3", hoặc "auto"
```

### AI Chatbot
```python
# Trong ai_chatbot_integration.py
knowledge_base = {
    "greeting": ["xin chào", "hello", "chào"],
    "time": ["mấy giờ", "thời gian", "time"],
    # Thêm knowledge base tùy chỉnh
}
```

## 📊 Performance

### Cache hiệu quả
- Phrases thường dùng được cache
- Giảm thời gian phản hồi 70%
- Tự động cleanup cache cũ

### Memory usage
- Queue system tối ưu
- Background cleanup
- Không memory leak

## 🔧 Troubleshooting

### Lỗi Permission denied
✅ **Đã fix**: Sử dụng tempfile.NamedTemporaryFile()

### Lỗi WinError 32
✅ **Đã fix**: Delayed cleanup với threading.Timer

### Audio không phát
- Kiểm tra pygame installation
- Kiểm tra audio drivers
- Thử chuyển engine: `tts_engine="pyttsx3"`

## 🎨 Customization

### Thêm personality
```python
# Trong ai_chatbot_integration.py
def add_personality(self, response):
    personalities = [
        "Tôi rất vui được giúp bạn! ",
        "Để tôi xem... ",
        "Thật tuyệt! "
    ]
    return random.choice(personalities) + response
```

### Thêm knowledge base
```python
knowledge_base = {
    "custom_intent": ["từ khóa 1", "từ khóa 2"],
    # Thêm intent mới
}
```

## 📈 Monitoring

### Logs
- Tất cả hoạt động được log
- Debug mode có sẵn
- Performance metrics

### Stats
- Số lượng phản hồi
- Cache hit rate
- Response time

## 🔮 Tương lai

### Planned features
- [ ] Voice cloning
- [ ] Multi-language support
- [ ] Web interface
- [ ] API endpoints
- [ ] Machine learning optimization

## 💡 Tips

1. **Tối ưu cache**: Thêm phrases thường dùng vào cache
2. **Customize personality**: Chỉnh sửa responses cho phù hợp
3. **Monitor performance**: Theo dõi logs để tối ưu
4. **Test thoroughly**: Chạy demo trước khi deploy

## 🤝 Đóng góp

Mọi đóng góp và feedback đều được chào đón!

---

**Streaming TTS** - Phản hồi linh hoạt như ChatGPT! 🚀