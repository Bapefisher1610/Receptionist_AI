#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inline Registration Module - Đăng ký người dùng trong cùng cửa sổ camera
"""

import cv2
import time
import uuid
import os
from pathlib import Path
from ..core.config import FACES_DIR, VOICES_DIR


class InlineRegistration:
    """Xử lý đăng ký người dùng trong cùng cửa sổ camera"""
    
    def __init__(self, face_module, voice_module, logger, ui):
        self.face_module = face_module
        self.voice_module = voice_module
        self.logger = logger
        self.ui = ui
        
        # Registration state
        self.is_active = False
        self.state = None
        self.user_id = None
        self.user_name = None
        self.user_dir = None
        
        # Cooldown timers
        self._last_capture_time = 0
        self._last_voice_time = 0
        
    def start(self):
        """Bắt đầu quy trình đăng ký"""
        if self.is_active:
            self.logger.info("⚠️ Đăng ký đang trong quá trình")
            return False
        
        try:
            self.is_active = True
            
            # Tạo user ID và thư mục
            self.user_id = str(uuid.uuid4())[:8]
            self.user_dir = FACES_DIR / self.user_id
            os.makedirs(self.user_dir, exist_ok=True)
            
            # Khởi tạo state
            self.state = {
                'step': 'get_name',  # get_name -> capture_face -> capture_voice -> complete
                'name': '',
                'face_count': 0,
                'voice_count': 0,
                'max_faces': 5,
                'max_voices': 3,
                'voice_keywords': []
            }
            
            # Hiển thị UI (không dấu cho font)
            self.ui.show_registration_ui(
                "DANG KY NGUOI DUNG MOI",
                "",
                "Vui long noi ten cua ban..."
            )
            
            self.logger.info(f"Bat dau dang ky - User ID: {self.user_id}")
            self.ui.add_log_message(f"Bat dau dang ky - ID: {self.user_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khởi động đăng ký: {e}")
            self.ui.add_log_message(f"❌ Lỗi: {e}")
            self.is_active = False
            return False
    
    def process(self, frame, detected_faces):
        """
        Xử lý quy trình đăng ký
        Returns: True nếu phát hiện người quen (cần hủy đăng ký)
        """
        if not self.is_active or not self.state:
            return False
        
        # Kiểm tra nếu có người quen xuất hiện -> Hủy đăng ký
        known_faces = [f for f in detected_faces if f.get('person_id', 'unknown') != 'unknown' and f.get('confidence', 0) >= 0.60]
        if known_faces:
            best_known = max(known_faces, key=lambda x: x.get('confidence', 0))
            self.logger.info(f"🔄 Phát hiện người quen {best_known['name']} - Hủy đăng ký")
            self.ui.add_log_message(f"🔄 Phát hiện {best_known['name']} - Hủy đăng ký")
            return True  # Signal to cancel
        
        # Xử lý theo step
        if self.state['step'] == 'capture_face':
            self._process_face_capture(frame)
        elif self.state['step'] == 'capture_voice':
            self._process_voice_capture()
        
        return False
    
    def handle_voice_input(self, text):
        """Xử lý input giọng nói trong quá trình đăng ký"""
        if not self.is_active or not self.state:
            self.logger.info(f"[DEBUG] handle_voice_input: not active or no state")
            return None
        
        self.logger.info(f"[DEBUG] handle_voice_input: step={self.state['step']}, text='{text}'")
        
        if self.state['step'] == 'get_name':
            # Trích xuất tên
            name = self._extract_name(text)
            self.logger.info(f"[DEBUG] Extracted name: '{name}' from text: '{text}'")
            
            if name:
                self.state['name'] = name
                self.user_name = name
                self.state['step'] = 'capture_face'
                
                self.logger.info(f"Da nhan ten: {name}")
                self.ui.add_log_message(f"Da nhan ten: {name}")
                
                # CẬP NHẬT UI NGAY LẬP TỨC
                self.ui.update_registration_status(
                    f"CHUP ANH KHUAN MAT (0/5)",
                    name,
                    "Nhin thang vao camera..."
                )
                
                return f"Xin chào {name}! Bây giờ tôi sẽ chụp ảnh khuôn mặt của bạn."
            else:
                self.logger.info(f"[DEBUG] Khong trich xuat duoc ten tu: '{text}'")
                self.ui.update_registration_status(
                    "KHONG HIEU TEN",
                    "",
                    "Vui long noi ro hon..."
                )
                return "Xin lỗi, tôi không hiểu tên của bạn. Vui lòng nói rõ hơn."
        
        return None
    
    def _process_face_capture(self, frame):
        """Xử lý chụp ảnh khuôn mặt"""
        current_time = time.time()
        if current_time - self._last_capture_time < 1.5:  # Cooldown 1.5s
            return
        
        # Phát hiện khuôn mặt
        faces = self.face_module.detect_faces(frame)
        
        if faces and len(faces) > 0:
            # Lưu ảnh
            timestamp = int(time.time())
            image_path = self.user_dir / f"{timestamp}.jpg"
            cv2.imwrite(str(image_path), frame)
            
            # Thêm face vào module
            if self.face_module.add_face(frame, self.user_id, self.user_name):
                self.state['face_count'] += 1
                self._last_capture_time = current_time
                
                log_msg = f"Da chup anh {self.state['face_count']}/{self.state['max_faces']}"
                self.logger.info(log_msg)
                self.ui.add_log_message(log_msg)
                
                # CẬP NHẬT UI NGAY
                self.ui.update_registration_status(
                    f"CHUP ANH ({self.state['face_count']}/{self.state['max_faces']})",
                    self.user_name,
                    "Thay doi goc do..." if self.state['face_count'] < self.state['max_faces'] else "Hoan tat!"
                )
                
                # Kiểm tra đã đủ ảnh chưa
                if self.state['face_count'] >= self.state['max_faces']:
                    self.state['step'] = 'capture_voice'
                    log_msg = "Hoan tat chup anh! Chuyen sang ghi am"
                    self.logger.info(log_msg)
                    self.ui.add_log_message(log_msg)
                    
                    # CẬP NHẬT UI SANG BƯỚC GHI ÂM
                    self.ui.update_registration_status(
                        f"GHI AM GIONG NOI (0/3)",
                        self.user_name,
                        f"Hay noi: 'Xin chao, toi la {self.user_name}'"
                    )
                    
                    # Thông báo bằng giọng nói có dấu
                    from ..modules.tts.streaming_tts_module import StreamingTTSModule
                    tts = StreamingTTSModule()
                    tts.speak_immediate(f"Tuyệt vời! Bây giờ hãy nói: Xin chào, tôi là {self.user_name}")
    
    def _process_voice_capture(self):
        """Xử lý ghi âm giọng nói"""
        current_time = time.time()
        if current_time - self._last_voice_time < 2.0:  # Cooldown 2s
            return
        
        try:
            # Lắng nghe giọng nói
            audio_text = self.voice_module.listen_for_command(timeout=2, phrase_time_limit=4)
            
            if audio_text and len(audio_text.strip()) > 0:
                self._last_voice_time = current_time
                
                # Trích xuất keywords
                words = audio_text.split()
                keywords = [word for word in words if len(word) > 3]
                self.state['voice_keywords'].extend(keywords)
                
                self.state['voice_count'] += 1
                
                log_msg = f"Da ghi am {self.state['voice_count']}/{self.state['max_voices']}: {audio_text}"
                self.logger.info(log_msg)
                self.ui.add_log_message(log_msg)
                
                # Kiểm tra đã đủ chưa
                if self.state['voice_count'] >= self.state['max_voices']:
                    return True  # Signal to complete
                else:
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
                    
                    next_phrase_ui = phrases_ui[self.state['voice_count']] if self.state['voice_count'] < len(phrases_ui) else "Noi bat ky"
                    next_phrase_tts = phrases_tts[self.state['voice_count']] if self.state['voice_count'] < len(phrases_tts) else "Nói bất kỳ câu nào"
                    
                    # CẬP NHẬT UI
                    self.ui.update_registration_status(
                        f"GHI AM ({self.state['voice_count']}/{self.state['max_voices']})",
                        self.user_name,
                        f"Hay noi: {next_phrase_ui}"
                    )
                    
                    # Thông báo bằng giọng nói có dấu
                    from ..modules.tts.streaming_tts_module import StreamingTTSModule
                    tts = StreamingTTSModule()
                    tts.speak_immediate(f"Tốt! Bây giờ hãy nói: {next_phrase_tts}")
        except:
            pass
        
        return False
    
    def complete(self):
        """Hoàn tất đăng ký"""
        try:
            log_msg = "Dang luu thong tin..."
            self.logger.info(log_msg)
            self.ui.add_log_message(log_msg)
            
            # CẬP NHẬT UI (không dấu)
            self.ui.update_registration_status(
                "DANG LUU THONG TIN...",
                self.user_name,
                "Vui long doi..."
            )
            
            # Thông báo bằng giọng nói (có dấu)
            from ..modules.tts.streaming_tts_module import StreamingTTSModule
            tts = StreamingTTSModule()
            tts.speak_immediate("Đang lưu thông tin của bạn...")
            
            # Lưu metadata
            metadata_path = self.user_dir / "metadata.txt"
            metadata_path.write_text(self.user_name, encoding='utf-8')
            
            # Lưu voice patterns
            if self.state['voice_keywords']:
                unique_keywords = list(set(self.state['voice_keywords']))
                if self.voice_module.add_voice_pattern(self.user_id, self.user_name, unique_keywords):
                    log_msg = f"Da luu {len(unique_keywords)} tu khoa"
                    self.logger.info(log_msg)
                    self.ui.add_log_message(log_msg)
            
            log_msg = f"Dang ky thanh cong: {self.user_name} (ID: {self.user_id})"
            self.logger.info(log_msg)
            self.ui.add_log_message(log_msg)
            
            # CẬP NHẬT UI HOÀN TẤT (không dấu)
            self.ui.update_registration_status(
                "HOAN TAT!",
                self.user_name,
                "Dang ky thanh cong!"
            )
            
            # Thông báo bằng giọng nói (có dấu)
            from ..modules.tts.streaming_tts_module import StreamingTTSModule
            tts = StreamingTTSModule()
            tts.speak_immediate(f"Hoàn tất! Đăng ký thành công cho {self.user_name}!")
            
            return True
            
        except Exception as e:
            error_msg = f"Loi khi luu: {e}"
            self.logger.error(error_msg)
            self.ui.add_log_message(error_msg)
            
            self.ui.update_registration_status(
                "LOI!",
                self.user_name,
                f"Loi: {str(e)[:30]}"
            )
            return False
    
    def cancel(self):
        """Hủy đăng ký"""
        try:
            if self.user_dir and self.user_dir.exists():
                import shutil
                shutil.rmtree(self.user_dir, ignore_errors=True)
                self.logger.info(f"Da xoa thu muc: {self.user_dir}")
            
            self.is_active = False
            self.state = None
            self.user_id = None
            self.user_name = None
            self.user_dir = None
            self._last_capture_time = 0
            self._last_voice_time = 0
            
            self.ui.hide_registration_ui()
            
            log_msg = "Da huy dang ky"
            self.logger.info(log_msg)
            self.ui.add_log_message(log_msg)
            
        except Exception as e:
            self.logger.error(f"Loi khi huy: {e}")
    
    def reset(self):
        """Reset sau khi hoàn tất"""
        self.is_active = False
        self.state = None
        self.user_id = None
        self.user_name = None
        self.user_dir = None
        self._last_capture_time = 0
        self._last_voice_time = 0
        self.ui.hide_registration_ui()
    
    def _extract_name(self, text):
        """Trích xuất tên từ text"""
        if not text:
            return None
            
        text = text.strip().lower()
        self.logger.info(f"[DEBUG] _extract_name input: '{text}'")
        
        # Các pattern để tìm tên
        patterns = [
            'tên tôi là', 'tôi là', 'tôi tên', 'mình là', 'mình tên',
            'tên là', 'tên mình là', 'em là', 'anh là', 'chị là',
            'ten toi la', 'toi la', 'toi ten', 'minh la', 'minh ten',
            'ten la', 'ten minh la', 'em la', 'anh la', 'chi la'
        ]
        
        for pattern in patterns:
            if pattern in text:
                name_part = text.split(pattern, 1)[1].strip()
                self.logger.info(f"[DEBUG] Found pattern '{pattern}', name_part: '{name_part}'")
                words = name_part.split()
                if words:
                    name = words[0]
                    skip_words = ['ạ', 'à', 'ơi', 'nhé', 'nha', 'đây', 'đó', 'a', 'nhe']
                    if name not in skip_words and len(name) > 1:
                        result = name.title()
                        self.logger.info(f"[DEBUG] Extracted name from pattern: '{result}'")
                        return result
        
        # Nếu không tìm thấy pattern, lấy từ đầu tiên có ý nghĩa
        words = text.split()
        self.logger.info(f"[DEBUG] No pattern found, trying words: {words}")
        
        for word in words:
            if len(word) > 1 and word.isalpha():
                skip_words = ['xin', 'chào', 'tôi', 'mình', 'em', 'anh', 'chị', 'là', 
                             'chao', 'toi', 'minh', 'la', 'ten', 'tên']
                if word not in skip_words:
                    result = word.title()
                    self.logger.info(f"[DEBUG] Extracted name from words: '{result}'")
                    return result
        
        self.logger.info(f"[DEBUG] Could not extract name from: '{text}'")
        return None
