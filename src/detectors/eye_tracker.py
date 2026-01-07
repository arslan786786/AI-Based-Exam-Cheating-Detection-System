"""
Eye Gaze Tracking Module
Detects eye movements and determines if student is looking away
"""
import cv2
import numpy as np
from typing import Tuple, Optional


class EyeGazeTracker:
    def __init__(self, ear_threshold=0.25):
        """
        Initialize eye gaze tracker
        
        Args:
            ear_threshold: Eye aspect ratio threshold for blink detection
        """
        self.ear_threshold = ear_threshold
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
    def calculate_eye_aspect_ratio(self, eye_points: np.ndarray) -> float:
        """
        Calculate eye aspect ratio (EAR) for blink detection
        
        Args:
            eye_points: Eye landmark points
            
        Returns:
            Eye aspect ratio value
        """
        # Compute euclidean distances between vertical eye landmarks
        vertical_1 = np.linalg.norm(eye_points[1] - eye_points[5])
        vertical_2 = np.linalg.norm(eye_points[2] - eye_points[4])
        
        # Compute euclidean distance between horizontal eye landmarks
        horizontal = np.linalg.norm(eye_points[0] - eye_points[3])
        
        # Calculate EAR
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        
        return ear
    
    def detect_eyes(self, frame: np.ndarray, face_roi: Tuple) -> Tuple[bool, int]:
        """
        Detect eyes in the face region
        
        Args:
            frame: Input image frame
            face_roi: Region of interest containing the face (x, y, w, h)
            
        Returns:
            Tuple of (eyes_detected: bool, num_eyes: int)
        """
        x, y, w, h = face_roi
        face_region = frame[y:y+h, x:x+w]
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        # Detect eyes in face region
        eyes = self.eye_cascade.detectMultiScale(
            gray_face,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20)
        )
        
        num_eyes = len(eyes)
        eyes_detected = num_eyes >= 1
        
        return eyes_detected, num_eyes
    
    def draw_eyes(self, frame: np.ndarray, face_roi: Tuple, eyes) -> np.ndarray:
        """
        Draw rectangles around detected eyes
        
        Args:
            frame: Input image frame
            face_roi: Face region of interest
            eyes: Detected eye coordinates
            
        Returns:
            Frame with eye bounding boxes
        """
        x, y, w, h = face_roi
        
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 0, 0), 2)
        
        return frame
    
    def is_looking_away(self, frame: np.ndarray, face_roi: Tuple) -> bool:
        """
        Determine if the person is looking away from the screen
        
        Args:
            frame: Input image frame
            face_roi: Face region of interest
            
        Returns:
            True if looking away, False otherwise
        """
        eyes_detected, num_eyes = self.detect_eyes(frame, face_roi)
        
        # If less than 1 eye detected, likely looking away
        return not eyes_detected or num_eyes < 1
