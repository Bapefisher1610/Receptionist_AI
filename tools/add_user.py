import os
import cv2
import uuid
import speech_recognition as sr
import time
from pathlib import Path

from ..src.core.config import FACES_DIR, VOICES_DIR
from ..src.modules.face_recognition.face_recognition_module import FaceRecognitionModule
from ..src.modules.voice_recognition.voice_recognition_module import VoiceRecognitionModule
from ..src.utils.logger import Logger
from ..src.utils.utils import resize_image, draw_text_with_background

def main():
    """Main function to add a new user"""
    print("=== Thêm người dùng mới ===\n")
    
    # Get user information
    name = input("Nhập tên người dùng: ")
    
    # Generate a unique ID for the user
    user_id = str(uuid.uuid4())[:8]
    
    # Create directories for user data
    user_face_dir = FACES_DIR / user_id
    os.makedirs(user_face_dir, exist_ok=True)
    
    # Save metadata
    with open(user_face_dir / 'metadata.txt', 'w', encoding='utf-8') as f:
        f.write(name)
    
    # Initialize modules
    logger = Logger()
    face_module = FaceRecognitionModule(logger)
    voice_module = VoiceRecognitionModule(logger)
    
    # Capture face images
    capture_face_images(user_id, name, face_module)
    
    # Record voice samples
    record_voice_samples(user_id, name, voice_module)
    
    print(f"\nNgười dùng {name} đã được thêm thành công với ID: {user_id}")

def capture_face_images(user_id, name, face_module):
    """Capture face images for a new user"""
    print("\n=== Chụp ảnh khuôn mặt ===")
    print("Hệ thống sẽ chụp 5 ảnh khuôn mặt của bạn từ các góc độ khác nhau.")
    print("Nhấn SPACE để chụp ảnh, ESC để hủy.")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở camera!")
        return
    
    # Create directory for user's face images
    user_dir = FACES_DIR / user_id
    os.makedirs(user_dir, exist_ok=True)
    
    # Capture 5 images
    image_count = 0
    max_images = 5
    
    while image_count < max_images:
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc khung hình từ camera!")
            break
        
        # Resize frame for display
        display_frame = resize_image(frame, width=800)
        
        # Draw instructions
        text = f"Ảnh {image_count+1}/{max_images} - Nhấn SPACE để chụp, ESC để hủy"
        draw_text_with_background(display_frame, text, (10, 30))
        
        # Show frame
        cv2.imshow("Chụp ảnh khuôn mặt", display_frame)
        
        # Wait for key press
        key = cv2.waitKey(1)
        
        if key == 27:  # ESC key
            print("Đã hủy chụp ảnh!")
            break
        
        if key == 32:  # SPACE key
            # Save image
            timestamp = int(time.time())
            image_path = user_dir / f"{timestamp}.jpg"
            cv2.imwrite(str(image_path), frame)
            
            # Convert BGR to RGB for face recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Add face to recognition module
            if face_module.add_face(rgb_frame, user_id, name):
                print(f"Đã chụp ảnh {image_count+1}/{max_images}")
                image_count += 1
            else:
                print("Không tìm thấy khuôn mặt trong ảnh. Vui lòng thử lại.")
            
            # Small delay to prevent multiple captures
            time.sleep(1)
    
    # Release camera and close windows
    cap.release()
    cv2.destroyAllWindows()

def record_voice_samples(user_id, name, voice_module):
    """Record voice samples for a new user"""
    print("\n=== Ghi âm giọng nói ===")
    print("Hãy đọc các câu sau đây để hệ thống ghi nhận giọng nói của bạn.")
    
    # Phrases to record
    phrases = [
        "Xin chào, tôi là " + name,
        "Tôi muốn đăng ký một cuộc hẹn",
        "Cảm ơn bạn rất nhiều"
    ]
    
    # Initialize recognizer and microphone
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    # Adjust for ambient noise
    print("\nĐang điều chỉnh cho tiếng ồn xung quanh...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
    
    # Record each phrase
    keywords = []
    
    for i, phrase in enumerate(phrases):
        print(f"\nPhrase {i+1}/{len(phrases)}: {phrase}")
        print("Nhấn Enter khi bạn sẵn sàng nói...")
        input()
        
        print("Đang ghi âm... Hãy nói ngay bây giờ!")
        
        try:
            with microphone as source:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("Đang xử lý...")
            
            try:
                text = recognizer.recognize_google(audio, language="vi-VN")
                print(f"Đã nhận dạng: {text}")
                
                # Extract keywords from recognized text
                words = text.split()
                keywords.extend([word for word in words if len(word) > 3])
                
            except sr.UnknownValueError:
                print("Không thể nhận dạng giọng nói!")
            except sr.RequestError as e:
                print(f"Lỗi khi yêu cầu kết quả từ Google Speech Recognition: {e}")
        
        except Exception as e:
            print(f"Lỗi khi ghi âm: {e}")
    
    # Remove duplicates and save keywords
    keywords = list(set(keywords))
    
    if keywords:
        # Add voice pattern
        if voice_module.add_voice_pattern(user_id, name, keywords):
            print(f"\nĐã ghi nhận {len(keywords)} từ khóa giọng nói: {', '.join(keywords)}")
        else:
            print("Không thể lưu mẫu giọng nói!")
    else:
        print("Không có từ khóa nào được trích xuất từ giọng nói!")

if __name__ == "__main__":
    main()