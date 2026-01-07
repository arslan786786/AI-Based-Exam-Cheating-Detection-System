# Detection Settings
FACE_DETECTION_CONFIDENCE = 0.5
HEAD_POSE_THRESHOLD = 30  # degrees
MULTIPLE_PERSON_ALERT = True
OBJECT_DETECTION_ENABLED = True

# Alert Settings
ALERT_COOLDOWN = 5  # seconds between alerts
SAVE_EVIDENCE = True
EVIDENCE_DIR = "evidence"

# Video Settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# Suspicious Activity Thresholds
MAX_NO_FACE_TIME = 5  # seconds
MAX_LOOKING_AWAY_TIME = 3  # seconds
MAX_MULTIPLE_FACES_TIME = 2  # seconds
