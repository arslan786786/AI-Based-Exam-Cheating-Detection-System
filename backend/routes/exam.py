"""
Exam management routes for creating and managing exams
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.models.models import db, Exam, User
from datetime import datetime

exam_bp = Blueprint('exam', __name__, url_prefix='/api/exams')

def require_role(*roles):
    """Decorator to check user role"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@exam_bp.route('/', methods=['GET'])
@jwt_required()
def list_exams():
    """List all exams (filtered by role)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        current_user_id = get_jwt_identity()
        
        if user_role == 'admin':
            # Admin can see all exams
            exams = Exam.query.all()
        elif user_role == 'faculty':
            # Faculty can see exams they created
            exams = Exam.query.filter_by(created_by=current_user_id).all()
        else:
            # Students can see active exams
            exams = Exam.query.filter_by(is_active=True).all()
        
        return jsonify({
            'exams': [exam.to_dict() for exam in exams]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/<int:exam_id>', methods=['GET'])
@jwt_required()
def get_exam(exam_id):
    """Get specific exam details"""
    try:
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return jsonify({'error': 'Exam not found'}), 404
        
        return jsonify({'exam': exam.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/', methods=['POST'])
@jwt_required()
@require_role('faculty', 'admin')
def create_exam():
    """Create a new exam (faculty/admin only)"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['title', 'duration_minutes']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new exam
        exam = Exam(
            title=data['title'],
            description=data.get('description', ''),
            duration_minutes=data['duration_minutes'],
            start_time=datetime.fromisoformat(data['start_time']) if 'start_time' in data else None,
            end_time=datetime.fromisoformat(data['end_time']) if 'end_time' in data else None,
            created_by=current_user_id,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(exam)
        db.session.commit()
        
        return jsonify({
            'message': 'Exam created successfully',
            'exam': exam.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/<int:exam_id>', methods=['PUT'])
@jwt_required()
@require_role('faculty', 'admin')
def update_exam(exam_id):
    """Update exam details (faculty/admin only)"""
    try:
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return jsonify({'error': 'Exam not found'}), 404
        
        # Check ownership (faculty can only update their own exams)
        claims = get_jwt()
        user_role = claims.get('role')
        current_user_id = get_jwt_identity()
        
        if user_role == 'faculty' and exam.created_by != current_user_id:
            return jsonify({'error': 'You can only update your own exams'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            exam.title = data['title']
        if 'description' in data:
            exam.description = data['description']
        if 'duration_minutes' in data:
            exam.duration_minutes = data['duration_minutes']
        if 'start_time' in data:
            exam.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            exam.end_time = datetime.fromisoformat(data['end_time'])
        if 'is_active' in data:
            exam.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Exam updated successfully',
            'exam': exam.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exam_bp.route('/<int:exam_id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_exam(exam_id):
    """Delete exam (admin only)"""
    try:
        exam = Exam.query.get(exam_id)
        
        if not exam:
            return jsonify({'error': 'Exam not found'}), 404
        
        db.session.delete(exam)
        db.session.commit()
        
        return jsonify({'message': 'Exam deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
