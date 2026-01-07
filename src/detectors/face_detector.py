"""
Face Detection Module
Detects faces in video frames and tracks face count
"""
import cv2
import numpy as np
from typing import List, Tuple


class FaceDetector:
    def __init__(self, confidence_threshold=0.5):
        """
        Initialize face detector using OpenCV's DNN face detector
        
        Args:
            confidence_threshold: Minimum confidence for face detection
        """
        self.confidence_threshold = confidence_threshold
        
        # Load face detection model
        # Using OpenCV's pre-trained face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
    def detect_faces(self, frame: np.ndarray) -> Tuple[List, int]:
        """
        Detect faces in a frame
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (list of face coordinates, number of faces)
        """
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return faces, len(faces)
    
    def draw_faces(self, frame: np.ndarray, faces: List) -> np.ndarray:
        """
        Draw bounding boxes around detected faces
        
        Args:
            frame: Input image frame
            faces: List of face coordinates
            
        Returns:
            Frame with drawn bounding boxes
        """
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Face", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
