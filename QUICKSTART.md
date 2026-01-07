# 🚀 Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git
- Webcam (for testing the system)

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/arslan786786/AI-Based-Exam-Cheating-Detection-System.git
cd AI-Based-Exam-Cheating-Detection-System
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Flask (web framework)
- OpenCV (computer vision)
- MediaPipe (face detection)
- YOLO (object detection)
- SQLAlchemy (database)
- And more...

**Note**: Installation may take 5-10 minutes depending on your internet connection.

### Step 4: Test Installation
```bash
python test_installation.py
```

If all tests pass, you're ready to proceed!

### Step 5: Initialize Database
```bash
python init_db.py
```

This creates:
- SQLite database file
- Sample users (admin, faculty, students)
- Sample exams

### Step 6: Start the Server
```bash
python backend/app.py
```

The server will start on `http://localhost:5000`

You should see:
```
* Running on http://0.0.0.0:5000
* Restarting with stat
* Debugger is active!
```

### Step 7: Access the Frontend

Open your web browser and navigate to:

1. **Student Interface**: 
   - Open `frontend/student.html` in your browser
   - Or visit: `file:///path/to/frontend/student.html`

2. **Invigilator Dashboard**: 
   - Open `frontend/invigilator.html` in your browser
   - Or visit: `file:///path/to/frontend/invigilator.html`

## Default Credentials

### Admin
- **Username**: `admin`
- **Password**: `admin123`

### Faculty
- **Username**: `faculty1`
- **Password**: `password123`

### Students
- **Username**: `student1`, `student2`, `student3`, `student4`, or `student5`
- **Password**: `password123` (for all students)

## Testing the System

### As a Student:
1. Open `frontend/student.html`
2. Login with `student1` / `password123`
3. Allow webcam access when prompted
4. The system will start monitoring your behavior
5. Try looking away, turning your head, or covering your face to see alerts

### As an Invigilator:
1. Open `frontend/invigilator.html`
2. It will auto-login as faculty
3. You'll see all active exam sessions
4. Monitor student behavior in real-time
5. View alerts and suspicious activities

## Troubleshooting

### Issue: Dependencies fail to install
**Solution**: Make sure you have Python 3.8+ installed
```bash
python --version
```

### Issue: Webcam not detected
**Solution**: 
- Check if your webcam is connected
- Grant browser permission to access webcam
- Try a different browser (Chrome recommended)

### Issue: Port 5000 already in use
**Solution**: Change the port in `backend/app.py`:
```python
port = int(os.environ.get('PORT', 8000))  # Change 5000 to 8000
```

### Issue: Database errors
**Solution**: Delete the database and reinitialize:
```bash
rm exam_proctoring.db
python init_db.py
```

### Issue: Import errors
**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Running in Production

For production deployment:

1. Use a production WSGI server (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

2. Use PostgreSQL instead of SQLite:
```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@localhost/dbname"
```

3. Set environment to production:
```bash
export FLASK_ENV=production
```

4. Use a reverse proxy (e.g., Nginx) for serving frontend files

## Docker Deployment

If you have Docker installed:

```bash
# Build Docker image
docker build -t exam-proctoring .

# Run container
docker run -p 5000:5000 exam-proctoring
```

## API Documentation

Full API documentation is available in the main [README.md](README.md) file.

Key endpoints:
- `/api/auth/login` - Login
- `/api/exams` - Manage exams
- `/api/monitoring/session/start` - Start exam session
- `/api/monitoring/alerts` - Get alerts
- `/api/reports/session/{id}/pdf` - Generate report

## Next Steps

1. **Customize Configuration**: Edit `backend/config/config.py` to adjust detection thresholds
2. **Add Users**: Use the registration API to add more users
3. **Create Exams**: Use the exam management API to create new exams
4. **Generate Reports**: After exam sessions, generate PDF/CSV reports

## Support

If you encounter any issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review error logs in the terminal
3. Open an issue on GitHub

## Security Notes

⚠️ **Important**:
- Change default passwords in production
- Use HTTPS in production
- Set strong JWT secret keys
- Review privacy laws before deploying

---

Happy Proctoring! 🎓📹
