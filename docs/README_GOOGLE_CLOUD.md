# 🌐 Google Cloud Integration - AI Receptionist

## 🚀 Tích hợp Google Cloud Speech Services

Hệ thống AI Receptionist hiện đã hỗ trợ Google Cloud Speech-to-Text và Text-to-Speech để cải thiện độ chính xác và hiệu suất nhận dạng giọng nói.

## ⚡ Quick Start

### 1. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình Google Cloud

1. **Tạo Service Account** trên [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable APIs**: Speech-to-Text và Text-to-Speech
3. **Tải file JSON** credentials
4. **Cấu hình biến môi trường**:

```powershell
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account.json"
$env:GOOGLE_CLOUD_PROJECT_ID="your-project-id"
```

### 3. Cấu hình .env

```env
# Enable Google Cloud Voice Recognition
USE_GOOGLE_CLOUD_VOICE=true
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_REGION=asia-southeast1
```

### 4. Test Setup

```bash
# Test cấu hình
python test_google_cloud.py

# Demo đầy đủ
python demo_google_cloud.py
```

### 5. Chạy AI Receptionist

```bash
python main.py
```

## 🎯 Tính năng

### ✅ Đã tích hợp

- **Google Cloud Speech-to-Text**: Nhận dạng giọng nói real-time với độ chính xác cao
- **Google Cloud Text-to-Speech**: Tổng hợp giọng nói tiếng Việt tự nhiên
- **Streaming Recognition**: Xử lý audio real-time với latency thấp
- **Face-Voice Linking**: Tự động liên kết giọng nói với khuôn mặt đã nhận dạng
- **Auto Learning**: Học tự động các mẫu giọng nói mới

### 🔄 Fallback Support

- Hệ thống tự động chuyển về **Local Voice Recognition** nếu Google Cloud không khả dụng
- Cấu hình linh hoạt qua biến môi trường `USE_GOOGLE_CLOUD_VOICE`

## 📊 So sánh Performance

| Tính năng | Local Recognition | Google Cloud |
|-----------|-------------------|-------------|
| Độ chính xác | 70-80% | 90-95% |
| Latency | 200-500ms | 100-300ms |
| Hỗ trợ tiếng Việt | Cơ bản | Xuất sắc |
| Offline | ✅ | ❌ |
| Cost | Miễn phí | Free tier + Pay-per-use |

## 🛠️ Troubleshooting

### Lỗi thường gặp:

1. **PERMISSION_DENIED**
   - Kiểm tra file credentials JSON
   - Đảm bảo Service Account có đủ quyền

2. **API_NOT_ENABLED**
   - Enable Speech-to-Text và Text-to-Speech APIs

3. **QUOTA_EXCEEDED**
   - Kiểm tra usage trong Cloud Console
   - Cân nhắc upgrade billing plan

### Debug:

```bash
# Kiểm tra setup
python test_google_cloud.py

# Xem logs chi tiết
tail -f data/logs/system_*.log
```

## 💰 Cost Optimization

### Free Tier (hàng tháng):
- **Speech-to-Text**: 60 phút miễn phí
- **Text-to-Speech**: 1 triệu ký tự miễn phí

### Tips tiết kiệm:
- Sử dụng region `asia-southeast1` (gần VN)
- Tối ưu thời gian recording
- Monitor usage thường xuyên
- Sử dụng Standard models thay vì Premium

## 📚 Tài liệu chi tiết

- [GOOGLE_CLOUD_SETUP.md](./GOOGLE_CLOUD_SETUP.md) - Hướng dẫn setup chi tiết
- [Google Cloud Speech Documentation](https://cloud.google.com/speech-to-text/docs)
- [Google Cloud TTS Documentation](https://cloud.google.com/text-to-speech/docs)

## 🆘 Support

Nếu gặp vấn đề:
1. Kiểm tra [Google Cloud Status](https://status.cloud.google.com/)
2. Xem logs trong `data/logs/`
3. Chạy `python test_google_cloud.py` để debug
4. Tham khảo [GOOGLE_CLOUD_SETUP.md](./GOOGLE_CLOUD_SETUP.md)

---

**Lưu ý**: Google Cloud Speech services yêu cầu kết nối internet. Để sử dụng offline, hãy đặt `USE_GOOGLE_CLOUD_VOICE=false`.