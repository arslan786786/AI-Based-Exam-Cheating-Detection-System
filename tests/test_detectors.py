"""
Unit tests for the AI-Based Exam Cheating Detection System
"""
import unittest
import sys
import numpy as np
import cv2

sys.path.insert(0, 'src')

from detectors import FaceDetector, EyeGazeTracker, ObjectDetector
from utils import AlertSystem, VideoProcessor


class TestFaceDetector(unittest.TestCase):
    """Test cases for FaceDetector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = FaceDetector()
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertIsNotNone(self.detector.face_cascade)
    
    def test_detect_faces_with_empty_frame(self):
        """Test face detection with empty frame"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        faces, num_faces = self.detector.detect_faces(frame)
        self.assertIsInstance(num_faces, int)
        self.assertGreaterEqual(num_faces, 0)
    
    def test_draw_faces(self):
        """Test drawing faces on frame"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = [(100, 100, 80, 80)]
        result = self.detector.draw_faces(frame, faces)
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, frame.shape)


class TestEyeGazeTracker(unittest.TestCase):
    """Test cases for EyeGazeTracker"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = EyeGazeTracker()
    
    def test_initialization(self):
        """Test tracker initialization"""
        self.assertIsNotNone(self.tracker)
        self.assertIsNotNone(self.tracker.eye_cascade)
    
    def test_detect_eyes(self):
        """Test eye detection"""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
        face_roi = (200, 150, 240, 180)
        eyes_detected, num_eyes = self.tracker.detect_eyes(frame, face_roi)
        self.assertIsInstance(eyes_detected, bool)
        self.assertIsInstance(num_eyes, int)
        self.assertGreaterEqual(num_eyes, 0)
    
    def test_is_looking_away(self):
        """Test looking away detection"""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
        face_roi = (200, 150, 240, 180)
        result = self.tracker.is_looking_away(frame, face_roi)
        self.assertIsInstance(result, bool)


class TestObjectDetector(unittest.TestCase):
    """Test cases for ObjectDetector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = ObjectDetector()
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector)
    
    def test_detect_phone(self):
        """Test phone detection"""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
        phone_detected, regions = self.detector.detect_phone(frame)
        self.assertIsInstance(phone_detected, bool)
        self.assertIsInstance(regions, list)
    
    def test_detect_paper(self):
        """Test paper detection"""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 100
        paper_detected, regions = self.detector.detect_paper(frame)
        self.assertIsInstance(paper_detected, bool)
        self.assertIsInstance(regions, list)
    
    def test_draw_objects(self):
        """Test drawing objects on frame"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        objects = [(100, 100, 50, 80)]
        result = self.detector.draw_objects(frame, objects, "Test", (255, 0, 0))
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, frame.shape)


class TestAlertSystem(unittest.TestCase):
    """Test cases for AlertSystem"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.alert_system = AlertSystem()
    
    def test_initialization(self):
        """Test alert system initialization"""
        self.assertIsNotNone(self.alert_system)
        self.assertEqual(self.alert_system.get_alert_count(), 0)
    
    def test_add_alert(self):
        """Test adding alerts"""
        self.alert_system.add_alert("TEST_ALERT", "Test description")
        self.assertEqual(self.alert_system.get_alert_count(), 1)
    
    def test_get_alerts(self):
        """Test getting alerts"""
        self.alert_system.add_alert("TEST_ALERT", "Test description")
        alerts = self.alert_system.get_alerts()
        self.assertIsInstance(alerts, list)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['type'], "TEST_ALERT")
    
    def test_clear_alerts(self):
        """Test clearing alerts"""
        self.alert_system.add_alert("TEST_ALERT", "Test description")
        self.alert_system.clear_alerts()
        self.assertEqual(self.alert_system.get_alert_count(), 0)


class TestVideoProcessor(unittest.TestCase):
    """Test cases for VideoProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = VideoProcessor(0, 640, 480)
    
    def test_initialization(self):
        """Test video processor initialization"""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.camera_index, 0)
        self.assertEqual(self.processor.width, 640)
        self.assertEqual(self.processor.height, 480)
    
    def test_release(self):
        """Test releasing video capture"""
        # This should not raise any exceptions
        self.processor.release()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
