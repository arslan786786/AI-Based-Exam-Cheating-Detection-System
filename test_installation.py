#!/usr/bin/env python
"""
Quick test script to verify the installation
"""
import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_jwt_extended', 'Flask-JWT-Extended'),
        ('cv2', 'OpenCV'),
        ('mediapipe', 'MediaPipe'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('reportlab', 'ReportLab'),
        ('matplotlib', 'Matplotlib'),
        ('pandas', 'Pandas'),
    ]
    
    failed = []
    
    for module, name in packages:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name} - {e}")
            failed.append(name)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from backend.config.config import config
        print("✓ Configuration loaded")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_models():
    """Test database models"""
    print("\nTesting database models...")
    try:
        from backend.models.models import User, Exam, ExamSession, CheatingEvent, Alert
        print("✓ Database models loaded")
        return True
    except Exception as e:
        print(f"✗ Models error: {e}")
        return False

def test_services():
    """Test services"""
    print("\nTesting services...")
    try:
        from backend.services.face_detection import FaceDetectionService
        from backend.services.object_detection import ObjectDetectionService
        from backend.services.cheating_detection import CheatingDetectionService
        print("✓ Services loaded")
        return True
    except Exception as e:
        print(f"✗ Services error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("AI-Based Exam Cheating Detection System - Installation Test")
    print("="*60)
    
    tests = [
        test_imports,
        test_config,
        test_models,
        test_services,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*60)
    if all(results):
        print("✅ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Run: python init_db.py")
        print("2. Run: python backend/app.py")
        print("3. Open frontend/student.html in your browser")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1
    print("="*60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
