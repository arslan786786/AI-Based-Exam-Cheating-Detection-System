"""
Report generation routes
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.services.report_service import ReportService
from backend.models.models import ExamSession
from flask import current_app
import os

report_bp = Blueprint('report', __name__, url_prefix='/api/reports')

@report_bp.route('/session/<int:session_id>/pdf', methods=['GET'])
@jwt_required()
def generate_pdf_report(session_id):
    """Generate PDF report for a session"""
    try:
        session = ExamSession.query.get(session_id)
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Check permissions
        if session.student_id != current_user_id and claims.get('role') not in ['faculty', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate report
        report_service = ReportService(current_app.config)
        filepath = report_service.generate_session_report_pdf(session_id)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Failed to generate report'}), 500
        
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'session_{session_id}_report.pdf'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/session/<int:session_id>/csv', methods=['GET'])
@jwt_required()
def generate_csv_report(session_id):
    """Generate CSV report for a session"""
    try:
        session = ExamSession.query.get(session_id)
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Check permissions
        if session.student_id != current_user_id and claims.get('role') not in ['faculty', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate report
        report_service = ReportService(current_app.config)
        filepath = report_service.generate_session_report_csv(session_id)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Failed to generate report'}), 500
        
        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'session_{session_id}_report.csv'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/exam/<int:exam_id>/summary', methods=['GET'])
@jwt_required()
def get_exam_summary(exam_id):
    """Get summary report for an exam"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role not in ['faculty', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate summary
        report_service = ReportService(current_app.config)
        summary = report_service.generate_summary_report(exam_id)
        
        return jsonify({'summary': summary}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
