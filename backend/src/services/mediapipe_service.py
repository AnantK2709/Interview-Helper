import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Any, List, Tuple
import base64

class MediaPipeService:
    def __init__(self):
        # Initialize face mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize pose detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize holistic model for combined analysis
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize drawing utilities
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Key facial landmark indices for various expressions
        self.expression_landmarks = {
            "eyebrows": [65, 105, 107, 336, 374],  # Eyebrow landmarks
            "mouth": [0, 17, 61, 291, 306, 375],   # Mouth landmarks
            "eyes": [159, 145, 386, 374]           # Eye landmarks
        }
    
    def decode_image(self, base64_string: str) -> np.ndarray:
        """Decode base64 image string to OpenCV format."""
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        image_bytes = base64.b64decode(base64_string)
        np_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return img
    
    def analyze_frame(self, frame_base64: str) -> Dict[str, Any]:
        """Process a frame from base64 string and return analysis."""
        frame = self.decode_image(frame_base64)
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        face_results = self.face_mesh.process(frame_rgb)
        pose_results = self.pose.process(frame_rgb)
        holistic_results = self.holistic.process(frame_rgb)
        
        # Initialize results
        results = {
            "face_detected": False,
            "facial_expression": None,
            "posture": None,
            "eye_contact": None,
            "hand_gestures": None,
            "confidence_score": None
        }
        
        # Analyze facial expression if face detected
        if face_results.multi_face_landmarks:
            results["face_detected"] = True
            facial_landmarks = self.extract_facial_landmarks(face_results.multi_face_landmarks[0])
            results["facial_expression"] = self.analyze_expression(facial_landmarks)
            results["eye_contact"] = self.analyze_eye_contact(facial_landmarks)
        
        # Analyze posture if pose detected
        if pose_results.pose_landmarks:
            results["posture"] = self.analyze_posture(pose_results.pose_landmarks)
        
        # Analyze hand gestures if detected
        if holistic_results.left_hand_landmarks or holistic_results.right_hand_landmarks:
            results["hand_gestures"] = self.analyze_hand_gestures(
                holistic_results.left_hand_landmarks, 
                holistic_results.right_hand_landmarks
            )
        
        # Calculate overall confidence score
        results["confidence_score"] = self.calculate_confidence_score(results)
        
        return results
    
    def extract_facial_landmarks(self, landmarks) -> Dict[str, List[Tuple[float, float]]]:
        """Extract key facial landmarks for expression analysis."""
        facial_landmarks = {}
        
        for region, indices in self.expression_landmarks.items():
            facial_landmarks[region] = []
            for idx in indices:
                landmark = landmarks.landmark[idx]
                facial_landmarks[region].append((landmark.x, landmark.y))
        
        return facial_landmarks
    
    def analyze_expression(self, landmarks: Dict[str, List[Tuple[float, float]]]) -> Dict[str, Any]:
        """Analyze facial expression based on landmarks."""
        # Calculate eyebrow position relative to eyes
        eyebrow_heights = [landmark[1] for landmark in landmarks["eyebrows"]]
        eye_heights = [landmark[1] for landmark in landmarks["eyes"]]
        
        avg_eyebrow_height = sum(eyebrow_heights) / len(eyebrow_heights)
        avg_eye_height = sum(eye_heights) / len(eye_heights)
        
        eyebrow_eye_distance = avg_eye_height - avg_eyebrow_height
        
        # Calculate mouth openness
        mouth_top = min([landmark[1] for landmark in landmarks["mouth"]])
        mouth_bottom = max([landmark[1] for landmark in landmarks["mouth"]])
        mouth_openness = mouth_bottom - mouth_top
        
        # Simplified expression classification
        expressions = {
            "neutral": 0.5,
            "happy": 0.0,
            "surprised": 0.0,
            "concerned": 0.0,
            "engaged": 0.0
        }
        
        # Adjust based on features
        # High eyebrows + open mouth = surprised
        if eyebrow_eye_distance > 0.03 and mouth_openness > 0.05:
            expressions["surprised"] = 0.7
            expressions["neutral"] = 0.2
        # Raised eyebrows + closed mouth = concerned/thinking
        elif eyebrow_eye_distance > 0.03 and mouth_openness < 0.03:
            expressions["concerned"] = 0.6
            expressions["neutral"] = 0.3
        # Normal eyebrows + wide mouth = happy
        elif eyebrow_eye_distance < 0.03 and mouth_openness > 0.04:
            expressions["happy"] = 0.8
            expressions["neutral"] = 0.2
        # Slight eyebrow raise + moderate mouth = engaged
        elif 0.02 < eyebrow_eye_distance < 0.03 and 0.02 < mouth_openness < 0.04:
            expressions["engaged"] = 0.7
            expressions["neutral"] = 0.3
        # Default is more neutral
        else:
            expressions["neutral"] = 0.8
        
        # Find the dominant expression
        dominant_expression = max(expressions.items(), key=lambda x: x[1])
        
        return {
            "dominant": dominant_expression[0],
            "confidence": dominant_expression[1],
            "all_expressions": expressions
        }
    
    def analyze_eye_contact(self, landmarks: Dict[str, List[Tuple[float, float]]]) -> Dict[str, Any]:
        """Analyze eye contact based on eye landmarks."""
        # Calculate eye positions
        left_eye = landmarks["eyes"][0:2]
        right_eye = landmarks["eyes"][2:4]
        
        # Calculate center position of both eyes
        left_eye_center = (sum(p[0] for p in left_eye) / len(left_eye), 
                          sum(p[1] for p in left_eye) / len(left_eye))
        right_eye_center = (sum(p[0] for p in right_eye) / len(right_eye), 
                           sum(p[1] for p in right_eye) / len(right_eye))
        
        # Horizontal eye position (0.5 is center of image)
        eye_x_position = (left_eye_center[0] + right_eye_center[0]) / 2
        
        # Determine if looking at camera (simplified)
        looking_at_camera = 0.4 < eye_x_position < 0.6
        
        return {
            "looking_at_camera": looking_at_camera,
            "confidence": 0.7 if looking_at_camera else 0.6,
            "position": "center" if looking_at_camera else ("left" if eye_x_position <= 0.4 else "right"),
            "duration": None  # This would be tracked over time in a real implementation
        }
    
    def analyze_posture(self, pose_landmarks) -> Dict[str, Any]:
        """Analyze posture based on body landmarks."""
        # Extract shoulder landmarks
        left_shoulder = (pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y)
        right_shoulder = (pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                         pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y)
        
        # Extract hip landmarks
        left_hip = (pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP.value].y)
        right_hip = (pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                    pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y)
        
        # Extract nose landmark for head position
        nose = (pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE.value].x,
               pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE.value].y)
        
        # Calculate shoulder slope (measure of slouching)
        shoulder_slope = abs(left_shoulder[1] - right_shoulder[1])
        
        # Calculate spine angle
        # First get midpoints of shoulders and hips
        shoulder_midpoint = ((left_shoulder[0] + right_shoulder[0]) / 2,
                            (left_shoulder[1] + right_shoulder[1]) / 2)
        hip_midpoint = ((left_hip[0] + right_hip[0]) / 2,
                       (left_hip[1] + right_hip[1]) / 2)
        
        # Calculate spine angle with vertical
        spine_vector = (hip_midpoint[0] - shoulder_midpoint[0], 
                       hip_midpoint[1] - shoulder_midpoint[1])
        vertical_vector = (0, 1)
        
        # Normalize vectors
        spine_magnitude = np.sqrt(spine_vector[0]**2 + spine_vector[1]**2)
        if spine_magnitude == 0:
            spine_vector = (0, 0)
        else:
            spine_vector = (spine_vector[0]/spine_magnitude, spine_vector[1]/spine_magnitude)
        
        # Calculate angle (dot product)
        dot_product = spine_vector[0] * vertical_vector[0] + spine_vector[1] * vertical_vector[1]
        angle = np.arccos(np.clip(dot_product, -1.0, 1.0)) * 180 / np.pi
        
        # Analyze posture based on these metrics
        posture_quality = "good"
        confidence = 0.7
        issues = []
        
        if shoulder_slope > 0.03:
            posture_quality = "poor"
            issues.append("uneven shoulders")
            confidence = 0.8
        
        if angle > 10:
            posture_quality = "poor"
            issues.append("leaning")
            confidence = 0.8
        
        # Check if head is too far forward
        head_forward = nose[0] < shoulder_midpoint[0] - 0.05
        if head_forward:
            posture_quality = "poor"
            issues.append("head forward")
            confidence = 0.8
        
        return {
            "quality": posture_quality,
            "confidence": confidence,
            "issues": issues,
            "metrics": {
                "shoulder_slope": float(shoulder_slope),
                "spine_angle": float(angle)
            }
        }
    
    def analyze_hand_gestures(self, left_hand_landmarks, right_hand_landmarks) -> Dict[str, Any]:
        """Analyze hand gestures based on hand landmarks."""
        # Initialize result
        result = {
            "left_hand_visible": left_hand_landmarks is not None,
            "right_hand_visible": right_hand_landmarks is not None,
            "gesture_type": "none",
            "intensity": 0.0,
            "confidence": 0.0
        }
        
        if not result["left_hand_visible"] and not result["right_hand_visible"]:
            return result
        
        # Count visible hands
        visible_hands = sum([result["left_hand_visible"], result["right_hand_visible"]])
        
        # Use a simple heuristic for gesture analysis
        # In a real application, this would be much more sophisticated
        if visible_hands == 2:
            result["gesture_type"] = "expressive"
            result["intensity"] = 0.8
            result["confidence"] = 0.7
        else:
            result["gesture_type"] = "subtle"
            result["intensity"] = 0.4
            result["confidence"] = 0.6
        
        return result
    
    def calculate_confidence_score(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate an overall confidence score based on all analysis results."""
        # Start with a base score
        base_score = 60
        
        # Adjust based on facial expression
        if analysis_results["facial_expression"]:
            expression = analysis_results["facial_expression"]["dominant"]
            if expression == "engaged":
                base_score += 15
            elif expression == "happy":
                base_score += 10
            elif expression == "neutral":
                base_score += 5
            elif expression == "concerned":
                base_score -= 5
        
        # Adjust based on eye contact
        if analysis_results["eye_contact"]:
            if analysis_results["eye_contact"]["looking_at_camera"]:
                base_score += 15
            else:
                base_score -= 10
        
        # Adjust based on posture
        if analysis_results["posture"]:
            if analysis_results["posture"]["quality"] == "good":
                base_score += 10
            else:
                base_score -= 10
                # Additional penalty for each posture issue
                base_score -= 5 * len(analysis_results["posture"]["issues"])
        
        # Adjust based on hand gestures
        if analysis_results["hand_gestures"]:
            if analysis_results["hand_gestures"]["gesture_type"] == "expressive":
                base_score += 5 * analysis_results["hand_gestures"]["intensity"]
        
        # Ensure the score is within 0-100 range
        final_score = max(0, min(100, base_score))
        
        # Determine confidence level based on score
        if final_score >= 80:
            confidence_level = "high"
        elif final_score >= 60:
            confidence_level = "moderate"
        else:
            confidence_level = "low"
        
        return {
            "score": final_score,
            "level": confidence_level,
            "areas_for_improvement": self.identify_improvement_areas(analysis_results)
        }
    
    def identify_improvement_areas(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement based on analysis results."""
        improvements = []
        
        # Check facial expression
        if analysis_results["facial_expression"]:
            expression = analysis_results["facial_expression"]["dominant"]
            if expression in ["neutral", "concerned"]:
                improvements.append("Show more engagement through facial expressions")
        
        # Check eye contact
        if analysis_results["eye_contact"] and not analysis_results["eye_contact"]["looking_at_camera"]:
            improvements.append("Maintain better eye contact")
        
        # Check posture
        if analysis_results["posture"] and analysis_results["posture"]["quality"] == "poor":
            for issue in analysis_results["posture"]["issues"]:
                if issue == "uneven shoulders":
                    improvements.append("Keep shoulders level")
                elif issue == "leaning":
                    improvements.append("Maintain upright posture")
                elif issue == "head forward":
                    improvements.append("Keep head aligned with shoulders")
        
        # Check hand gestures
        if analysis_results["hand_gestures"]:
            if analysis_results["hand_gestures"]["gesture_type"] == "none":
                improvements.append("Use more hand gestures to emphasize points")
            elif analysis_results["hand_gestures"]["intensity"] > 0.8:
                improvements.append("Reduce excessive hand movements")
        
        return improvements
    
    def annotate_image(self, frame_base64: str) -> str:
        """Process a frame and annotate it with detected landmarks."""
        frame = self.decode_image(frame_base64)
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with holistic model to get all landmarks
        holistic_results = self.holistic.process(frame_rgb)
        
        # Convert back to BGR for OpenCV
        annotated_frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        # Draw face landmarks
        if holistic_results.face_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                holistic_results.face_landmarks,
                self.mp_holistic.FACEMESH_CONTOURS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
            )
        
        # Draw pose landmarks
        if holistic_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                holistic_results.pose_landmarks,
                self.mp_holistic.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        
        # Draw hand landmarks
        if holistic_results.left_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                holistic_results.left_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
        
        if holistic_results.right_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                holistic_results.right_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
        
        # Convert back to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{annotated_base64}"