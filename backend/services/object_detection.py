"""
Object detection service for mobile phone detection using YOLO
"""
import cv2
import numpy as np
from typing import Dict, List
from ultralytics import YOLO

class ObjectDetectionService:
    """Service for detecting objects like mobile phones"""
    
    def __init__(self, model_path: str = 'yolov8n.pt'):
        """
        Initialize YOLO model for object detection
        
        Args:
            model_path: Path to YOLO model weights
        """
        try:
            self.model = YOLO(model_path)
            # Phone-related class IDs in COCO dataset
            # COCO class names: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml
            self.COCO_CELL_PHONE = 67  # cell phone
            self.COCO_LAPTOP = 77  # laptop (also suspicious during exam)
            self.phone_classes = [self.COCO_CELL_PHONE]
            self.suspicious_classes = [self.COCO_CELL_PHONE, self.COCO_LAPTOP]
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = None
    
    def detect_mobile_phone(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> Dict:
        """
        Detect mobile phones in the frame
        
        Args:
            frame: Input image frame
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            Dictionary with detection results
        """
        if self.model is None:
            return {
                'phone_detected': False,
                'phone_count': 0,
                'detections': [],
                'status': 'model_not_loaded'
            }
        
        try:
            # Run inference
            results = self.model(frame, verbose=False)
            
            phone_detections = []
            phone_count = 0
            
            # Process results
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Check if it's a phone and meets confidence threshold
                    if class_id in self.phone_classes and confidence >= confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        phone_detections.append({
                            'class_id': class_id,
                            'class_name': self.model.names[class_id],
                            'confidence': confidence,
                            'bbox': {
                                'x1': x1,
                                'y1': y1,
                                'x2': x2,
                                'y2': y2
                            }
                        })
                        phone_count += 1
            
            return {
                'phone_detected': phone_count > 0,
                'phone_count': phone_count,
                'detections': phone_detections,
                'status': 'ok'
            }
        
        except Exception as e:
            return {
                'phone_detected': False,
                'phone_count': 0,
                'detections': [],
                'status': f'error: {str(e)}'
            }
    
    def detect_suspicious_objects(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> Dict:
        """
        Detect any suspicious objects (phones, laptops, etc.)
        
        Args:
            frame: Input image frame
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            Dictionary with detection results
        """
        if self.model is None:
            return {
                'suspicious_detected': False,
                'object_count': 0,
                'detections': [],
                'status': 'model_not_loaded'
            }
        
        try:
            # Run inference
            results = self.model(frame, verbose=False)
            
            suspicious_detections = []
            object_count = 0
            
            # Process results
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Check if it's a suspicious object
                    if class_id in self.suspicious_classes and confidence >= confidence_threshold:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        suspicious_detections.append({
                            'class_id': class_id,
                            'class_name': self.model.names[class_id],
                            'confidence': confidence,
                            'bbox': {
                                'x1': x1,
                                'y1': y1,
                                'x2': x2,
                                'y2': y2
                            }
                        })
                        object_count += 1
            
            return {
                'suspicious_detected': object_count > 0,
                'object_count': object_count,
                'detections': suspicious_detections,
                'status': 'ok'
            }
        
        except Exception as e:
            return {
                'suspicious_detected': False,
                'object_count': 0,
                'detections': [],
                'status': f'error: {str(e)}'
            }
