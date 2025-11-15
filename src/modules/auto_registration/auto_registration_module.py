import os
import cv2
import uuid
import time
from datetime import datetime
from pathlib import Path

from ...core.config import FACES_DIR, VOICES_DIR
from ...utils.utils import get_timestamp

class AutoRegistrationModule:
    def __init__(self, face_module, voice_module, logger):
        """Initialize auto registration module"""
        self.face_module = face_module
        self.voice_module = voice_module
        self.logger = logger
        
        # Registration state
        self.pending_registration = None
        self.registration_timeout = 60  # 60 seconds timeout
        self.captured_face_frame = None
        self.captured_voice_text = None
        self.registration_start_time = None
        
    def start_registration(self, frame):
        """Bắt đầu quá trình đăng ký người dùng mới"""
        if self.pending_registration:
            return False  # Already in registration process
            
        # Generate unique person ID
        person_id = str(uuid.uuid4())[:8]
        
        # Capture current frame for face
        self.captured_face_frame = frame.copy()
        
        # Initialize registration state
        self.pending_registration = {
            'person_id': person_id,
            'status': 'waiting_for_name',
            'face_captured': True,
            'voice_captured': False,
            'name': None,
            'voice_keywords': []
        }
        
        self.registration_start_time = time.time()
        
        self.logger.info(f"🆕 Bắt đầu đăng ký người dùng mới: {person_id}")
        return True
        
    def process_voice_input(self, text_input):
        """Xử lý input trong quá trình đăng ký"""
        if not self.pending_registration:
            return None
            
        # Check timeout
        if time.time() - self.registration_start_time > self.registration_timeout:
            self.cancel_registration()
            return {'status': 'timeout', 'message': 'Quá trình đăng ký đã hết thời gian. Vui lòng thử lại.'}
            
        status = self.pending_registration['status']
        
        if status == 'waiting_for_name':
            # Extract name from input
            name = self._extract_name_from_text(text_input)
            if name:
                self.pending_registration['name'] = name
                self.pending_registration['status'] = 'collecting_voice'
                
                # Add current text as voice keyword
                self.pending_registration['voice_keywords'].append(text_input.lower())
                
                return {
                    'status': 'processing',
                    'person_name': name,
                    'message': f'Cảm ơn {name}! Tôi đã ghi nhận tên của bạn. Hãy nói thêm vài câu để tôi nhận diện giọng nói của bạn.'
                }
            else:
                return {
                    'status': 'need_more_info',
                    'message': 'Tôi không hiểu tên của bạn. Vui lòng nói rõ tên của bạn.'
                }
                
        elif status == 'collecting_voice':
            # Collect more voice samples
            self.pending_registration['voice_keywords'].append(text_input.lower())
            
            # If we have enough voice samples, complete registration
            if len(self.pending_registration['voice_keywords']) >= 3:
                return self._complete_registration()
            else:
                remaining = 3 - len(self.pending_registration['voice_keywords'])
                return {
                    'status': 'processing',
                    'person_name': self.pending_registration['name'],
                    'message': f'Tốt! Hãy nói thêm {remaining} câu nữa để hoàn tất đăng ký.'
                }
                
        return None
        
    def _extract_name_from_text(self, text):
        """Trích xuất tên từ văn bản"""
        # Simple name extraction - look for common patterns
        text = text.strip().lower()
        
        # Remove common phrases
        name_indicators = ['tên tôi là', 'tôi là', 'tôi tên', 'mình là', 'mình tên']
        
        for indicator in name_indicators:
            if indicator in text:
                name_part = text.split(indicator, 1)[1].strip()
                # Take first word as name
                name = name_part.split()[0] if name_part.split() else None
                if name and len(name) > 1:
                    return name.title()
                    
        # If no indicator found, try to extract first meaningful word
        words = text.split()
        for word in words:
            if len(word) > 2 and word.isalpha():
                return word.title()
                
        return None
        
    def _complete_registration(self):
        """Hoàn tất quá trình đăng ký"""
        try:
            person_id = self.pending_registration['person_id']
            name = self.pending_registration['name']
            voice_keywords = self.pending_registration['voice_keywords']
            
            # Save face to database
            if self.captured_face_frame is not None:
                success = self.face_module.add_face(
                    self.captured_face_frame, 
                    person_id, 
                    name
                )
                
                if not success:
                    return {
                        'status': 'error',
                        'message': 'Không thể lưu khuôn mặt. Vui lòng thử lại.'
                    }
                    
            # Save voice pattern to database
            success = self.voice_module.add_voice_pattern(
                person_id,
                name,
                voice_keywords
            )
            
            if not success:
                return {
                    'status': 'error',
                    'message': 'Không thể lưu giọng nói. Vui lòng thử lại.'
                }
                
            # Log successful registration
            self.logger.info(f"✅ Đăng ký thành công: {name} (ID: {person_id})")
            
            # Clear registration state
            self.pending_registration = None
            self.captured_face_frame = None
            self.registration_start_time = None
            
            return {
                'status': 'completed',
                'person_name': name,
                'message': f'Chào mừng {name}! Tôi đã ghi nhận thông tin của bạn. Từ giờ tôi sẽ nhận ra bạn.'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi đăng ký: {e}")
            self.cancel_registration()
            return {
                'status': 'error',
                'message': 'Có lỗi xảy ra trong quá trình đăng ký. Vui lòng thử lại.'
            }
            
    def cancel_registration(self):
        """Hủy quá trình đăng ký"""
        if self.pending_registration:
            person_id = self.pending_registration['person_id']
            self.logger.info(f"❌ Hủy đăng ký: {person_id}")
            
        self.pending_registration = None
        self.captured_face_frame = None
        self.registration_start_time = None
        
    def is_registering(self):
        """Kiểm tra xem có đang trong quá trình đăng ký không"""
        return self.pending_registration is not None
        
    def get_registration_status(self):
        """Lấy trạng thái đăng ký hiện tại"""
        if not self.pending_registration:
            return None
            
        return {
            'person_id': self.pending_registration['person_id'],
            'status': self.pending_registration['status'],
            'name': self.pending_registration.get('name'),
            'voice_samples': len(self.pending_registration['voice_keywords']),
            'time_remaining': max(0, self.registration_timeout - (time.time() - self.registration_start_time))
        }