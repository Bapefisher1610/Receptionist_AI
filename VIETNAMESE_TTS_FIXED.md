# ✅ ĐÃ SỬA: TTS Tiếng Việt Có Dấu

## 🎯 Vấn Đề

**Trước**: Tất cả câu TTS không dấu → Phát âm không chuẩn
```python
"Xin chao! Bay gio toi se chup anh khuan mat cua ban."
```

**Sau**: TTS có dấu, UI không dấu → Phát âm chuẩn, hiển thị ổn
```python
# TTS (có dấu)
"Xin chào! Bây giờ tôi sẽ chụp ảnh khuôn mặt của bạn."

# UI (không dấu - vì font)
"CHUP ANH KHUAN MAT (0/5)"
```

## 🔧 Chiến Lược

### Nguyên Tắc:
1. **TTS (Text-to-Speech)**: Luôn có dấu → Phát âm chuẩn
2. **UI (Hiển thị)**: Không dấu → Tránh lỗi font
3. **Log**: Không dấu → Tránh lỗi font

## 📝 Các Câu Đã Sửa

### 1. Bắt Đầu Đăng Ký
```python
# TTS
"Xin chào! Tôi phát hiện bạn là người mới. Bắt đầu đăng ký..."
"Vui lòng nói tên của bạn. Ví dụ: Tôi là Sơn"

# UI
"DANG KY NGUOI DUNG MOI"
"Vui long noi ten cua ban..."
```

### 2. Nhận Tên
```python
# TTS
"Xin chào {name}! Bây giờ tôi sẽ chụp ảnh khuôn mặt của bạn."

# UI
"CHUP ANH KHUAN MAT (0/5)"
"Nhin thang vao camera..."
```

### 3. Chụp Ảnh Xong → Ghi Âm
```python
# TTS
"Tuyệt vời! Bây giờ hãy nói: Xin chào, tôi là {name}"

# UI
"GHI AM GIONG NOI (0/3)"
"Hay noi: 'Xin chao, toi la {name}'"
```

### 4. Ghi Âm Từng Mẫu
```python
# TTS (có dấu)
phrases_tts = [
    "Xin chào, tôi là {name}",
    "Tôi muốn đăng ký một cuộc hẹn",
    "Cảm ơn bạn rất nhiều"
]
"Tốt! Bây giờ hãy nói: {next_phrase_tts}"

# UI (không dấu)
phrases_ui = [
    "Xin chao, toi la {name}",
    "Toi muon dang ky mot cuoc hen",
    "Cam on ban rat nhieu"
]
"Hay noi: {next_phrase_ui}"
```

### 5. Đang Lưu
```python
# TTS
"Đang lưu thông tin của bạn..."

# UI
"DANG LUU THONG TIN..."
"Vui long doi..."
```

### 6. Hoàn Tất
```python
# TTS
"Hoàn tất! Đăng ký thành công cho {name}!"

# UI
"HOAN TAT!"
"Dang ky thanh cong!"
```

### 7. Không Hiểu Tên
```python
# TTS
"Xin lỗi, tôi không hiểu tên của bạn. Vui lòng nói rõ hơn."

# UI
"KHONG HIEU TEN"
"Vui long noi ro hon..."
```

## 🎤 Flow TTS Hoàn Chỉnh

```
1. Phát hiện người lạ
   🔊 "Xin chào! Tôi phát hiện bạn là người mới. Bắt đầu đăng ký..."
   🔊 "Vui lòng nói tên của bạn. Ví dụ: Tôi là Sơn"
   📺 UI: "DANG KY NGUOI DUNG MOI"

2. Người dùng nói: "Tôi là Sơn"
   🔊 "Xin chào Sơn! Bây giờ tôi sẽ chụp ảnh khuôn mặt của bạn."
   📺 UI: "CHUP ANH KHUAN MAT (0/5)" + Tên: Son

3. Chụp 5 ảnh tự động
   📺 UI: "CHUP ANH (1/5)" ... "CHUP ANH (5/5)"

4. Hoàn tất chụp ảnh
   🔊 "Tuyệt vời! Bây giờ hãy nói: Xin chào, tôi là Sơn"
   📺 UI: "GHI AM GIONG NOI (0/3)"

5. Ghi âm mẫu 1
   🔊 "Tốt! Bây giờ hãy nói: Tôi muốn đăng ký một cuộc hẹn"
   📺 UI: "GHI AM (1/3)"

6. Ghi âm mẫu 2
   🔊 "Tốt! Bây giờ hãy nói: Cảm ơn bạn rất nhiều"
   📺 UI: "GHI AM (2/3)"

7. Ghi âm mẫu 3 xong
   🔊 "Đang lưu thông tin của bạn..."
   📺 UI: "DANG LUU THONG TIN..."

8. Hoàn tất
   🔊 "Hoàn tất! Đăng ký thành công cho Sơn!"
   📺 UI: "HOAN TAT!"
```

