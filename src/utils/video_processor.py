"""
Video Processor Module
Handles video capture and frame processing
"""
import cv2
import numpy as np
from typing import Optional


class VideoProcessor:
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Initialize video processor
        
        Args:
            camera_index: Camera device index
            width: Frame width
            height: Frame height
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        
    def start(self) -> bool:
        """
        Start video capture
        
        Returns:
            True if successful, False otherwise
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}")
            return False
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        return True
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read a frame from the video capture
        
        Returns:
            Frame if successful, None otherwise
        """
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            return None
        
        return frame
    
    def release(self):
        """Release video capture resources"""
        if self.cap is not None:
            self.cap.release()
    
    def is_opened(self) -> bool:
        """
        Check if video capture is open
        
        Returns:
            True if open, False otherwise
        """
        return self.cap is not None and self.cap.isOpened()
