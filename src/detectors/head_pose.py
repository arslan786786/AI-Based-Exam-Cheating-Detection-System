"""
Head Pose Estimation Module
Estimates head pose to detect if student is looking away
"""
import cv2
import numpy as np
from typing import Tuple, Optional


class HeadPoseEstimator:
    def __init__(self):
        """Initialize head pose estimator"""
        # 3D model points of a generic face
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float64)
        
    def estimate_pose(self, frame: np.ndarray, face_landmarks) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Estimate head pose from facial landmarks
        
        Args:
            frame: Input image frame
            face_landmarks: Facial landmark points
            
        Returns:
            Tuple of (rotation_vector, translation_vector)
        """
        if face_landmarks is None or len(face_landmarks) < 6:
            return None, None
        
        size = frame.shape
        
        # Camera internals
        focal_length = size[1]
        center = (size[1] / 2, size[0] / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        
        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points,
            face_landmarks,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return None, None
        
        return rotation_vector, translation_vector
    
    def get_euler_angles(self, rotation_vector: np.ndarray) -> Tuple[float, float, float]:
        """
        Convert rotation vector to Euler angles
        
        Args:
            rotation_vector: Rotation vector from pose estimation
            
        Returns:
            Tuple of (pitch, yaw, roll) in degrees
        """
        rotation_mat, _ = cv2.Rodrigues(rotation_vector)
        
        # Calculate Euler angles
        sy = np.sqrt(rotation_mat[0, 0] ** 2 + rotation_mat[1, 0] ** 2)
        
        singular = sy < 1e-6
        
        if not singular:
            pitch = np.arctan2(rotation_mat[2, 1], rotation_mat[2, 2])
            yaw = np.arctan2(-rotation_mat[2, 0], sy)
            roll = np.arctan2(rotation_mat[1, 0], rotation_mat[0, 0])
        else:
            pitch = np.arctan2(-rotation_mat[1, 2], rotation_mat[1, 1])
            yaw = np.arctan2(-rotation_mat[2, 0], sy)
            roll = 0
        
        # Convert to degrees
        pitch = np.degrees(pitch)
        yaw = np.degrees(yaw)
        roll = np.degrees(roll)
        
        return pitch, yaw, roll
    
    def is_head_turned(self, rotation_vector: np.ndarray, threshold: float = 30.0) -> bool:
        """
        Check if head is turned away from the camera
        
        Args:
            rotation_vector: Rotation vector from pose estimation
            threshold: Angle threshold in degrees
            
        Returns:
            True if head is turned away, False otherwise
        """
        if rotation_vector is None:
            return False
        
        pitch, yaw, roll = self.get_euler_angles(rotation_vector)
        
        # Check if head is turned significantly
        return abs(yaw) > threshold or abs(pitch) > threshold
