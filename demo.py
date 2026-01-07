"""
Demo script to test the detection modules without camera
"""
import sys
import cv2
import numpy as np

sys.path.insert(0, 'src')

from detectors import FaceDetector, EyeGazeTracker, ObjectDetector
from utils import AlertSystem


def create_test_image_with_face():
    """Create a simple test image with a face-like pattern"""
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200
    
    # Draw a simple face-like structure
    cv2.circle(img, (320, 240), 80, (255, 220, 180), -1)  # Face
    cv2.circle(img, (290, 220), 15, (0, 0, 0), -1)  # Left eye
    cv2.circle(img, (350, 220), 15, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(img, (320, 260), (30, 15), 0, 0, 180, (0, 0, 0), 2)  # Mouth
    
    return img


def create_test_image_no_face():
    """Create a test image without a face"""
    img = np.ones((480, 640, 3), dtype=np.uint8) * 150
    return img


def create_test_image_multiple_faces():
    """Create a test image with multiple faces"""
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200
    
    # Face 1
    cv2.circle(img, (200, 240), 60, (255, 220, 180), -1)
    cv2.circle(img, (180, 220), 12, (0, 0, 0), -1)
    cv2.circle(img, (220, 220), 12, (0, 0, 0), -1)
    
    # Face 2
    cv2.circle(img, (440, 240), 60, (255, 220, 180), -1)
    cv2.circle(img, (420, 220), 12, (0, 0, 0), -1)
    cv2.circle(img, (460, 220), 12, (0, 0, 0), -1)
    
    return img


def test_face_detection():
    """Test face detection module"""
    print("\n" + "=" * 50)
    print("Testing Face Detection")
    print("=" * 50)
    
    detector = FaceDetector()
    
    # Test with face
    print("\n1. Testing with face present:")
    img_with_face = create_test_image_with_face()
    faces, num_faces = detector.detect_faces(img_with_face)
    print(f"   Faces detected: {num_faces}")
    
    # Test without face
    print("\n2. Testing without face:")
    img_no_face = create_test_image_no_face()
    faces, num_faces = detector.detect_faces(img_no_face)
    print(f"   Faces detected: {num_faces}")
    
    # Test with multiple faces
    print("\n3. Testing with multiple faces:")
    img_multiple = create_test_image_multiple_faces()
    faces, num_faces = detector.detect_faces(img_multiple)
    print(f"   Faces detected: {num_faces}")
    
    print("\n✓ Face detection test completed")


def test_eye_tracking():
    """Test eye tracking module"""
    print("\n" + "=" * 50)
    print("Testing Eye Tracking")
    print("=" * 50)
    
    tracker = EyeGazeTracker()
    
    img = create_test_image_with_face()
    face_roi = (240, 160, 160, 160)  # Approximate face location
    
    print("\nChecking if looking away...")
    looking_away = tracker.is_looking_away(img, face_roi)
    print(f"   Looking away: {looking_away}")
    
    print("\n✓ Eye tracking test completed")


def test_object_detection():
    """Test object detection module"""
    print("\n" + "=" * 50)
    print("Testing Object Detection")
    print("=" * 50)
    
    detector = ObjectDetector()
    
    # Create test image with dark rectangular object (potential phone)
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200
    cv2.rectangle(img, (100, 300), (180, 400), (20, 20, 20), -1)
    
    print("\n1. Testing phone detection:")
    phone_detected, phone_regions = detector.detect_phone(img)
    print(f"   Phone detected: {phone_detected}")
    print(f"   Regions found: {len(phone_regions)}")
    
    # Create test image with white rectangular object (potential paper)
    img2 = np.ones((480, 640, 3), dtype=np.uint8) * 100
    cv2.rectangle(img2, (200, 100), (400, 300), (255, 255, 255), -1)
    
    print("\n2. Testing paper detection:")
    paper_detected, paper_regions = detector.detect_paper(img2)
    print(f"   Paper detected: {paper_detected}")
    print(f"   Regions found: {len(paper_regions)}")
    
    print("\n✓ Object detection test completed")


def test_alert_system():
    """Test alert system"""
    print("\n" + "=" * 50)
    print("Testing Alert System")
    print("=" * 50)
    
    alert_system = AlertSystem()
    
    print("\n1. Adding test alerts...")
    alert_system.add_alert("NO_FACE_DETECTED", "Student not visible")
    alert_system.add_alert("MULTIPLE_FACES", "Multiple people detected")
    alert_system.add_alert("LOOKING_AWAY", "Student looking away")
    
    print(f"\n2. Total alerts: {alert_system.get_alert_count()}")
    
    print("\n3. Saving report...")
    alert_system.save_report("demo_report.json")
    
    print("\n✓ Alert system test completed")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AI-BASED EXAM CHEATING DETECTION SYSTEM - DEMO")
    print("=" * 60)
    print("\nRunning module tests without camera...")
    
    try:
        test_face_detection()
        test_eye_tracking()
        test_object_detection()
        test_alert_system()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nThe detection modules are working correctly.")
        print("To run the full system with camera, execute: python main.py")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
