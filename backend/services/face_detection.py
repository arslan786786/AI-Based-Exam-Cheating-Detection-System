"""
Face detection and recognition service using MediaPipe
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Tuple, Optional

class FaceDetectionService:
    """Service for detecting faces and analyzing facial features"""
    
    def __init__(self):
        """Initialize MediaPipe face detection and face mesh"""
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5
        )
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=5,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def detect_faces(self, frame: np.ndarray) -> Dict:
        """
        Detect faces in the frame
        
        Args:
            frame: Input image frame
            
        Returns:
            Dictionary with face count and detection results
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        face_count = 0
        detections = []
        
        if results.detections:
            face_count = len(results.detections)
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                detections.append({
                    'confidence': detection.score[0],
                    'bbox': {
                        'x': bbox.xmin,
                        'y': bbox.ymin,
                        'width': bbox.width,
                        'height': bbox.height
                    }
                })
        
        return {
            'face_count': face_count,
            'detections': detections,
            'status': 'ok' if face_count == 1 else ('no_face' if face_count == 0 else 'multiple_faces')
        }
    
    def get_face_landmarks(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Get facial landmarks for pose and gaze estimation
        
        Args:
            frame: Input image frame
            
        Returns:
            Face landmarks or None if no face detected
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]
        
        return None
    
    def estimate_head_pose(self, frame: np.ndarray) -> Dict:
        """
        Estimate head pose angles (yaw, pitch, roll)
        
        Args:
            frame: Input image frame
            
        Returns:
            Dictionary with head pose angles in degrees
        """
        landmarks = self.get_face_landmarks(frame)
        
        if landmarks is None:
            return {
                'yaw': 0,
                'pitch': 0,
                'roll': 0,
                'status': 'no_face'
            }
        
        # Get image dimensions
        h, w = frame.shape[:2]
        
        # Key facial landmarks for pose estimation
        # Nose tip, chin, left eye corner, right eye corner, left mouth corner, right mouth corner
        landmark_indices = [1, 152, 33, 263, 61, 291]
        
        # Extract 2D points
        image_points = np.array([
            [landmarks.landmark[idx].x * w, landmarks.landmark[idx].y * h]
            for idx in landmark_indices
        ], dtype=np.float64)
        
        # 3D model points (generic face model)
        model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye corner
            (225.0, 170.0, -135.0),      # Right eye corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])
        
        # Camera parameters
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        dist_coeffs = np.zeros((4, 1))
        
        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return {
                'yaw': 0,
                'pitch': 0,
                'roll': 0,
                'status': 'estimation_failed'
            }
        
        # Convert rotation vector to rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        
        # Calculate Euler angles
        sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
        singular = sy < 1e-6
        
        if not singular:
            pitch = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            yaw = np.arctan2(-rotation_matrix[2, 0], sy)
            roll = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            pitch = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            yaw = np.arctan2(-rotation_matrix[2, 0], sy)
            roll = 0
        
        # Convert to degrees
        pitch = np.degrees(pitch)
        yaw = np.degrees(yaw)
        roll = np.degrees(roll)
        
        return {
            'yaw': float(yaw),
            'pitch': float(pitch),
            'roll': float(roll),
            'status': 'ok'
        }
    
    def estimate_gaze_direction(self, frame: np.ndarray) -> Dict:
        """
        Estimate eye gaze direction
        
        Args:
            frame: Input image frame
            
        Returns:
            Dictionary with gaze information
        """
        landmarks = self.get_face_landmarks(frame)
        
        if landmarks is None:
            return {
                'gaze_x': 0,
                'gaze_y': 0,
                'looking_away': False,
                'status': 'no_face'
            }
        
        h, w = frame.shape[:2]
        
        # Eye landmarks
        # Left eye: indices around 33, 133
        # Right eye: indices around 362, 263
        left_eye_indices = [33, 133, 160, 159, 158, 157, 173]
        right_eye_indices = [362, 263, 387, 386, 385, 384, 398]
        
        # Calculate eye centers
        left_eye_center = np.mean([
            [landmarks.landmark[idx].x * w, landmarks.landmark[idx].y * h]
            for idx in left_eye_indices
        ], axis=0)
        
        right_eye_center = np.mean([
            [landmarks.landmark[idx].x * w, landmarks.landmark[idx].y * h]
            for idx in right_eye_indices
        ], axis=0)
        
        # Pupil approximation (using iris landmarks if available)
        # Check if iris landmarks exist (MediaPipe face mesh with iris refinement has 478 landmarks)
        if len(landmarks.landmark) > 473:
            left_iris = [landmarks.landmark[468].x * w, landmarks.landmark[468].y * h]
            right_iris = [landmarks.landmark[473].x * w, landmarks.landmark[473].y * h]
        else:
            # Fall back to eye center if iris landmarks not available
            left_iris = left_eye_center
            right_iris = right_eye_center
        
        # Calculate gaze deviation from center
        left_deviation = np.linalg.norm(left_iris - left_eye_center)
        right_deviation = np.linalg.norm(right_iris - right_eye_center)
        
        avg_deviation = (left_deviation + right_deviation) / 2
        
        # Normalize deviation (rough estimation)
        normalized_deviation = avg_deviation / (w * 0.05)
        
        # Calculate gaze direction (simplified)
        gaze_x = (left_iris[0] + right_iris[0]) / 2 - w / 2
        gaze_y = (left_iris[1] + right_iris[1]) / 2 - h / 2
        
        # Normalize to [-1, 1]
        gaze_x = gaze_x / (w / 2)
        gaze_y = gaze_y / (h / 2)
        
        # Determine if looking away (deviation threshold)
        looking_away = normalized_deviation > 0.3
        
        return {
            'gaze_x': float(gaze_x),
            'gaze_y': float(gaze_y),
            'deviation': float(normalized_deviation),
            'looking_away': looking_away,
            'status': 'ok'
        }
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'face_detection'):
            self.face_detection.close()
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
