import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Any, List

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
print("Hi")
class MediaPipeService:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a single frame and extract facial landmarks."""
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame with MediaPipe
        results = self.face_mesh.process(frame_rgb)
        
        if not results.multi_face_landmarks:
            return {"face_detected": False, "landmarks": []}
        
        # Extract landmarks
        landmarks = []
        for facial_landmarks in results.multi_face_landmarks:
            for i, landmark in enumerate(facial_landmarks.landmark):
                landmarks.append({
                    "id": i,
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z
                })
        
        return {
            "face_detected": True,
            "landmarks": landmarks
        }
    
    def analyze_expression(self, landmarks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze facial expression based on landmarks."""
        # Simplified expression analysis
        # In a real implementation, this would be much more sophisticated
        if not landmarks:
            return {
                "neutral": 0.0,
                "happy": 0.0,
                "surprised": 0.0,
                "angry": 0.0
            }
        
        # Placeholder for expression analysis
        # This is a simplified mock implementation
        # Real implementation would use the landmarks to calculate expressions
        return {
            "neutral": 0.7,
            "happy": 0.2,
            "surprised": 0.05,
            "angry": 0.05
        }