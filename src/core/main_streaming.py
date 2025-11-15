#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import time
import threading
from pathlib import Path

# Import modules
from .config import *
from ..utils.logger import setup_logger, Logger
from ..modules.face_recognition.face_recognition_module import FaceRecognitionModule
from ..services.google_voice_recognition import GoogleVoiceRecognitionModule
from ..modules.tts.streaming_tts_module import StreamingTTSModule
from ..modules.ai_chatbot.ai_chatbot_integration import AIReceptionistChatbot  # AI Chatbot
from ..modules.auto_registration.auto_registration_module import AutoRegistrationModule
from ..ui.ui import UI as ReceptionistUI
from ..utils.utils import load_face_encodings, load_voice_patterns

class StreamingAIReceptionist:
    """AI Receptionist với Streaming TTS và AI Chatbot"""
    
    def __init__(self):
        # Setup logging
        self.system_logger = setup_logger()
        self.logger = Logger()  # Logger class for recognition logging
        self.system_logger.info("Khoi dong Streaming AI Receptionist...")
        
        # Initialize modules
        self.face_module = FaceRecognitionModule(self.logger)
        self.voice_module = GoogleVoiceRecognitionModule(self.logger)
        
        # Sử dụng AI Chatbot với Streaming TTS
        self.ai_chatbot = AIReceptionistChatbot(tts_engine="auto")
        self.auto_registration = AutoRegistrationModule(self.face_module, self.voice_module, self.system_logger)
        
        # UI
        self.ui = ReceptionistUI()
        
        # Load data
        self.face_encodings = load_face_encodings()
        self.voice_patterns = load_voice_patterns()
        
        # State
        self.running = False
        self.current_user = None
        self.last_interaction = time.time()
        self.unknown_person_asked = False  # Theo dõi đã hỏi người lạ chưa
        self.last_unknown_time = 0  # Thời gian lần cuối phát hiện người lạ
        
        # Camera
        self.camera = None
        
        self.system_logger.info("Streaming AI Receptionist initialized")
    
    def start_camera(self):
        """Khởi động camera"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.system_logger.error("Khong the mo camera")
                return False
            
            # Cấu hình camera
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 60)
            
            self.system_logger.info("📹 Camera đã sẵn sàng")
            return True
            
        except Exception as e:
            self.system_logger.error(f"Loi khoi dong camera: {e}")
            return False

    
    def process_face_recognition(self, frame):
        """Xử lý nhận diện khuôn mặt"""
        try:
            # Detect faces
            faces = self.face_module.detect_faces(frame)
            
            if not faces:
                return []
            
            # Tìm khuôn mặt được nhận diện có confidence cao nhất (chỉ xét những khuôn mặt known)
            known_faces = [face for face in faces if face.get('person_id', 'unknown') != 'unknown']
            
            if known_faces:
                # Có khuôn mặt được nhận diện - chọn khuôn mặt có confidence cao nhất
                best_known_face = max(known_faces, key=lambda x: x.get('confidence', 0.0))
                person_id = best_known_face.get('person_id', 'unknown')
                person_name = best_known_face.get('name', 'Unknown')
                confidence = best_known_face.get('confidence', 0.0)
                
                # Chỉ chào khi confidence đủ cao
                if confidence >= 0.6:
                    # Reset trạng thái người lạ khi có người quen
                    self.unknown_person_asked = False
                    
                    # Reset current_user nếu đã quá 30 giây
                    if hasattr(self, 'last_interaction') and time.time() - self.last_interaction > 30:
                        self.current_user = None
                    
                    # Chào hỏi bằng AI Chatbot
                    if person_id != self.current_user:
                        greeting = f"Chào {person_name}! Rất vui được gặp bạn. Bạn cần hỗ trợ gì không?"
                        self.ai_chatbot.speak_direct(greeting)
                        
                        self.current_user = person_id
                        self.last_interaction = time.time()
                        
                        self.system_logger.info(f"👤 Chào hỏi: {person_name} (confidence: {confidence:.2f})")
                    return faces
            
            # Không có khuôn mặt nào được nhận diện hoặc confidence thấp - hỏi thông tin
            current_time = time.time()
            # Chỉ hỏi nếu chưa hỏi hoặc đã quá 60 giây kể từ lần hỏi cuối
            if not self.unknown_person_asked or (current_time - self.last_unknown_time) > 60:
                # Start auto registration process
                if not self.auto_registration.is_registering():
                    self.auto_registration.start_registration(frame)
                    self.ui.show_registration_ui("Đang đăng ký người dùng mới...")
                    unknown_greeting = "Xin chào! Tôi không nhận ra bạn. Tên bạn là gì? Bạn đến đây để làm gì?"
                    self.ai_chatbot.speak_direct(unknown_greeting)
                
                self.unknown_person_asked = True
                self.last_unknown_time = current_time
                self.current_user = None  # Reset current user
                
                self.system_logger.info("❓ Hỏi thông tin người lạ")
            
            # Update UI with all face info
            self.ui.update_recognition_results(faces)
            
            return faces
            
        except Exception as e:
            self.system_logger.error(f"Loi xu ly face recognition: {e}")
            return []
    
    def process_voice_command(self):
        """Xử lý lệnh giọng nói"""
        try:
            print("[VOICE] Attempting to listen for voice command...")
            # Lắng nghe giọng nói
            audio_text = self.voice_module.listen_for_command()

            if audio_text:
                self.system_logger.info(f"[VOICE] SUCCESS - Nghe duoc: '{audio_text}'")

                # Kiểm tra nếu đang trong chế độ đăng ký
                if self.auto_registration.is_registering():
                    print("[VOICE] Processing registration input...")
                    # Xử lý input đăng ký
                    registration_result = self.auto_registration.process_voice_input(audio_text)

                    if registration_result:
                         if registration_result['status'] == 'completed':
                             # Đăng ký hoàn tất thành công
                             person_name = registration_result['person_name']
                             self.ui.update_registration_status("Đăng ký thành công!", person_name, "Đã lưu thông tin")
                             response = f"Cảm ơn {person_name}! Tôi đã ghi nhận thông tin của bạn. Chào mừng bạn!"
                             self.ai_chatbot.speak_response(response, priority="high")
                             # Hide registration UI after a delay
                             import threading
                             threading.Timer(3.0, self.ui.hide_registration_ui).start()
                             # Reset trạng thái người lạ
                             self.unknown_person_asked = False
                         elif registration_result['status'] == 'need_more_info':
                             # Cần thêm thông tin
                             self.ui.update_registration_status("Cần thêm thông tin", "", "Vui lòng nói rõ tên của bạn")
                             response = "Xin lỗi, tôi cần thêm thông tin. Bạn có thể nói rõ tên của bạn không?"
                             self.ai_chatbot.speak_response(response, priority="high")
                         elif registration_result['status'] == 'timeout':
                             # Hết thời gian đăng ký
                             self.ui.update_registration_status("Hết thời gian", "", "Đăng ký không thành công")
                             response = "Thời gian đăng ký đã hết. Nếu bạn muốn đăng ký, xin hãy thử lại."
                             self.ai_chatbot.speak_response(response, priority="high")
                             # Hide registration UI
                             import threading
                             threading.Timer(2.0, self.ui.hide_registration_ui).start()
                             self.unknown_person_asked = False
                         elif registration_result['status'] == 'processing':
                             # Đang xử lý
                             if 'person_name' in registration_result:
                                 self.ui.update_registration_status("Đang xử lý...",
                                                                   registration_result['person_name'],
                                                                   "Đang lưu thông tin")
                else:
                    print(f"[VOICE] Processing general input: '{audio_text}'")
                    # Xử lý giọng nói bình thường
                    response = self.ai_chatbot.speak_response(audio_text, priority="high")
                    print(f"[VOICE] Chatbot response: '{response}'")

                    # Log phản hồi
                    self.system_logger.info(f"[VOICE] Phan hoi: {response}")

                self.last_interaction = time.time()
                return audio_text, response
            else:
                print("[VOICE] No speech detected")

        except Exception as e:
            self.system_logger.error(f"[VOICE] Loi xu ly voice command: {e}")
            print(f"[VOICE] Error: {e}")

        return None, None
    
    def handle_text_input(self, text_input):
        """Xử lý input text từ UI"""
        if text_input.strip():
            self.system_logger.info(f"💬 Text input: {text_input}")
            
            # Kiểm tra nếu đang trong chế độ đăng ký
            if self.auto_registration.is_registering():
                # Xử lý input đăng ký
                registration_result = self.auto_registration.process_voice_input(text_input)
                
                if registration_result:
                     if registration_result['status'] == 'completed':
                         # Đăng ký hoàn tất thành công
                         person_name = registration_result['person_name']
                         self.ui.update_registration_status("Đăng ký thành công!", person_name, "Đã lưu thông tin")
                         response = f"Cảm ơn {person_name}! Tôi đã ghi nhận thông tin của bạn. Chào mừng bạn!"
                         self.ai_chatbot.speak_response(response, priority="high")
                         # Hide registration UI after a delay
                         import threading
                         threading.Timer(3.0, self.ui.hide_registration_ui).start()
                         # Reset trạng thái người lạ
                         self.unknown_person_asked = False
                     elif registration_result['status'] == 'need_more_info':
                         # Cần thêm thông tin
                         self.ui.update_registration_status("Cần thêm thông tin", "", "Vui lòng nói rõ tên của bạn")
                         response = "Xin lỗi, tôi cần thêm thông tin. Bạn có thể nói rõ tên của bạn không?"
                         self.ai_chatbot.speak_response(response, priority="high")
                     elif registration_result['status'] == 'timeout':
                         # Hết thời gian đăng ký
                         self.ui.update_registration_status("Hết thời gian", "", "Đăng ký không thành công")
                         response = "Thời gian đăng ký đã hết. Nếu bạn muốn đăng ký, xin hãy thử lại."
                         self.ai_chatbot.speak_response(response, priority="high")
                         # Hide registration UI
                         import threading
                         threading.Timer(2.0, self.ui.hide_registration_ui).start()
                         self.unknown_person_asked = False
                     elif registration_result['status'] == 'processing':
                         # Đang xử lý
                         if 'person_name' in registration_result:
                             self.ui.update_registration_status("Đang xử lý...", 
                                                               registration_result['person_name'], 
                                                               "Đang lưu thông tin")
            else:
                # Xử lý text bình thường
                response = self.ai_chatbot.speak_response(text_input, priority="normal")
            
            self.system_logger.info(f"Phan hoi: {response}")
            self.last_interaction = time.time()
            
            return response
        return None
    
    def check_idle_timeout(self):
        """Kiểm tra timeout không hoạt động"""
        if time.time() - self.last_interaction > 300:  # 5 phút
            if self.current_user:
                idle_msg = "Tôi vẫn ở đây nếu bạn cần hỗ trợ gì thêm."
                self.ai_chatbot.tts.speak_async(idle_msg)
                self.last_interaction = time.time()
    
    def run(self):
        """Chạy hệ thống chính"""
        self.system_logger.info("Bat dau chay Streaming AI Receptionist")
        
        # Khởi động camera
        if not self.start_camera():
            self.system_logger.error("Khong the khoi dong camera")
            return
        
        # Chào mừng
        welcome_msg = "Xin chào! Hệ thống AI Receptionist với Streaming TTS đã sẵn sàng."
        self.ai_chatbot.tts.speak_async(welcome_msg)
        
        self.running = True
        
        # Voice recognition thread
        voice_thread = threading.Thread(target=self._voice_worker, daemon=True)
        voice_thread.start()
        
        try:
            while self.running:
                # Đọc frame từ camera
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Xử lý face recognition
                faces = self.process_face_recognition(frame)
                
                # Kiểm tra idle timeout
                self.check_idle_timeout()
                
                # Hiển thị UI
                self.ui.update_frame(frame)
                
                # Xử lý input từ UI
                text_input = self.ui.get_text_input()
                if text_input:
                    self.handle_text_input(text_input)
                
                # Hiển thị frame
                cv2.imshow('Streaming AI Receptionist', frame)
                
                # Kiểm tra phím thoát
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' hoặc ESC
                    break
                elif key == ord('s'):  # 's' để dừng giọng nói
                    self.ai_chatbot.tts.stop_current_speech()
                elif key == ord('h'):  # 'h' để help
                    help_msg = "Phím tắt: Q=Thoát, S=Dừng giọng nói, H=Trợ giúp"
                    self.ai_chatbot.tts.speak_immediate(help_msg)
        
        except KeyboardInterrupt:
            self.system_logger.info("⚠️ Nhận tín hiệu dừng từ người dùng")
        
        except Exception as e:
            self.system_logger.error(f"Loi trong main loop: {e}")
        
        finally:
            self.cleanup()
    
    def _voice_worker(self):
        """Worker thread cho voice recognition"""
        while self.running:
            try:
                # Only process voice command if not in registration mode
                if not self.auto_registration.is_registering():
                    self.process_voice_command()
                time.sleep(2)  # Wait 2 seconds between listening attempts
            except Exception as e:
                self.system_logger.error(f"Loi voice worker: {e}")
                time.sleep(1)
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        self.system_logger.info("Dang don dep tai nguyen...")
        
        self.running = False
        
        # Tạm biệt
        goodbye_msg = "Tạm biệt! Cảm ơn bạn đã sử dụng AI Receptionist."
        self.ai_chatbot.tts.speak_immediate(goodbye_msg)
        
        # Đợi phát xong
        while self.ai_chatbot.is_busy():
            time.sleep(0.1)
        
        # Cleanup
        if self.camera:
            self.camera.release()
        
        cv2.destroyAllWindows()
        
        # Stop AI chatbot
        self.ai_chatbot.stop()
        
        self.system_logger.info("Don dep hoan tat")

def main():
    """Hàm main"""
    try:
        receptionist = StreamingAIReceptionist()
        receptionist.run()
    except Exception as e:
        print(f"Loi khoi dong: {e}")

if __name__ == "__main__":
    main()