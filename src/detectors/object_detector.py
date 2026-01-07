"""
Object Detection Module
Detects suspicious objects like phones, books, notes
"""
import cv2
import numpy as np
from typing import List, Tuple


class ObjectDetector:
    def __init__(self):
        """Initialize object detector"""
        # For this implementation, we'll use simple color and shape detection
        # In a production system, you'd use YOLO or similar deep learning models
        pass
    
    def detect_phone(self, frame: np.ndarray) -> Tuple[bool, List]:
        """
        Detect phone-like objects using color and shape analysis
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (phone_detected: bool, detected_regions: List)
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define range for detecting dark rectangular objects (potential phones)
        lower_dark = np.array([0, 0, 0])
        upper_dark = np.array([180, 255, 50])
        
        mask = cv2.inRange(hsv, lower_dark, upper_dark)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_objects = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500 and area < 50000:  # Filter by size
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                # Phones typically have aspect ratio between 0.4 and 0.7
                if 0.4 < aspect_ratio < 0.7 or 1.4 < aspect_ratio < 2.5:
                    detected_objects.append((x, y, w, h))
        
        return len(detected_objects) > 0, detected_objects
    
    def detect_paper(self, frame: np.ndarray) -> Tuple[bool, List]:
        """
        Detect paper-like objects (white rectangular regions)
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (paper_detected: bool, detected_regions: List)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Threshold to find white regions
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_papers = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum paper size
                x, y, w, h = cv2.boundingRect(contour)
                detected_papers.append((x, y, w, h))
        
        return len(detected_papers) > 0, detected_papers
    
    def draw_objects(self, frame: np.ndarray, objects: List, label: str, color: Tuple) -> np.ndarray:
        """
        Draw bounding boxes around detected objects
        
        Args:
            frame: Input image frame
            objects: List of object coordinates
            label: Label for the objects
            color: Color for bounding box
            
        Returns:
            Frame with drawn bounding boxes
        """
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
