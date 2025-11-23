import os
import cv2
import face_recognition
import numpy as np
from pathlib import Path
import pickle
import time
from datetime import datetime

from ...core.config import (
    FACES_DIR, FACE_RECOGNITION_TOLERANCE, FACE_RECOGNITION_MODEL, 
    FACE_MATCH_MARGIN, STRICT_FOLDER_EXISTENCE, MIN_FACE_DISTANCE, 
    MIN_CONFIDENCE_THRESHOLD, MIN_FACE_SIZE, FACE_DETECTION_UPSAMPLE,
    ENABLE_PREPROCESSING
)
from ...utils.utils import load_image_from_path, resize_image

class FaceRecognitionModule:
    def __init__(self, logger):
        """Initialize the face recognition module"""
        self.logger = logger
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.encodings_file = FACES_DIR / 'encodings.pkl'
        
        # Load existing face encodings if available
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known face encodings from file or directory"""
        # Try to load from pickle file first (faster)
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get('encodings', [])
                    self.known_face_names = data.get('names', [])
                    self.known_face_ids = data.get('ids', [])
                print(f"Loaded {len(self.known_face_encodings)} face encodings from file")
                return
            except Exception as e:
                print(f"Error loading face encodings: {e}")
        
        # If pickle file doesn't exist or has an error, load from image files
        self._load_from_image_files()
    
    def _load_from_image_files(self):
        """Load face encodings from image files in the faces directory"""
        # Reset lists
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        # Ensure the faces directory exists
        os.makedirs(FACES_DIR, exist_ok=True)
        
        # Get all subdirectories (one per person)
        person_dirs = [d for d in FACES_DIR.iterdir() if d.is_dir()]
        
        for person_dir in person_dirs:
            person_id = person_dir.name
            
            # Get person name from metadata file if it exists
            person_name = person_id
            metadata_file = person_dir / 'metadata.txt'
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    person_name = f.read().strip()
            
            # Get all image files for this person
            image_files = list(person_dir.glob('*.jpg')) + list(person_dir.glob('*.png'))
            
            if not image_files:
                continue
                
            # Process each image file
            for image_file in image_files:
                image = load_image_from_path(image_file)
                if image is None:
                    continue
                
                # Find face encodings in the image
                face_encodings = face_recognition.face_encodings(image)
                
                if face_encodings:
                    # Use the first face encoding found
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_names.append(person_name)
                    self.known_face_ids.append(person_id)
        
        # Save encodings to file for faster loading next time
        if self.known_face_encodings:
            self._save_encodings()
            
        print(f"Loaded {len(self.known_face_encodings)} face encodings from image files")
    
    def _save_encodings(self):
        """Save face encodings to a pickle file for faster loading"""
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names,
            'ids': self.known_face_ids
        }
        
        os.makedirs(FACES_DIR, exist_ok=True)
        
        with open(self.encodings_file, 'wb') as f:
            pickle.dump(data, f)
    
    def add_face(self, face_image, person_id, person_name):
        """Add a new face to the known faces"""
        if face_image is None:
            return False

        # Ensure RGB color for encoding
        try:
            face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        except Exception:
            face_rgb = face_image
        # Get face encoding
        face_encodings = face_recognition.face_encodings(face_rgb)

        if not face_encodings:
            return False

        # Add to known faces
        self.known_face_encodings.append(face_encodings[0])
        self.known_face_names.append(person_name)
        self.known_face_ids.append(person_id)

        # Save the face image
        person_dir = FACES_DIR / person_id
        os.makedirs(person_dir, exist_ok=True)

        # Save metadata
        with open(person_dir / 'metadata.txt', 'w', encoding='utf-8') as f:
            f.write(person_name)

        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = person_dir / f"{timestamp}.jpg"
        
        # Convert RGB to BGR for OpenCV
        try:
            cv2.imwrite(str(image_path), cv2.cvtColor(face_rgb, cv2.COLOR_RGB2BGR))
        except Exception:
            cv2.imwrite(str(image_path), face_image)
        
        # Update encodings file
        self._save_encodings()
        
        return True
        
    def capture_face_from_frame(self, frame):
        """Capture and extract face from current frame for registration"""
        try:
            # Find face locations in the frame
            face_locations = face_recognition.face_locations(frame)
            
            if not face_locations:
                return None
                
            # Get the largest face (closest to camera)
            largest_face = max(face_locations, key=lambda loc: (loc[2] - loc[0]) * (loc[1] - loc[3]))
            
            # Extract face region
            top, right, bottom, left = largest_face
            
            # Add some padding around the face
            padding = 20
            height, width = frame.shape[:2]
            
            top = max(0, top - padding)
            bottom = min(height, bottom + padding)
            left = max(0, left - padding)
            right = min(width, right + padding)
            
            # Extract face image
            face_image = frame[top:bottom, left:right]
            
            # Convert BGR to RGB for face_recognition library
            face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            return face_image_rgb
            
        except Exception as e:
            print(f"Error capturing face from frame: {e}")
            return None
    
    def _calculate_face_center(self, location):
        """Tính tọa độ trung tâm của khuôn mặt"""
        top, right, bottom, left = location
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2
        return (center_x, center_y)
    
    def _calculate_distance(self, point1, point2):
        """Tính khoảng cách Euclidean giữa 2 điểm"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def _remove_duplicate_faces(self, results):
        """Loại bỏ các khuôn mặt trùng lặp (cùng 1 người được nhận diện nhiều lần)"""
        if len(results) <= 1:
            return results
        
        # Nhóm các khuôn mặt theo person_id
        person_groups = {}
        for result in results:
            person_id = result['person_id']
            if person_id not in person_groups:
                person_groups[person_id] = []
            person_groups[person_id].append(result)
        
        # Với mỗi person_id, chỉ giữ lại khuôn mặt có confidence cao nhất
        filtered_results = []
        for person_id, faces in person_groups.items():
            if person_id == "unknown":
                # Với unknown, kiểm tra khoảng cách giữa các khuôn mặt
                # Chỉ giữ những khuôn mặt cách xa nhau
                unique_unknowns = []
                for face in faces:
                    face_center = self._calculate_face_center(face['location'])
                    is_duplicate = False
                    
                    for existing_face in unique_unknowns:
                        existing_center = self._calculate_face_center(existing_face['location'])
                        distance = self._calculate_distance(face_center, existing_center)
                        
                        if distance < MIN_FACE_DISTANCE:
                            # Đây là duplicate, giữ cái có confidence cao hơn
                            is_duplicate = True
                            if face['confidence'] > existing_face['confidence']:
                                unique_unknowns.remove(existing_face)
                                unique_unknowns.append(face)
                            break
                    
                    if not is_duplicate:
                        unique_unknowns.append(face)
                
                filtered_results.extend(unique_unknowns)
            else:
                # Với người đã biết, chỉ giữ khuôn mặt có confidence cao nhất
                best_face = max(faces, key=lambda x: x['confidence'])
                filtered_results.append(best_face)
        
        return filtered_results
    
    def _preprocess_frame(self, frame):
        """Tiền xử lý frame để cải thiện nhận diện trong điều kiện ánh sáng kém"""
        try:
            # Chuyển sang grayscale để kiểm tra độ sáng
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Tính độ sáng trung bình
            brightness = np.mean(gray)
            
            # Nếu quá tối hoặc quá sáng, điều chỉnh
            if brightness < 80:  # Quá tối
                # Tăng độ sáng
                frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=30)
            elif brightness > 180:  # Quá sáng
                # Giảm độ sáng
                frame = cv2.convertScaleAbs(frame, alpha=0.8, beta=-20)
            
            # Áp dụng histogram equalization để cân bằng ánh sáng
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            frame = cv2.merge([l, a, b])
            frame = cv2.cvtColor(frame, cv2.COLOR_LAB2BGR)
            
            # Giảm nhiễu
            frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
            
            return frame
        except Exception as e:
            print(f"Lỗi tiền xử lý frame: {e}")
            return frame
    
    def _is_valid_face(self, location):
        """Kiểm tra xem khuôn mặt có hợp lệ không (đủ lớn, không bị cắt)"""
        top, right, bottom, left = location
        
        # Kiểm tra kích thước
        width = right - left
        height = bottom - top
        
        if width < MIN_FACE_SIZE or height < MIN_FACE_SIZE:
            return False
        
        # Kiểm tra tỷ lệ (khuôn mặt thường có tỷ lệ gần 1:1)
        ratio = width / height if height > 0 else 0
        if ratio < 0.6 or ratio > 1.4:
            return False
        
        return True
    
    def recognize_faces(self, frame):
        """Recognize faces in a frame and return results"""
        # If no known faces, return empty results
        if not self.known_face_encodings:
            return []
        
        # Resize frame for faster processing (scale down by 0.5)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        
        # Convert the image from BGR color (OpenCV) to RGB color (face_recognition)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find all face locations and face encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame, model=FACE_RECOGNITION_MODEL)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        results = []
        
        # Loop through each face found in the frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            person_id = "unknown"
            confidence = 0.0

            # Compute distances to all known encodings
            if len(self.known_face_encodings) > 0:
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_idx = int(np.argmin(distances))
                best_dist = float(distances[best_idx])
                candidate_id = self.known_face_ids[best_idx]
                candidate_dir_ok = True
                if STRICT_FOLDER_EXISTENCE:
                    candidate_dir_ok = (FACES_DIR / candidate_id).exists()
                
                # Tính confidence trước
                temp_confidence = max(0.0, 1.0 - best_dist)
                
                # Decision: chỉ chấp nhận nếu:
                # 1. Candidate tồn tại trong folder
                # 2. Distance trong tolerance
                # 3. Confidence đủ cao (>= MIN_CONFIDENCE_THRESHOLD)
                if candidate_dir_ok and best_dist <= FACE_RECOGNITION_TOLERANCE and temp_confidence >= MIN_CONFIDENCE_THRESHOLD:
                    confidence = temp_confidence
                    name = self.known_face_names[best_idx]
                    person_id = candidate_id
                else:
                    # Không đạt ngưỡng - đánh dấu là Unknown
                    name = "Unknown"
                    person_id = "unknown"
                    confidence = 0.0
            
            # Scale back coordinates to original frame size
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            
            # Add to results
            results.append({
                'name': name,
                'person_id': person_id,
                'confidence': confidence,
                'location': (top, right, bottom, left)
            })
            
            # Log the recognition if confidence is high enough and not unknown
            if name != "Unknown" and confidence >= 0.5:
                self.logger.log_recognition(person_id, name, "face", confidence)
        
        # Loại bỏ các khuôn mặt trùng lặp
        results = self._remove_duplicate_faces(results)
        
        return results
    
    def detect_faces(self, frame):
        """Detect and recognize faces in frame, return list of detected faces"""
        return self.recognize_faces(frame)
    
    def detect_faces_with_encodings(self, frame):
        """Detect faces và trả về cả face data và encodings"""
        try:
            # Tiền xử lý frame (nếu được bật)
            if ENABLE_PREPROCESSING:
                processed_frame = self._preprocess_frame(frame)
            else:
                processed_frame = frame
            
            # Resize frame
            small_frame = cv2.resize(processed_frame, (0, 0), fx=0.5, fy=0.5)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(
                rgb_frame,
                model=FACE_RECOGNITION_MODEL,
                number_of_times_to_upsample=FACE_DETECTION_UPSAMPLE
            )
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            results = []
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Scale back
                top *= 2
                right *= 2
                bottom *= 2
                left *= 2
                
                # Validate
                if not self._is_valid_face((top, right, bottom, left)):
                    continue
                
                name = "Unknown"
                person_id = "unknown"
                confidence = 0.0
                
                # Match với known faces
                if len(self.known_face_encodings) > 0:
                    distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_idx = int(np.argmin(distances))
                    best_dist = float(distances[best_idx])
                    candidate_id = self.known_face_ids[best_idx]
                    candidate_dir_ok = True
                    
                    if STRICT_FOLDER_EXISTENCE:
                        candidate_dir_ok = (FACES_DIR / candidate_id).exists()
                    
                    temp_confidence = max(0.0, 1.0 - best_dist)
                    
                    # Debug logging
                    print(f"[DEBUG] Matching: {self.known_face_names[best_idx]} - Distance: {best_dist:.3f}, Confidence: {temp_confidence:.3f}")
                    print(f"[DEBUG] Thresholds: Tolerance={FACE_RECOGNITION_TOLERANCE}, Min_Confidence={MIN_CONFIDENCE_THRESHOLD}")
                    
                    if candidate_dir_ok and best_dist <= FACE_RECOGNITION_TOLERANCE and temp_confidence >= MIN_CONFIDENCE_THRESHOLD:
                        confidence = temp_confidence
                        name = self.known_face_names[best_idx]
                        person_id = candidate_id
                        print(f"[DEBUG] ✅ MATCHED: {name} (distance: {best_dist:.3f}, confidence: {confidence:.3f})")
                    else:
                        print(f"[DEBUG] ❌ NOT MATCHED: distance={best_dist:.3f} > {FACE_RECOGNITION_TOLERANCE} OR confidence={temp_confidence:.3f} < {MIN_CONFIDENCE_THRESHOLD}")
                
                # Tạo face data
                face_data = {
                    'name': name,
                    'person_id': person_id,
                    'confidence': confidence,
                    'location': (top, right, bottom, left)
                }
                
                # Log nếu là known
                if name != "Unknown" and confidence >= 0.5:
                    self.logger.log_recognition(person_id, name, "face", confidence)
                
                results.append({
                    'face_data': face_data,
                    'encoding': face_encoding
                })
            
            # Remove duplicates
            face_data_list = [r['face_data'] for r in results]
            filtered_face_data = self._remove_duplicate_faces(face_data_list)
            
            # Lọc results để chỉ giữ những face không bị duplicate
            filtered_results = []
            for r in results:
                if r['face_data'] in filtered_face_data:
                    filtered_results.append(r)
            
            return filtered_results
            
        except Exception as e:
            print(f"Error in detect_faces_with_encodings: {e}")
            return []
    
    def recognize_face(self, face_location):
        """Recognize a single face from face location data"""
        # This is a simplified version - in practice you'd extract the face from the location
        # For now, return a placeholder result
        if face_location and 'name' in face_location:
            return face_location.get('person_id', 'unknown'), face_location.get('confidence', 0.0)
        return 'unknown', 0.0