"""
Monitoring routes for real-time exam proctoring
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.models.models import db, ExamSession, CheatingEvent, Alert, Exam, User
from datetime import datetime
import base64
import cv2
import numpy as np
import os

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

@monitoring_bp.route('/session/start', methods=['POST'])
@jwt_required()
def start_session():
    """Start an exam session for a student"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        if 'exam_id' not in data:
            return jsonify({'error': 'Missing exam_id'}), 400
        
        exam = Exam.query.get(data['exam_id'])
        if not exam:
            return jsonify({'error': 'Exam not found'}), 404
        
        if not exam.is_active:
            return jsonify({'error': 'Exam is not active'}), 400
        
        # Check if session already exists
        existing_session = ExamSession.query.filter_by(
            exam_id=data['exam_id'],
            student_id=current_user_id,
            status='in_progress'
        ).first()
        
        if existing_session:
            return jsonify({
                'message': 'Session already exists',
                'session': existing_session.to_dict()
            }), 200
        
        # Create new session
        session = ExamSession(
            exam_id=data['exam_id'],
            student_id=current_user_id,
            camera_status='active'
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'Session started successfully',
            'session': session.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/session/<int:session_id>/end', methods=['POST'])
@jwt_required()
def end_session(session_id):
    """End an exam session"""
    try:
        current_user_id = get_jwt_identity()
        session = ExamSession.query.get(session_id)
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Verify ownership
        if session.student_id != current_user_id:
            claims = get_jwt()
            if claims.get('role') not in ['faculty', 'admin']:
                return jsonify({'error': 'Unauthorized'}), 403
        
        session.end_time = datetime.utcnow()
        session.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Session ended successfully',
            'session': session.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """Get session details"""
    try:
        session = ExamSession.query.get(session_id)
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Check permissions
        if session.student_id != current_user_id and claims.get('role') not in ['faculty', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({'session': session.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/sessions/active', methods=['GET'])
@jwt_required()
def get_active_sessions():
    """Get all active sessions (for invigilators)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role not in ['faculty', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        sessions = ExamSession.query.filter_by(status='in_progress').all()
        
        # Include student information
        session_data = []
        for session in sessions:
            session_dict = session.to_dict()
            student = User.query.get(session.student_id)
            exam = Exam.query.get(session.exam_id)
            
            session_dict['student'] = student.to_dict() if student else None
            session_dict['exam'] = exam.to_dict() if exam else None
            session_data.append(session_dict)
        
        return jsonify({'sessions': session_data}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/event', methods=['POST'])
@jwt_required()
def log_event():
    """Log a cheating event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['session_id', 'event_type', 'score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        session = ExamSession.query.get(data['session_id'])
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Create event
        event = CheatingEvent(
            session_id=data['session_id'],
            event_type=data['event_type'],
            score=data['score'],
            details=data.get('details'),
            snapshot_path=data.get('snapshot_path')
        )
        
        db.session.add(event)
        
        # Update session score and risk level
        session.total_cheating_score += data['score']
        
        # Determine risk level using config thresholds
        from flask import current_app
        config = current_app.config
        if session.total_cheating_score >= config['RISK_HIGH_THRESHOLD']:
            session.risk_level = 'high'
        elif session.total_cheating_score >= config['RISK_MEDIUM_THRESHOLD']:
            session.risk_level = 'medium'
        else:
            session.risk_level = 'low'
        
        db.session.commit()
        
        # Create alert if high severity
        if session.risk_level in ['high', 'medium']:
            alert = Alert(
                session_id=session.id,
                alert_type=data['event_type'],
                message=data.get('details', {}).get('message', f'{data["event_type"]} detected'),
                severity='high' if session.risk_level == 'high' else 'medium'
            )
            db.session.add(alert)
            db.session.commit()
        
        return jsonify({
            'message': 'Event logged successfully',
            'event': event.to_dict(),
            'session': session.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/session/<int:session_id>/events', methods=['GET'])
@jwt_required()
def get_session_events(session_id):
    """Get all events for a session"""
    try:
        session = ExamSession.query.get(session_id)
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Check permissions
        if session.student_id != current_user_id and claims.get('role') not in ['faculty', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        events = CheatingEvent.query.filter_by(session_id=session_id).order_by(CheatingEvent.timestamp.desc()).all()
        
        return jsonify({
            'events': [event.to_dict() for event in events]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get all alerts for invigilators"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role not in ['faculty', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get query parameters
        is_read = request.args.get('is_read')
        severity = request.args.get('severity')
        
        query = Alert.query
        
        if is_read is not None:
            query = query.filter_by(is_read=(is_read.lower() == 'true'))
        
        if severity:
            query = query.filter_by(severity=severity)
        
        alerts = query.order_by(Alert.timestamp.desc()).limit(100).all()
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/alert/<int:alert_id>/read', methods=['POST'])
@jwt_required()
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role not in ['faculty', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Alert marked as read',
            'alert': alert.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
