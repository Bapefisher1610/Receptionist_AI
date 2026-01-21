#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import time
import threading
import subprocess
import sys
import uuid
import os
from pathlib import Path

# Import modules
from .config import *
from ..utils.logger import setup_logger, Logger
from ..modules.face_recognition.face_recognition_module import FaceRecognitionModule
from ..modules.voice_recognition.voice_recognition_module import VoiceRecognitionModule
from ..modules.tts.streaming_tts_module import StreamingTTSModule
from ..modules.ai_chatbot.ai_chatbot_integration import AIReceptionistChatbot  # AI Chatbot
from ..ui.ui import UI as ReceptionistUI
from ..utils.utils import load_face_encodings, load_voice_patterns, resize_image, draw_text_with_background
from .inline_registration import InlineRegistration

class StreamingAIReceptionist:
    """AI Receptionist với Streaming TTS và AI Chatbot"""
    
    def __init__(self):
        # Setup logging
        self.system_logger = setup_logger()
        self.logger = Logger()  # Logger class for recognition logging
        self.system_logger.info("Khoi dong Streaming AI Receptionist...")
        
        # Initialize modules
        self.face_module = FaceRecognitionModule(self.logger)
        self.voice_module = VoiceRecognitionModule(self.logger)
        
        # Sử dụng AI Chatbot với Streaming TTS
        self.ai_chatbot = AIReceptionistChatbot(tts_engine="auto")
        
        # UI
        self.ui = ReceptionistUI()
        
        # Inline Registration Module
        self.registration = InlineRegistration(self.face_module, self.voice_module, self.system_logger, self.ui)
        
        # Load data
        self.face_encodings = load_face_encodings()
        self.voice_patterns = load_voice_patterns()
        
        # State
        self.running = False
        self.current_user = None
        self.last_interaction = time.time()
        self.unknown_person_notified = False  # Theo dõi đã thông báo người lạ chưa
        self.last_unknown_time = 0  # Thời gian lần cuối phát hiện người lạ
        self.greeted_people = set()  # Track people greeted in current session
        self.session_start_time = time.time()  # Track session start
        self.unknown_notification_cooldown = 30  # Thông báo lại sau 30 giây
        
        # Lưu trữ khuôn mặt hiện tại để so sánh
        self.current_face_encoding = None  # Face encoding của người hiện tại
        self.current_person_id = None  # ID của người hiện tại (known hoặc "unknown")
        self.face_change_threshold = FACE_CHANGE_THRESHOLD  # Ngưỡng để xác định khuôn mặt khác (distance)
        
        # Metrics
        self.metrics = {
            'face': {'known': 0, 'unknown': 0},
            'voice': {'recognized': 0, 'unintelligible': 0},
            'greetings': {'known': 0, 'unknown': 0},
        }
        # Debounce and frame-level locks
        self.last_known_seen_time = 0.0
        self.last_greet_log_time = 0.0
        self.unknown_debounce_sec = 2.0
        
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
        """Xử lý nhận diện khuôn mặt với logic: chỉ đăng ký khi có người KHÁC xuất hiện"""
        try:
            # Detect faces và lấy encodings
            faces_with_encodings = self.face_module.detect_faces_with_encodings(frame)
            
            if not faces_with_encodings:
                # Không có khuôn mặt nào - không reset current_face
                # Giữ nguyên để khi người quay lại, vẫn nhận diện được
                return []
            
            # Lấy face data và encodings
            faces = [f['face_data'] for f in faces_with_encodings]
            
            # Metrics and UI update
            known_faces = [face for face in faces if face.get('person_id', 'unknown') != 'unknown']
            unknown_faces = [face for face in faces if face.get('person_id', 'unknown') == 'unknown']
            self.metrics['face']['known'] += len(known_faces)
            self.metrics['face']['unknown'] += len(unknown_faces)
            self.ui.update_recognition_results(faces)
            
            now = time.time()
            
            # Lấy khuôn mặt tốt nhất (known hoặc unknown)
            best_face_data = None
            best_face_encoding = None
            best_person_id = None
            best_person_name = None
            best_confidence = 0.0
            
            # Ưu tiên known faces
            if known_faces:
                best_known = max(known_faces, key=lambda x: x.get('confidence', 0.0))
                if best_known.get('confidence', 0.0) >= 0.65:
                    best_face_data = best_known
                    best_person_id = best_known.get('person_id')
                    best_person_name = best_known.get('name')
                    best_confidence = best_known.get('confidence', 0.0)
                    
                    # Tìm encoding tương ứng
                    for f in faces_with_encodings:
                        if f['face_data'] == best_known:
                            best_face_encoding = f['encoding']
                            break
            
            # Nếu không có known face đủ tốt, lấy unknown
            if best_face_data is None and unknown_faces:
                best_unknown = unknown_faces[0]  # Lấy unknown đầu tiên
                best_face_data = best_unknown
                best_person_id = "unknown"
                best_person_name = "Unknown"
                best_confidence = 0.0
                
                # Tìm encoding tương ứng
                for f in faces_with_encodings:
                    if f['face_data'] == best_unknown:
                        best_face_encoding = f['encoding']
                        break
            
            # Nếu có khuôn mặt được phát hiện
            if best_face_data and best_face_encoding is not None:
                # Kiểm tra xem có phải là người KHÁC không
                is_different = self._is_different_person(best_face_encoding, best_person_id)
                
                # QUAN TRỌNG: Nếu confidence quá thấp (< 0.60), coi như là người khác
                # Điều này xử lý trường hợp bị nhận diện nhầm do tolerance lỏng
                is_low_confidence = (best_person_id != "unknown" and best_confidence < 0.60)
                
                if is_low_confidence and self.current_person_id is not None:
                    self.system_logger.info(f"⚠️ Confidence thấp ({best_confidence:.3f} < 0.60) - Có thể là người khác!")
                    is_different = True  # Override: coi như người khác
                    best_person_id = "unknown"  # Đánh dấu là unknown
                    best_person_name = "Unknown"
                
                if is_different and not self.registration.is_active:
                    # Phát hiện người KHÁC → Tự động mở đăng ký
                    log_msg = f"Phat hien nguoi KHAC! Tu '{self.current_person_id}' sang '{best_person_id}'"
                    self.system_logger.info(log_msg)
                    self.ui.add_log_message(log_msg)
                    
                    if best_person_id == "unknown":
                        # Người mới chưa đăng ký
                        unknown_greeting = "Xin chào! Tôi phát hiện bạn là người mới. Bắt đầu đăng ký..."
                        self.ai_chatbot.speak_direct(unknown_greeting)
                        self.metrics['greetings']['unknown'] += 1
                        
                        # Cập nhật current face trước khi mở đăng ký
                        self._update_current_face(best_face_encoding, best_person_id)
                        
                        # Bắt đầu đăng ký inline
                        if self.registration.start():
                            time.sleep(1)
                            self.ai_chatbot.tts.speak_immediate("Vui lòng nói tên của bạn. Ví dụ: Tôi là Sơn")
                    else:
                        # Người mới nhưng đã có trong database
                        # Cập nhật current face và chào
                        self._update_current_face(best_face_encoding, best_person_id)
                        
                        if best_person_id not in self.greeted_people:
                            greeting = f"Xin chào {best_person_name}"
                            self.ai_chatbot.speak_direct(greeting)
                            self.metrics['greetings']['known'] += 1
                            self.greeted_people.add(best_person_id)
                            log_msg = f"👋 Chào người mới: {best_person_name}"
                            self.system_logger.info(log_msg)
                            self.ui.add_log_message(log_msg)
                
                elif not is_different:
                    # Cùng người → Xử lý bình thường
                    if best_person_id != "unknown":
                        # Người quen
                        self.last_known_seen_time = now
                        self.unknown_person_notified = False
                        
                        # Cập nhật current face nếu chưa có
                        if self.current_face_encoding is None:
                            self._update_current_face(best_face_encoding, best_person_id)
                        
                        # Chào nếu chưa chào
                        if best_person_id not in self.greeted_people:
                            greeting = f"Xin chào {best_person_name}"
                            self.ai_chatbot.speak_direct(greeting)
                            self.metrics['greetings']['known'] += 1
                            self.greeted_people.add(best_person_id)
                            self.current_user = best_person_id
                            self.last_interaction = time.time()
                            self.system_logger.info(f"Chao hoi: {best_person_name} (confidence: {best_confidence:.2f})")
                        else:
                            # Đã chào rồi, chỉ cập nhật
                            self.current_user = best_person_id
                            self.last_interaction = time.time()
                    else:
                        # Unknown nhưng cùng người
                        # Cập nhật current face nếu chưa có
                        if self.current_face_encoding is None:
                            self._update_current_face(best_face_encoding, best_person_id)
                        
                        # Không làm gì thêm (đã là unknown và cùng người)
                        pass
            
            return faces
            
        except Exception as e:
            self.system_logger.error(f"Loi xu ly face recognition: {e}")
            return []
    
    def process_voice_command(self):
        """Xử lý lệnh giọng nói"""
        try:
            # Lắng nghe giọng nói
            audio_text = self.voice_module.listen_for_command()

            if audio_text:
                log_msg = f"🎤 Nghe được: {audio_text}"
                self.system_logger.info(log_msg)
                self.ui.add_log_message(log_msg)
                self.metrics['voice']['recognized'] += 1

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

                # Xử lý giọng nói bình thường
                try:
                    response = self.ai_chatbot.speak_response(audio_text, priority="high")
                    if response and response.strip():
                        log_msg = f"🤖 Phản hồi: {response}"
                        self.system_logger.info(log_msg)
                        self.ui.add_log_message(log_msg)
                except Exception as e:
                    error_msg = f"❌ Lỗi chatbot: {str(e)[:50]}"
                    self.system_logger.error(error_msg)
                    self.ui.add_log_message(error_msg)
                    response = "Xin lỗi, có lỗi khi xử lý."

                self.last_interaction = time.time()
                return audio_text, response

        except Exception as e:
            error_msg = f"❌ Lỗi voice: {e}"
            self.system_logger.error(error_msg)
            self.ui.add_log_message(error_msg)
            self.metrics['voice']['unintelligible'] += 1

        return None, None
    
    def handle_text_input(self, text_input):
        """Xử lý input text từ UI"""
        if text_input.strip():
            log_msg = f"💬 Text input: {text_input}"
            self.system_logger.info(log_msg)
            self.ui.add_log_message(log_msg)
            
            # Kiểm tra nếu đang đăng ký
            if self.registration.is_active:
                response = self.registration.handle_voice_input(text_input)
                if response:
                    self.ai_chatbot.tts.speak_immediate(response)
                    log_msg = f"Phan hoi dang ky: {response}"
                    self.system_logger.info(log_msg)
                    self.ui.add_log_message(log_msg)
                    return response
            
            # Xử lý text bình thường
            response = self.ai_chatbot.speak_response(text_input, priority="normal")
            log_msg = f"🤖 Phản hồi: {response}"
            self.system_logger.info(log_msg)
            self.ui.add_log_message(log_msg)
            
            self.last_interaction = time.time()
            return response
        return None
    
    def _is_different_person(self, new_face_encoding, new_person_id):
        """Kiểm tra xem có phải là người KHÁC không"""
        # Nếu chưa có người nào → không phải người khác (là người đầu tiên)
        if self.current_face_encoding is None:
            return False
        
        # Nếu cùng person_id (cả 2 đều known và cùng ID) → không phải người khác
        if new_person_id != "unknown" and self.current_person_id != "unknown" and new_person_id == self.current_person_id:
            return False
        
        # So sánh face encoding để xác định
        try:
            import face_recognition
            distance = face_recognition.face_distance([self.current_face_encoding], new_face_encoding)[0]
            
            # Nếu distance > threshold → là người khác
            is_different = distance > self.face_change_threshold
            
            if is_different:
                self.system_logger.info(f"✨ Phát hiện người KHÁC! Distance: {distance:.3f} > {self.face_change_threshold}")
                self.system_logger.info(f"   Từ: {self.current_person_id} → Sang: {new_person_id}")
            
            return is_different
        except Exception as e:
            self.system_logger.error(f"Lỗi so sánh face encoding: {e}")
            return False
    
    def _update_current_face(self, face_encoding, person_id):
        """Cập nhật khuôn mặt hiện tại"""
        self.current_face_encoding = face_encoding
        self.current_person_id = person_id
        log_msg = f"📝 Cập nhật khuôn mặt hiện tại: {person_id}"
        self.system_logger.info(log_msg)
        self.ui.add_log_message(log_msg)
    

    
    def reload_face_encodings(self):
        """Reload face encodings sau khi có người dùng mới đăng ký"""
        log_msg = "🔄 Đang reload face encodings..."
        self.system_logger.info(log_msg)
        self.ui.add_log_message(log_msg)
        
        old_count = len(self.face_module.known_face_encodings)
        self.face_module.load_known_faces()
        new_count = len(self.face_module.known_face_encodings)
        
        if new_count > old_count:
            msg = f"✅ Reload thành công! +{new_count - old_count} người dùng"
        else:
            msg = f"✅ Reload xong. Tổng: {new_count} người dùng"
        
        self.system_logger.info(msg)
        self.ui.add_log_message(msg)
        
        # Reset trạng thái để nhận diện lại
        self.greeted_people.clear()
        self.unknown_person_notified = False
        self.last_known_seen_time = 0
    
    def check_idle_timeout(self):
        """Kiểm tra timeout không hoạt động"""
        if time.time() - self.last_interaction > 300:  # 5 phút
            if self.current_user:
                idle_msg = "Tôi vẫn ở đây nếu bạn cần hỗ trợ gì thêm."
                self.ai_chatbot.tts.speak_async(idle_msg)
                self.last_interaction = time.time()

    def reset_session(self):
        """Reset session state for new interactions"""
        self.greeted_people.clear()
        self.current_user = None
        self.unknown_person_notified = False
        self.session_start_time = time.time()
        self.system_logger.info("Session reset - ready for new interactions")
    
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
                # Kiểm tra camera có hoạt động không
                if not self.camera or not self.camera.isOpened():
                    self.system_logger.warning("⚠️ Camera không hoạt động, đang restart...")
                    if not self.start_camera():
                        self.system_logger.error("❌ Không thể restart camera!")
                        time.sleep(1)
                    continue
                
                # Đọc frame từ camera
                ret, frame = self.camera.read()
                if not ret:
                    self.system_logger.warning("⚠️ Không đọc được frame từ camera")
                    time.sleep(0.1)
                    continue
                
                # Xử lý face recognition
                faces = self.process_face_recognition(frame)
                
                # Xử lý đăng ký nếu đang active
                if self.registration.is_active:
                    should_cancel = self.registration.process(frame, faces)
                    if should_cancel:
                        # Phát hiện người quen -> Hủy đăng ký
                        known_face = max([f for f in faces if f.get('person_id', 'unknown') != 'unknown'], 
                                       key=lambda x: x.get('confidence', 0))
                        cancel_msg = f"Xin chào {known_face['name']}! Hủy đăng ký và chuyển sang nhận diện bạn."
                        self.ai_chatbot.tts.speak_immediate(cancel_msg)
                        self.registration.cancel()
                        # Cập nhật current face
                        if 'encoding' in known_face:
                            self._update_current_face(known_face['encoding'], known_face['person_id'])
                        if known_face['person_id'] not in self.greeted_people:
                            self.greeted_people.add(known_face['person_id'])
                            self.metrics['greetings']['known'] += 1
                    
                    # Kiểm tra nếu hoàn tất
                    if self.registration.state:
                        # Hoàn tất nếu đã chụp đủ ảnh (bỏ qua ghi âm nếu cần)
                        if self.registration.state['step'] == 'capture_face' and self.registration.state['face_count'] >= self.registration.state['max_faces']:
                            # Chuyển sang ghi âm
                            pass  # Đã xử lý trong _process_face_capture
                        
                        # Xử lý trạng thái completed (sau khi chụp đủ 5 ảnh)
                        elif self.registration.state['step'] == 'completed':
                            if self.registration.complete():
                                time.sleep(2)
                                # Reload và reset
                                self.reload_face_encodings()
                                self.registration.reset()
                                self.current_face_encoding = None
                                self.current_person_id = None
                                self.greeted_people.clear()
                
                # Kiểm tra idle timeout
                self.check_idle_timeout()
                
                # Hiển thị UI
                self.ui.update_frame(frame)
                
                # Xử lý input từ UI
                text_input = self.ui.get_text_input()
                if text_input:
                    self.handle_text_input(text_input)
                
                # Hiển thị UI với overlay
                self.ui.render()
                
                # Kiểm tra phím thoát
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' hoặc ESC
                    break
                elif key == ord('s'):  # 's' để dừng giọng nói
                    self.ai_chatbot.tts.stop_current_speech()
                elif key == ord('h'):  # 'h' để help
                    help_msg = "Phím tắt: Q=Thoát, S=Dừng giọng, H=Trợ giúp, R=Reload, C=Clear cache"
                    self.ai_chatbot.tts.speak_immediate(help_msg)
                elif key == ord('r'):  # 'r' để reload
                    self.reload_face_encodings()
                    msg = "Đã reload danh sách người dùng"
                    self.ai_chatbot.tts.speak_immediate(msg)
                elif key == ord('c'):  # 'c' để clear cache
                    self.current_face_encoding = None
                    self.current_person_id = None
                    self.greeted_people.clear()
                    msg = "Đã xóa cache nhận diện"
                    self.system_logger.info(msg)
                    self.ai_chatbot.tts.speak_immediate(msg)
                elif key == ord('f'):  # 'f' để hoàn tất đăng ký sớm (finish)
                    if self.registration.is_active and self.registration.state:
                        if self.registration.state['face_count'] >= 3:
                            log_msg = "Nguoi dung hoan tat dang ky som (phim F)"
                            self.system_logger.info(log_msg)
                            self.ui.add_log_message(log_msg)
                            if self.registration.complete():
                                time.sleep(2)
                                self.reload_face_encodings()
                                self.registration.reset()
                                self.current_face_encoding = None
                                self.current_person_id = None
                                self.greeted_people.clear()
                                self.registration.reset()
                                self.current_face_encoding = None
                                self.current_person_id = None
                                self.greeted_people.clear()
                        else:
                            msg = f"Can it nhat 3 anh de hoan tat (hien co {self.registration.state['face_count']})"
                            self.system_logger.info(msg)
                            self.ui.add_log_message(msg)
        
        except KeyboardInterrupt:
            self.system_logger.info("⚠️ Nhận tín hiệu dừng từ người dùng")
        
        except Exception as e:
            self.system_logger.error(f"Loi trong main loop: {e}")
        
        finally:
            self.cleanup()
    
    def _voice_worker(self):
        """Worker thread cho voice recognition"""
        print("[VOICE] Voice worker thread started")
        while self.running:
            try:
                result = self.process_voice_command()
                if result and result[0]:  # If we got voice input
                    print(f"[VOICE] Voice worker processed: {result[0]}")
                time.sleep(0.1)
            except Exception as e:
                print(f"[VOICE] Voice worker error: {e}")
                self.system_logger.error(f"Loi voice worker: {e}")
                time.sleep(1)
        print("[VOICE] Voice worker thread stopped")
    
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
        # Report metrics summary
        try:
            total_faces = self.metrics['face']['known'] + self.metrics['face']['unknown']
            voice_total = self.metrics['voice']['recognized'] + self.metrics['voice']['unintelligible']
            face_known_rate = (self.metrics['face']['known'] / total_faces) if total_faces else 0
            voice_recognize_rate = (self.metrics['voice']['recognized'] / voice_total) if voice_total else 0
            self.system_logger.info(
                f"Metrics: faces_total={total_faces}, known_rate={face_known_rate:.2f}, voice_total={voice_total}, voice_recognize_rate={voice_recognize_rate:.2f}, greetings_known={self.metrics['greetings']['known']}, greetings_unknown={self.metrics['greetings']['unknown']}"
            )
        except Exception:
            pass
        
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