## 💻 Code Implementation

### File: `src/core/inline_registration.py`

#### Pattern: TTS riêng, UI riêng

```python
# Cập nhật UI (không dấu)
self.ui.update_registration_status(
    "GHI AM GIONG NOI (0/3)",
    self.user_name,
    f"Hay noi: 'Xin chao, toi la {self.user_name}'"
)

# Thông báo bằng giọng nói (có dấu)
from ..modules.tts.streaming_tts_module import StreamingTTSModule
tts = StreamingTTSModule()
tts.speak_immediate(f"Tuyệt vời! Bây giờ hãy nói: Xin chào, tôi là {self.user_name}")
```

#### Phrases Array: 2 versions

```python
# Phrases cho UI (không dấu)
phrases_ui = [
    f"Xin chao, toi la {self.user_name}",
    "Toi muon dang ky mot cuoc hen",
    "Cam on ban rat nhieu"
]

# Phrases cho TTS (có dấu)
phrases_tts = [
    f"Xin chào, tôi là {self.user_name}",
    "Tôi muốn đăng ký một cuộc hẹn",
    "Cảm ơn bạn rất nhiều"
]

# Sử dụng
self.ui.update_registration_status(..., next_phrase_ui)
tts.speak_immediate(f"Tốt! Bây giờ hãy nói: {next_phrase_tts}")
```

## ✅ Kết Quả

### Trước:
- 🔊 TTS: "Xin chao Son! Bay gio toi se chup anh..." ❌ Phát âm sai
- 📺 UI: "CHUP ANH KHUAN MAT" ✅ Hiển thị OK

### Sau:
- 🔊 TTS: "Xin chào Sơn! Bây giờ tôi sẽ chụp ảnh..." ✅ Phát âm chuẩn
- 📺 UI: "CHUP ANH KHUAN MAT" ✅ Hiển thị OK

## 🚀 Test

### 1. Restart
```bash
python main.py
```

### 2. Đăng ký người mới
1. Đứng trước camera (người lạ)
2. Nghe: **"Xin chào! Tôi phát hiện bạn là người mới..."** (có dấu, chuẩn)
3. Nghe: **"Vui lòng nói tên của bạn. Ví dụ: Tôi là Sơn"** (có dấu, chuẩn)
4. Nói: "Tôi là Sơn"
5. Nghe: **"Xin chào Sơn! Bây giờ tôi sẽ chụp ảnh..."** (có dấu, chuẩn)
6. Chụp 5 ảnh
7. Nghe: **"Tuyệt vời! Bây giờ hãy nói: Xin chào, tôi là Sơn"** (có dấu, chuẩn)
8. Ghi 3 mẫu giọng
9. Nghe: **"Đang lưu thông tin của bạn..."** (có dấu, chuẩn)
10. Nghe: **"Hoàn tất! Đăng ký thành công cho Sơn!"** (có dấu, chuẩn)

### 3. Kiểm tra
- ✅ TTS phát âm chuẩn tiếng Việt
- ✅ UI hiển thị không bị lỗi font
- ✅ Log không bị lỗi font

## 📊 So Sánh

| Phần | Trước | Sau |
|------|-------|-----|
| **TTS** | Không dấu ❌ | Có dấu ✅ |
| **UI** | Không dấu ✅ | Không dấu ✅ |
| **Log** | Không dấu ✅ | Không dấu ✅ |
| **Phát âm** | Sai ❌ | Chuẩn ✅ |
| **Hiển thị** | OK ✅ | OK ✅ |

## 💡 Lưu Ý

### Tại sao UI không dấu?
- OpenCV `cv2.putText()` không hỗ trợ Unicode tốt
- Dùng PIL/Pillow cho tiếng Việt nhưng chậm hơn
- Giải pháp: UI không dấu, TTS có dấu

### Tại sao TTS có dấu?
- Google TTS cần dấu để phát âm chuẩn
- "Xin chao" → phát âm sai
- "Xin chào" → phát âm đúng

### Best Practice:
```python
# ✅ ĐÚNG
ui.update_registration_status("CHUP ANH (0/5)", ...)  # Không dấu
tts.speak_immediate("Chụp ảnh khuôn mặt của bạn")     # Có dấu

# ❌ SAI
ui.update_registration_status("CHỤP ẢNH (0/5)", ...)  # Có dấu → Lỗi font
tts.speak_immediate("Chup anh khuan mat cua ban")     # Không dấu → Phát âm sai
```

## 🎉 Hoàn Tất

Bây giờ hệ thống:
- ✅ Phát âm tiếng Việt chuẩn
- ✅ Hiển thị UI không lỗi
- ✅ Trải nghiệm người dùng tốt hơn
- ✅ Dễ hiểu, dễ theo dõi
