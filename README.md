# AI-Based Exam Cheating Detection System

An intelligent real-time monitoring system that uses computer vision and AI to detect suspicious activities during online exams.

## Features

- **Face Detection**: Identifies and tracks student faces during exams
- **Multiple Person Detection**: Alerts when more than one person is detected in the frame
- **Eye Gaze Tracking**: Monitors if the student is looking away from the screen
- **Head Pose Estimation**: Detects unusual head movements
- **Object Detection**: Identifies suspicious objects like phones or notes
- **Real-time Alerts**: Generates immediate alerts for suspicious activities
- **Evidence Collection**: Automatically saves screenshots of suspicious activities
- **Detailed Reports**: Generates comprehensive JSON reports of all detected incidents

## System Requirements

- Python 3.7 or higher
- Webcam or camera device
- Operating Systems: Windows, macOS, or Linux

## Installation

1. Clone the repository:
```bash
git clone https://github.com/arslan786786/AI-Based-Exam-Cheating-Detection-System.git
cd AI-Based-Exam-Cheating-Detection-System
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the monitoring system:
```bash
python main.py
```

### Controls

- **Press 'q'**: Quit the application
- **Press 's'**: Save current report

### Configuration

Edit `config.py` to customize detection parameters:

```python
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
```

## Project Structure

```
AI-Based-Exam-Cheating-Detection-System/
├── main.py                          # Main application entry point
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── README.md                       # Documentation
├── src/
│   ├── detectors/
│   │   ├── face_detector.py       # Face detection module
│   │   ├── eye_tracker.py         # Eye gaze tracking module
│   │   ├── head_pose.py           # Head pose estimation module
│   │   └── object_detector.py     # Object detection module
│   └── utils/
│       ├── alert_system.py        # Alert management system
│       └── video_processor.py     # Video capture and processing
├── tests/                          # Unit tests
└── evidence/                       # Saved evidence screenshots
```

## Detection Capabilities

### 1. Face Detection
- Detects and tracks student faces in real-time
- Alerts when no face is detected for extended periods
- Uses OpenCV's Haar Cascade classifier

### 2. Multiple Person Detection
- Identifies when more than one person appears in the frame
- Helps prevent impersonation or unauthorized assistance

### 3. Eye Gaze Tracking
- Monitors eye movements to detect if student is looking away
- Useful for identifying potential cheating by looking at other screens or notes

### 4. Head Pose Estimation
- Tracks head orientation to detect unusual movements
- Alerts when head is turned significantly away from the screen

### 5. Object Detection
- Identifies suspicious objects like phones, books, or notes
- Uses color and shape analysis for real-time detection

## Alert System

The system generates alerts for the following suspicious activities:

- **NO_FACE_DETECTED**: Student not visible in frame
- **MULTIPLE_FACES**: Multiple people detected
- **LOOKING_AWAY**: Student looking away from screen
- **PHONE_DETECTED**: Phone or similar device detected

All alerts are:
- Timestamped
- Logged to console
- Saved to JSON report
- Accompanied by evidence screenshots (optional)

## Output

### Console Output
Real-time alerts are displayed in the console:
```
[ALERT] 14:23:45 - MULTIPLE_FACES: Multiple people detected (2 faces)
[ALERT] 14:24:12 - LOOKING_AWAY: Student looking away from screen
```

### Report Files
JSON reports are automatically generated:
```json
{
    "report_generated": "2026-01-07T14:30:00",
    "total_alerts": 5,
    "alerts": [
        {
            "timestamp": "2026-01-07T14:23:45",
            "type": "MULTIPLE_FACES",
            "description": "Multiple people detected (2 faces)",
            "evidence_file": "MULTIPLE_FACES_20260107_142345.jpg"
        }
    ]
}
```

### Evidence Screenshots
Screenshots are saved in the `evidence/` directory with timestamps.

## Customization

### Adjusting Sensitivity

- **Face Detection**: Modify `FACE_DETECTION_CONFIDENCE` (0.0-1.0)
- **Head Pose**: Change `HEAD_POSE_THRESHOLD` (degrees)

### Alert Cooldown

To prevent alert spam, adjust `ALERT_COOLDOWN` (seconds) in config.py.

### Camera Selection

If you have multiple cameras, change `CAMERA_INDEX` in config.py:
- 0: Default camera
- 1, 2, ...: Additional cameras

## Limitations

- Lighting conditions can affect detection accuracy
- Requires clear view of the student's face
- Object detection is basic and may need improvement for production use
- Performance depends on hardware capabilities

## Future Enhancements

- Deep learning-based object detection (YOLO, SSD)
- Audio analysis for suspicious sounds
- Integration with exam platforms (Moodle, Canvas, etc.)
- Cloud-based monitoring for multiple students
- Advanced facial recognition for identity verification
- Behavioral pattern analysis

## Troubleshooting

### Camera Not Working
- Check camera permissions
- Verify camera index in config.py
- Ensure no other application is using the camera

### Low FPS
- Reduce frame resolution in config.py
- Disable object detection if not needed
- Close other resource-intensive applications

### False Alerts
- Adjust detection thresholds in config.py
- Improve lighting conditions
- Ensure camera is properly positioned

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is open source and available under the MIT License.

## Disclaimer

This system is intended for educational purposes and legitimate exam monitoring with proper consent. Users must comply with privacy laws and obtain necessary permissions before deployment.

## Author

Developed for educational and research purposes to demonstrate AI applications in exam integrity.

## Acknowledgments

- OpenCV for computer vision capabilities
- Python community for excellent libraries
- Contributors and testers
