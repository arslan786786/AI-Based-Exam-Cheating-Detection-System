"""
Configuration settings for the application
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'exam_proctoring.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Webcam Configuration
    WEBCAM_FPS = 2  # Capture frames per second (1-5 FPS)
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    
    # Cheating Detection Thresholds
    HEAD_TURN_ANGLE_THRESHOLD = 30  # degrees
    HEAD_TURN_DURATION_THRESHOLD = 5  # seconds
    GAZE_DEVIATION_THRESHOLD = 0.3  # normalized value
    FACE_MISSING_THRESHOLD = 3  # seconds
    
    # Cheating Score Weights
    SCORE_NO_FACE = 30
    SCORE_MULTIPLE_FACES = 40
    SCORE_HEAD_MOVEMENT = 15
    SCORE_EYE_GAZE_DEVIATION = 10
    SCORE_MOBILE_PHONE = 50
    
    # Risk Levels
    RISK_LOW_THRESHOLD = 30
    RISK_MEDIUM_THRESHOLD = 60
    RISK_HIGH_THRESHOLD = 100
    
    # Storage Configuration
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'uploads')
    SNAPSHOTS_FOLDER = os.path.join(basedir, '..', 'snapshots')
    RECORDINGS_FOLDER = os.path.join(basedir, '..', 'recordings')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(SNAPSHOTS_FOLDER, exist_ok=True)
    os.makedirs(RECORDINGS_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
