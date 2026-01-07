"""
Main Flask application for AI-Based Exam Cheating Detection System
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from backend.config.config import config
from backend.models.models import db
from backend.routes.auth import auth_bp
from backend.routes.exam import exam_bp
from backend.routes.monitoring import monitoring_bp
from backend.routes.reports import report_bp
import os

def create_app(config_name='development'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration name (development, production)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt = JWTManager(app)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(exam_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(report_bp)
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token', 'message': str(error)}), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({'error': 'Missing authorization header', 'message': str(error)}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'AI-Based Exam Cheating Detection System API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'exams': '/api/exams',
                'monitoring': '/api/monitoring',
                'reports': '/api/reports'
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
    
    # Store socketio instance in app config for use in other modules
    app.socketio = socketio
    
    # WebSocket events for real-time monitoring
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('join_monitoring')
    def handle_join_monitoring(data):
        """Join monitoring room for real-time updates"""
        from flask_socketio import join_room
        session_id = data.get('session_id')
        if session_id:
            join_room(f'session_{session_id}')
            print(f'Client joined monitoring for session {session_id}')
    
    @socketio.on('leave_monitoring')
    def handle_leave_monitoring(data):
        """Leave monitoring room"""
        from flask_socketio import leave_room
        session_id = data.get('session_id')
        if session_id:
            leave_room(f'session_{session_id}')
            print(f'Client left monitoring for session {session_id}')
    
    return app, socketio

# Create application instance
app, socketio = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Run application with SocketIO support
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
