import os
import cv2
import face_recognition
import numpy as np
from pathlib import Path
import pickle
import time
from datetime import datetime

from ...core.config import FACES_DIR, FACE_RECOGNITION_TOLERANCE, FACE_RECOGNITION_MODEL
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

        # Get face encoding
        face_encodings = face_recognition.face_encodings(face_image)

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
        cv2.imwrite(str(image_path), cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR))
        
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
            # See if the face is a match for the known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, 
                                                   tolerance=FACE_RECOGNITION_TOLERANCE)
            
            name = "Unknown"
            person_id = "unknown"
            confidence = 0.0
            
            # If we found a match
            if True in matches:
                # Find the indexes of all matched faces then compute distances
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    confidence = 1.0 - face_distances[best_match_index]
                    name = self.known_face_names[best_match_index]
                    person_id = self.known_face_ids[best_match_index]
            
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
        
        return results
    
    def detect_faces(self, frame):
        """Detect and recognize faces in frame, return list of detected faces"""
        return self.recognize_faces(frame)
    
    def recognize_face(self, face_location):
        """Recognize a single face from face location data"""
        # This is a simplified version - in practice you'd extract the face from the location
        # For now, return a placeholder result
        if face_location and 'name' in face_location:
            return face_location.get('person_id', 'unknown'), face_location.get('confidence', 0.0)
        return 'unknown', 0.0