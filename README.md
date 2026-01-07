# 🎓 AI-Based Exam Cheating Detection System

A comprehensive real-time proctoring system that uses AI and computer vision to detect cheating behavior during online exams.

## 🌟 Features

### 👨‍🎓 Student Features
- **Webcam Monitoring**: Real-time video capture during exam
- **Live Feedback**: Instant notifications about suspicious behavior
- **Session Tracking**: Track exam duration and status

### 👩‍🏫 Invigilator/Faculty Features
- **Live Monitoring Dashboard**: Monitor all active exam sessions in real-time
- **Alert System**: Receive instant alerts for suspicious activities
- **Risk Assessment**: Color-coded risk levels (Low, Medium, High)
- **Event Timeline**: View detailed timeline of all detection events

### 🧑‍💼 Admin Features
- **User Management**: Create and manage students, faculty, and admin accounts
- **Exam Configuration**: Create and configure exams with custom settings
- **Analytics Dashboard**: View comprehensive statistics and reports
- **Report Generation**: Export detailed reports in PDF and CSV formats

## 🤖 AI Detection Capabilities

### Face Detection & Recognition (Section 4.3)
- ✅ Detect presence of face
- ✅ Ensure single face in frame
- ✅ Detect no face scenarios
- ✅ Detect multiple faces
- ✅ Track face count and missing duration

### Head Pose Estimation (Section 4.4)
- ✅ Detect abnormal head movements (left/right, up/down)
- ✅ Track head turn angles (yaw, pitch, roll)
- ✅ Configurable thresholds (default: >30° for >5 seconds)

### Eye Gaze Tracking (Section 4.5)
- ✅ Detect gaze direction
- ✅ Identify off-screen gazes
- ✅ Detect looking down (possible phone use)
- ✅ Track repeated gaze deviations

### Mobile Phone Detection (Section 4.6)
- ✅ Detect mobile phones in frame using YOLO
- ✅ Log timestamps when detected
- ✅ Track phone presence duration

### Cheating Score System (Section 4.8)
Weighted scoring system:
| Behavior | Weight |
|----------|--------|
| No face detected | 30 |
| Multiple faces | 40 |
| Head movement | 15 |
| Eye gaze deviation | 10 |
| Mobile phone | 50 |

**Risk Levels:**
- **Low**: Score < 30
- **Medium**: Score 30-60
- **High**: Score > 60

## 🏗️ Architecture

### Backend (Python/Flask)
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-JWT-Extended**: JWT authentication
- **Flask-SocketIO**: Real-time communication
- **OpenCV**: Computer vision operations
- **MediaPipe**: Face detection and facial landmarks
- **YOLO (Ultralytics)**: Object detection for phones
- **ReportLab**: PDF report generation

### Frontend (HTML/CSS/JavaScript)
- Pure HTML/CSS/JavaScript (no framework dependencies)
- Real-time WebSocket communication
- Responsive design
- Separate interfaces for students, invigilators, and admins

### Database (SQLite/PostgreSQL)
- User management (students, faculty, admins)
- Exam and session tracking
- Event logging
- Alert management

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Webcam (for testing)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/arslan786786/AI-Based-Exam-Cheating-Detection-System.git
cd AI-Based-Exam-Cheating-Detection-System
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize database**
```bash
python init_db.py
```

This will create:
- Database tables
- Sample users (admin, faculty, students)
- Sample exams

5. **Run the application**
```bash
python backend/app.py
```

The server will start on `http://localhost:5000`

## 🚀 Usage

### Access the Applications

1. **Student Interface**: Open `frontend/student.html` in your browser
   - Login with: `student1` / `password123`
   - Allow webcam access when prompted
   - Start taking the exam

2. **Invigilator Dashboard**: Open `frontend/invigilator.html` in your browser
   - Login with: `faculty1` / `password123`
   - Monitor active sessions in real-time
   - View alerts and suspicious activities

3. **Admin Panel**: Use API endpoints or create custom admin interface
   - Login with: `admin` / `admin123`

### Sample Credentials

**Admin:**
- Username: `admin`
- Password: `admin123`

**Faculty:**
- Username: `faculty1`
- Password: `password123`

**Students:**
- Username: `student1` to `student5`
- Password: `password123`

## 📡 API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user info
- `POST /change-password` - Change password

### Exams (`/api/exams`)
- `GET /` - List all exams
- `GET /{id}` - Get exam details
- `POST /` - Create exam (faculty/admin)
- `PUT /{id}` - Update exam (faculty/admin)
- `DELETE /{id}` - Delete exam (admin)

### Monitoring (`/api/monitoring`)
- `POST /session/start` - Start exam session
- `POST /session/{id}/end` - End exam session
- `GET /session/{id}` - Get session details
- `GET /sessions/active` - Get all active sessions
- `POST /event` - Log cheating event
- `GET /session/{id}/events` - Get session events
- `GET /alerts` - Get alerts (invigilator)
- `POST /alert/{id}/read` - Mark alert as read

### Reports (`/api/reports`)
- `GET /session/{id}/pdf` - Generate PDF report
- `GET /session/{id}/csv` - Generate CSV report
- `GET /exam/{id}/summary` - Get exam summary statistics

## 🔧 Configuration

Edit `backend/config/config.py` to customize:

```python
# Webcam settings
WEBCAM_FPS = 2  # Frames per second

# Detection thresholds
HEAD_TURN_ANGLE_THRESHOLD = 30  # degrees
HEAD_TURN_DURATION_THRESHOLD = 5  # seconds
GAZE_DEVIATION_THRESHOLD = 0.3

# Scoring weights
SCORE_NO_FACE = 30
SCORE_MULTIPLE_FACES = 40
SCORE_HEAD_MOVEMENT = 15
SCORE_EYE_GAZE_DEVIATION = 10
SCORE_MOBILE_PHONE = 50

# Risk levels
RISK_LOW_THRESHOLD = 30
RISK_MEDIUM_THRESHOLD = 60
RISK_HIGH_THRESHOLD = 100
```

## 🧪 Testing

To test the system:

1. Start the backend server
2. Open `student.html` in a browser
3. Login and start an exam session
4. Open `invigilator.html` in another browser window/tab
5. Observe real-time monitoring and alerts

## 📊 Reports

The system generates comprehensive reports including:

- **PDF Reports**: Detailed session reports with charts and timelines
- **CSV Exports**: Raw data export for further analysis
- **Summary Statistics**: Exam-wide analytics and metrics

## 🔒 Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Secure session management
- Privacy-aware recording (only suspicious moments)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- Arslan - Initial work

## 🙏 Acknowledgments

- MediaPipe for face detection and landmarks
- Ultralytics YOLO for object detection
- Flask community for excellent documentation
- OpenCV for computer vision capabilities

## 📧 Support

For support and questions, please open an issue on GitHub.

---

**⚠️ Disclaimer**: This system is designed for educational and authorized proctoring purposes only. Ensure compliance with privacy laws and regulations in your jurisdiction.
