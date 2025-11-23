# ✅ ĐÃ SỬA: System Log Bán Trong Suốt & Logic Đăng Ký

## 🔧 Đã Sửa

### 1. ✅ System Log Bán Trong Suốt
**Vấn đề**: Log che khuất hình ảnh camera

**Giải pháp**: Sử dụng `cv2.addWeighted()` để tạo overlay bán trong suốt

**Code mới trong `src/ui/ui.py`**:
```python
# Draw semi-transparent black background
overlay = frame.copy()
cv2.rectangle(overlay, (0, log_y_start), (width, height), (0, 0, 0), -1)
# Alpha blend: 0.7 = 70% transparent
cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
```

**Kết quả**: Vùng log màu đen 70% trong suốt, vẫn thấy được hình ảnh phía sau

### 2. ✅ Logic Đăng Ký Hoạt Động Đúng

#### Vấn đề Phát Hiện:
1. **Voice command không được xử lý đúng** - Dùng `speak_response` thay vì `speak_immediate`
2. **Trích xuất tên không đủ pattern** - Thiếu pattern không dấu
3. **Không có debug log** - Khó biết tại sao không nhận tên

#### Giải Pháp:

##### A. Sửa Voice Command Handler
**File**: `src/core/main_streaming.py`

```python
# Kiểm tra nếu đang đăng ký
if self.registration.is_active:
    response = self.registration.handle_voice_input(audio_text)
    if response:
        # Sử dụng speak_immediate để phản hồi ngay
        self.ai_chatbot.tts.speak_immediate(response)
        log_msg = f"Phan hoi dang ky: {response}"
        self.system_logger.info(log_msg)
        self.ui.add_log_message(log_msg)
        return audio_text, response
```

**Thay đổi**:
- ❌ Cũ: `speak_response(response, priority="high")` - Chậm, có thể bị queue
- ✅ Mới: `tts.speak_immediate(response)` - Nói ngay lập tức

##### B. Cải Thiện Trích Xuất Tên
**File**: `src/core/inline_registration.py`

**Thêm patterns không dấu**:
```python
patterns = [
    # Có dấu
    'tên tôi là', 'tôi là', 'tôi tên', 'mình là', 'mình tên',
    'tên là', 'tên mình là', 'em là', 'anh là', 'chị là',
    # Không dấu (cho Google Speech Recognition)
    'ten toi la', 'toi la', 'toi ten', 'minh la', 'minh ten',
    'ten la', 'ten minh la', 'em la', 'anh la', 'chi la'
]
```

**Thêm debug logs**:
```python
self.logger.info(f"[DEBUG] _extract_name input: '{text}'")
self.logger.info(f"[DEBUG] Found pattern '{pattern}', name_part: '{name_part}'")
self.logger.info(f"[DEBUG] Extracted name: '{result}'")
```

##### C. Cải Thiện Hướng Dẫn
**Thay đổi câu hướng dẫn**:
```python
# Cũ
"Vui long noi ten cua ban"

# Mới
"Vui long noi ten cua ban. Vi du: Toi la Son"
```

## 🎯 Flow Đăng Ký Mới

```
1. Phát hiện người lạ
   → "Xin chao! Bat dau dang ky..."
   → UI: "DANG KY NGUOI DUNG MOI"
   
2. Hướng dẫn
   → "Vui long noi ten cua ban. Vi du: Toi la Son"
   
3. Người dùng nói: "Tôi là Sơn" hoặc "Toi la Son"
   → [DEBUG] _extract_name input: 'toi la son'
   → [DEBUG] Found pattern 'toi la', name_part: 'son'
   → [DEBUG] Extracted name: 'Son'
   → "Da nhan ten: Son"
   → UI: "CHUP ANH KHUAN MAT (0/5)" + Tên: Son
   → "Xin chao Son! Bay gio toi se chup anh..."
   
4. Tự động chụp 5 ảnh
   → UI: "CHUP ANH (1/5)" ... "CHUP ANH (5/5)"
   
5. Tự động ghi 3 mẫu giọng
   → UI: "GHI AM (1/3)" ... "GHI AM (3/3)"
   
6. Lưu và hoàn tất
   → UI: "DANG LUU THONG TIN..."
   → UI: "HOAN TAT!"
```

