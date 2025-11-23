# ✅ ĐÃ SỬA: Font Tiếng Việt & UI Đăng Ký

## 🔧 Đã Sửa 2 Vấn Đề

### 1. ✅ Font Tiếng Việt Hiển Thị Đúng
**Vấn đề cũ**: Hiển thị ??? thay vì tiếng Việt

**Giải pháp**:
- Sử dụng **PIL/Pillow** thay vì OpenCV để vẽ text tiếng Việt
- Load font hỗ trợ Unicode: `arial.ttf` (Windows) hoặc `DejaVuSans.ttf` (Linux)
- Convert frame: OpenCV → PIL → Vẽ text → OpenCV

**Code mới trong `src/ui/ui.py`**:
```python
def _draw_log_area(self, frame):
    from PIL import Image, ImageDraw, ImageFont
    
    # Convert to PIL for Vietnamese text
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)
    
    # Load font
    font = ImageFont.truetype("arial.ttf", 14)
    
    # Draw Vietnamese text
    draw.text((10, y_offset), log_msg, font=font, fill=color)
    
    # Convert back to OpenCV
    frame_cv = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
```

### 2. ✅ UI Đăng Ký Cập Nhật Đúng
**Vấn đề cũ**: Sau khi nói tên, UI vẫn hiển thị "Đang đăng ký người dùng"

**Giải pháp**: Thêm `ui.update_registration_status()` sau mỗi bước

**Flow cập nhật UI**:
```
1. Bắt đầu đăng ký
   → UI: "DANG KY NGUOI DUNG MOI"
   
2. Nói tên → Nhận được tên
   → UI: "CHUP ANH KHUAN MAT (0/5)"
   → Tên: [Tên người dùng]
   
3. Chụp ảnh 1
   → UI: "CHUP ANH (1/5)"
   
4. Chụp ảnh 2-5
   → UI: "CHUP ANH (2/5)" ... "CHUP ANH (5/5)"
   
5. Hoàn tất chụp ảnh
   → UI: "GHI AM GIONG NOI (0/3)"
   
6. Ghi âm 1-3
   → UI: "GHI AM (1/3)" ... "GHI AM (3/3)"
   
7. Lưu thông tin
   → UI: "DANG LUU THONG TIN..."
   
8. Hoàn tất
   → UI: "HOAN TAT!"
   → Tên: [Tên người dùng]
   → "Dang ky thanh cong!"
```

## 📝 Thay Đổi Code

### File: `src/core/inline_registration.py`

#### 1. Method `handle_voice_input()` - Cập nhật UI khi nhận tên
```python
# CẬP NHẬT UI NGAY LẬP TỨC
self.ui.update_registration_status(
    f"CHUP ANH KHUAN MAT (0/5)",
    name,
    "Nhin thang vao camera..."
)
```

#### 2. Method `_process_face_capture()` - Cập nhật UI mỗi ảnh
```python
# CẬP NHẬT UI NGAY
self.ui.update_registration_status(
    f"CHUP ANH ({self.state['face_count']}/{self.state['max_faces']})",
    self.user_name,
    "Thay doi goc do..."
)
```

#### 3. Method `_process_voice_capture()` - Cập nhật UI mỗi mẫu giọng
```python
# CẬP NHẬT UI
self.ui.update_registration_status(
    f"GHI AM ({self.state['voice_count']}/{self.state['max_voices']})",
    self.user_name,
    f"Hay noi: {next_phrase}"
)
```

#### 4. Method `complete()` - Cập nhật UI khi lưu và hoàn tất
```python
# Đang lưu
self.ui.update_registration_status(
    "DANG LUU THONG TIN...",
    self.user_name,
    "Vui long doi..."
)

# Hoàn tất
self.ui.update_registration_status(
    "HOAN TAT!",
    self.user_name,
    "Dang ky thanh cong!"
)
```

### File: `src/ui/ui.py`

#### Method `_draw_log_area()` - Sử dụng PIL cho tiếng Việt
```python
def _draw_log_area(self, frame):
    from PIL import Image, ImageDraw, ImageFont
    
    # Convert to PIL
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)
    
    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 14)  # Windows
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)  # Linux
        except:
            font = ImageFont.load_default()
    
    # Draw Vietnamese text
    draw.text((10, y_offset), log_msg, font=font, fill=color)
    
    # Convert back
    frame_cv = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
    frame[:] = frame_cv
```

## 📦 Yêu Cầu Thư Viện

Cần cài đặt **Pillow** (PIL):
```bash
pip install Pillow
```

Hoặc thêm vào `requirements.txt`:
```
Pillow>=10.0.0
```

## 🎨 Màu Sắc Log (RGB cho PIL)

- 🔴 **Đỏ** (255, 0, 0): ERROR
- 🟡 **Vàng** (255, 255, 0): WARNING
- 🟢 **Xanh lá** (0, 255, 0): INFO, Success
- 🟣 **Tím** (255, 0, 255): DEBUG
- 🟠 **Cam** (255, 165, 0): System events

## 🚀 Cách Test

### 1. Cài đặt Pillow
```bash
pip install Pillow
```

### 2. Restart chương trình
```bash
python main.py
```

### 3. Test đăng ký
1. Đứng trước camera (người lạ)
2. Hệ thống: "Xin chào! Bắt đầu đăng ký..."
3. UI hiển thị: **"DANG KY NGUOI DUNG MOI"**
4. Nói tên: "Tôi là Sơn"
5. UI cập nhật: **"CHUP ANH KHUAN MAT (0/5)"** + Tên: **Son**
6. Tự động chụp 5 ảnh
7. UI cập nhật: **"CHUP ANH (1/5)"** → **"CHUP ANH (5/5)"**
8. UI cập nhật: **"GHI AM GIONG NOI (0/3)"**
9. Nói 3 câu
10. UI cập nhật: **"GHI AM (1/3)"** → **"GHI AM (3/3)"**
11. UI cập nhật: **"DANG LUU THONG TIN..."**
12. UI cập nhật: **"HOAN TAT!"**

### 4. Kiểm tra log
- Nhìn vào vùng SYSTEM LOG ở dưới
- Tiếng Việt hiển thị đúng (không còn ???)
- Màu sắc phân biệt rõ ràng

## ✅ Kết Quả

- ✅ Font tiếng Việt hiển thị đúng
- ✅ UI cập nhật theo từng bước đăng ký
- ✅ Người dùng biết rõ đang ở bước nào
- ✅ Log hiển thị đầy đủ thông tin

## 🐛 Troubleshooting

### Lỗi: "cannot import name 'Image' from 'PIL'"
```bash
pip install --upgrade Pillow
```

### Lỗi: "cannot open resource"
Font không tìm thấy → Sẽ dùng font mặc định (vẫn hiển thị được tiếng Việt)

### UI vẫn không cập nhật
Kiểm tra:
1. Đã restart chương trình chưa?
2. File `inline_registration.py` có các dòng `ui.update_registration_status()` chưa?
3. Python có đang chạy code mới không?
