"""
AI-Based Exam Cheating Detection System
Main monitoring application with real-time detection
"""
import cv2
import sys
import time
import numpy as np
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

import config
from detectors import FaceDetector, EyeGazeTracker, HeadPoseEstimator, ObjectDetector
from utils import AlertSystem, VideoProcessor


class ExamMonitor:
    def __init__(self):
        """Initialize exam monitoring system"""
        print("Initializing AI-Based Exam Cheating Detection System...")
        
        # Initialize detectors
        self.face_detector = FaceDetector(config.FACE_DETECTION_CONFIDENCE)
        self.eye_tracker = EyeGazeTracker(config.EYE_ASPECT_RATIO_THRESHOLD)
        self.head_pose_estimator = HeadPoseEstimator()
        self.object_detector = ObjectDetector()
        
        # Initialize utilities
        self.alert_system = AlertSystem()
        self.video_processor = VideoProcessor(
            config.CAMERA_INDEX,
            config.FRAME_WIDTH,
            config.FRAME_HEIGHT
        )
        
        # Tracking variables
        self.no_face_start_time = None
        self.looking_away_start_time = None
        self.multiple_faces_start_time = None
        
        print("System initialized successfully!")
    
    def check_suspicious_activity(self, frame: np.ndarray, faces, num_faces: int):
        """
        Check for suspicious activities
        
        Args:
            frame: Current video frame
            faces: Detected faces
            num_faces: Number of detected faces
        """
        current_time = time.time()
        
        # Check for no face detected
        if num_faces == 0:
            if self.no_face_start_time is None:
                self.no_face_start_time = current_time
            elif current_time - self.no_face_start_time > config.MAX_NO_FACE_TIME:
                self.alert_system.add_alert(
                    "NO_FACE_DETECTED",
                    "Student not visible in frame",
                    frame
                )
                self.no_face_start_time = current_time
        else:
            self.no_face_start_time = None
        
        # Check for multiple faces
        if num_faces > 1:
            if self.multiple_faces_start_time is None:
                self.multiple_faces_start_time = current_time
            elif current_time - self.multiple_faces_start_time > config.MAX_MULTIPLE_FACES_TIME:
                self.alert_system.add_alert(
                    "MULTIPLE_FACES",
                    f"Multiple people detected ({num_faces} faces)",
                    frame
                )
                self.multiple_faces_start_time = current_time
        else:
            self.multiple_faces_start_time = None
        
        # Check for looking away (only if one face detected)
        if num_faces == 1:
            face_roi = faces[0]
            if self.eye_tracker.is_looking_away(frame, face_roi):
                if self.looking_away_start_time is None:
                    self.looking_away_start_time = current_time
                elif current_time - self.looking_away_start_time > config.MAX_LOOKING_AWAY_TIME:
                    self.alert_system.add_alert(
                        "LOOKING_AWAY",
                        "Student looking away from screen",
                        frame
                    )
                    self.looking_away_start_time = current_time
            else:
                self.looking_away_start_time = None
        
        # Check for suspicious objects
        if config.OBJECT_DETECTION_ENABLED:
            phone_detected, phone_regions = self.object_detector.detect_phone(frame)
            if phone_detected:
                self.alert_system.add_alert(
                    "PHONE_DETECTED",
                    "Suspicious phone-like object detected",
                    frame
                )
    
    def draw_info(self, frame: np.ndarray, num_faces: int, fps: float):
        """
        Draw information overlay on frame
        
        Args:
            frame: Video frame
            num_faces: Number of detected faces
            fps: Current FPS
        """
        # Draw semi-transparent overlay for info
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Draw information
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"Exam Monitor - {timestamp}", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Faces: {num_faces}", (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(frame, f"Alerts: {self.alert_system.get_alert_count()}", (150, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(frame, f"FPS: {fps:.1f}", (300, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Status indicator
        status_color = (0, 255, 0) if num_faces == 1 else (0, 0, 255)
        status_text = "NORMAL" if num_faces == 1 else "ALERT"
        cv2.putText(frame, f"Status: {status_text}", (450, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
        
        return frame
    
    def run(self):
        """Run the monitoring system"""
        print("\nStarting exam monitoring...")
        print("Press 'q' to quit")
        print("Press 's' to save report")
        print("-" * 50)
        
        # Start video capture
        if not self.video_processor.start():
            print("Failed to start video capture!")
            return
        
        # FPS calculation
        fps = 0
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                # Read frame
                frame = self.video_processor.read_frame()
                
                if frame is None:
                    print("Failed to read frame")
                    break
                
                # Detect faces
                faces, num_faces = self.face_detector.detect_faces(frame)
                
                # Draw face bounding boxes
                frame = self.face_detector.draw_faces(frame, faces)
                
                # Check for suspicious activity
                self.check_suspicious_activity(frame, faces, num_faces)
                
                # Calculate FPS
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time
                
                # Draw information overlay
                frame = self.draw_info(frame, num_faces, fps)
                
                # Display frame
                cv2.imshow('AI Exam Cheating Detection', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\nQuitting...")
                    break
                elif key == ord('s'):
                    print("\nSaving report...")
                    self.alert_system.save_report()
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            # Cleanup
            self.video_processor.release()
            cv2.destroyAllWindows()
            
            # Print summary
            print("\n" + "=" * 50)
            print("MONITORING SESSION SUMMARY")
            print("=" * 50)
            print(f"Total alerts: {self.alert_system.get_alert_count()}")
            print(f"Session duration: {time.time() - start_time:.1f} seconds")
            
            # Save final report
            self.alert_system.save_report()
            print("\nThank you for using AI-Based Exam Cheating Detection System")


def main():
    """Main entry point"""
    print("=" * 60)
    print("AI-BASED EXAM CHEATING DETECTION SYSTEM")
    print("=" * 60)
    print()
    
    monitor = ExamMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