## 🐛 Debug

### Kiểm Tra Log
Khi người dùng nói tên, xem log:

```
[DEBUG] handle_voice_input: step=get_name, text='toi la son'
[DEBUG] _extract_name input: 'toi la son'
[DEBUG] Found pattern 'toi la', name_part: 'son'
[DEBUG] Extracted name from pattern: 'Son'
Da nhan ten: Son
Phan hoi dang ky: Xin chao Son! Bay gio toi se chup anh khuan mat cua ban.
```

### Nếu Không Nhận Tên
Kiểm tra:
1. **Log có hiển thị `[DEBUG] _extract_name input`?**
   - Không → Voice command không được gọi
   - Có → Xem text nhận được là gì

2. **Text nhận được đúng không?**
   - Ví dụ: `'toi la son'` ✅
   - Ví dụ: `'xin chào'` ❌ (không có tên)

3. **Pattern có match không?**
   - Có `[DEBUG] Found pattern` → Đang trích xuất
   - Không có → Thử nói rõ hơn: "Tôi là [Tên]"

## 📝 Patterns Hỗ Trợ

### Có Dấu (Nếu mic tốt):
- "Tên tôi là Sơn"
- "Tôi là Sơn"
- "Mình là Sơn"
- "Em là Sơn"

### Không Dấu (Google Speech Recognition thường trả về):
- "Ten toi la Son"
- "Toi la Son"
- "Minh la Son"
- "Em la Son"

### Đơn Giản (Fallback):
- "Sơn" (chỉ nói tên)
- "Son" (không dấu)

## 🚀 Cách Test

### 1. Restart chương trình
```bash
python main.py
```

### 2. Test đăng ký
1. Đứng trước camera (người lạ)
2. Nghe: "Vui long noi ten cua ban. Vi du: Toi la Son"
3. **Nói rõ ràng**: "Tôi là Sơn" hoặc "Toi la Son"
4. Xem log console:
   - Có `[DEBUG] _extract_name input` → Đang xử lý
   - Có `Da nhan ten: Son` → Thành công
   - UI chuyển sang "CHUP ANH KHUAN MAT (0/5)"

### 3. Kiểm tra System Log
- Vùng log ở dưới bây giờ **bán trong suốt**
- Vẫn thấy được hình ảnh camera phía sau
- Text tiếng Việt hiển thị đúng (nhờ PIL)

## ✅ Kết Quả

- ✅ System log bán trong suốt (70% transparent)
- ✅ Voice command xử lý ngay với `speak_immediate`
- ✅ Trích xuất tên hỗ trợ cả có dấu và không dấu
- ✅ Debug logs giúp troubleshoot
- ✅ Hướng dẫn rõ ràng hơn với ví dụ

## 🎨 Độ Trong Suốt

Có thể điều chỉnh trong `src/ui/ui.py`:

```python
# 0.7 = 70% transparent (mặc định)
cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

# Muốn trong suốt hơn (80%):
cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

# Muốn đậm hơn (60%):
cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
```

## 💡 Tips

### Để Đăng Ký Thành Công:
1. **Nói rõ ràng**: "Tôi là [Tên]"
2. **Nói chậm**: Để Google Speech Recognition nhận đúng
3. **Nói gần mic**: Đảm bảo âm thanh rõ
4. **Xem log**: Kiểm tra text nhận được

### Nếu Vẫn Không Nhận:
1. Thử nói: "Toi la [Ten]" (không dấu)
2. Thử nói chỉ tên: "[Ten]"
3. Kiểm tra mic hoạt động
4. Xem console log để debug
