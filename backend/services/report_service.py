"""
Report generation service for exam cheating analysis
"""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import io
import pandas as pd
from backend.models.models import ExamSession, CheatingEvent, User, Exam

class ReportService:
    """Service for generating cheating reports"""
    
    def __init__(self, config):
        """
        Initialize report service
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.reports_folder = os.path.join(config.UPLOAD_FOLDER, 'reports')
        os.makedirs(self.reports_folder, exist_ok=True)
    
    def generate_session_report_pdf(self, session_id: int) -> str:
        """
        Generate PDF report for a session
        
        Args:
            session_id: Exam session ID
            
        Returns:
            Path to generated PDF file
        """
        session = ExamSession.query.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        student = User.query.get(session.student_id)
        exam = Exam.query.get(session.exam_id)
        events = CheatingEvent.query.filter_by(session_id=session_id).order_by(CheatingEvent.timestamp).all()
        
        # Create PDF filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"session_{session_id}_report_{timestamp}.pdf"
        filepath = os.path.join(self.reports_folder, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Exam Cheating Detection Report", title_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Session Information
        info_data = [
            ['Student:', student.full_name if student else 'Unknown'],
            ['Username:', student.username if student else 'Unknown'],
            ['Exam:', exam.title if exam else 'Unknown'],
            ['Start Time:', session.start_time.strftime('%Y-%m-%d %H:%M:%S') if session.start_time else 'N/A'],
            ['End Time:', session.end_time.strftime('%Y-%m-%d %H:%M:%S') if session.end_time else 'N/A'],
            ['Total Score:', f"{session.total_cheating_score:.2f}"],
            ['Risk Level:', session.risk_level.upper()],
            ['Status:', session.status.upper()]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.5 * inch))
        
        # Events Summary
        story.append(Paragraph("Cheating Events Summary", styles['Heading2']))
        story.append(Spacer(1, 0.2 * inch))
        
        if events:
            # Event statistics
            event_types = {}
            for event in events:
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
            event_summary = [['Event Type', 'Count', 'Total Score']]
            for event_type, count in event_types.items():
                total_score = sum(e.score for e in events if e.event_type == event_type)
                event_summary.append([event_type.replace('_', ' ').title(), str(count), f"{total_score:.2f}"])
            
            summary_table = Table(event_summary, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a4a4a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.5 * inch))
            
            # Detailed Events
            story.append(Paragraph("Detailed Events Timeline", styles['Heading2']))
            story.append(Spacer(1, 0.2 * inch))
            
            # Create timeline chart
            chart_buffer = self._create_timeline_chart(events)
            if chart_buffer:
                img = Image(chart_buffer, width=6*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 0.3 * inch))
        else:
            story.append(Paragraph("No cheating events detected.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _create_timeline_chart(self, events):
        """Create a timeline chart of events"""
        if not events:
            return None
        
        try:
            # Prepare data
            timestamps = [event.timestamp for event in events]
            event_types = [event.event_type.replace('_', ' ').title() for event in events]
            scores = [event.score for event in events]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Plot events
            colors_map = {
                'No Face': 'orange',
                'Multiple Faces': 'red',
                'Head Movement': 'yellow',
                'Gaze Deviation': 'lightblue',
                'Mobile Phone': 'darkred'
            }
            
            for i, (ts, et, score) in enumerate(zip(timestamps, event_types, scores)):
                color = colors_map.get(et, 'gray')
                ax.scatter(ts, score, c=color, s=100, alpha=0.6, edgecolors='black')
                ax.annotate(et, (ts, score), fontsize=8, ha='center')
            
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Score', fontsize=12)
            ax.set_title('Cheating Events Timeline', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
        except Exception as e:
            print(f"Error creating timeline chart: {e}")
            return None
    
    def generate_session_report_csv(self, session_id: int) -> str:
        """
        Generate CSV report for a session
        
        Args:
            session_id: Exam session ID
            
        Returns:
            Path to generated CSV file
        """
        session = ExamSession.query.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        student = User.query.get(session.student_id)
        exam = Exam.query.get(session.exam_id)
        events = CheatingEvent.query.filter_by(session_id=session_id).order_by(CheatingEvent.timestamp).all()
        
        # Create CSV filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"session_{session_id}_report_{timestamp}.csv"
        filepath = os.path.join(self.reports_folder, filename)
        
        # Prepare data
        data = []
        for event in events:
            data.append({
                'Session ID': session_id,
                'Student': student.full_name if student else 'Unknown',
                'Username': student.username if student else 'Unknown',
                'Exam': exam.title if exam else 'Unknown',
                'Event Type': event.event_type,
                'Timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S') if event.timestamp else 'N/A',
                'Score': event.score,
                'Details': str(event.details) if event.details else ''
            })
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    def generate_summary_report(self, exam_id: int) -> dict:
        """
        Generate summary report for all sessions in an exam
        
        Args:
            exam_id: Exam ID
            
        Returns:
            Dictionary with summary statistics
        """
        sessions = ExamSession.query.filter_by(exam_id=exam_id).all()
        
        total_sessions = len(sessions)
        high_risk = sum(1 for s in sessions if s.risk_level == 'high')
        medium_risk = sum(1 for s in sessions if s.risk_level == 'medium')
        low_risk = sum(1 for s in sessions if s.risk_level == 'low')
        
        avg_score = sum(s.total_cheating_score for s in sessions) / total_sessions if total_sessions > 0 else 0
        
        # Event statistics
        all_events = CheatingEvent.query.join(ExamSession).filter(ExamSession.exam_id == exam_id).all()
        event_counts = {}
        for event in all_events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        return {
            'exam_id': exam_id,
            'total_sessions': total_sessions,
            'risk_distribution': {
                'high': high_risk,
                'medium': medium_risk,
                'low': low_risk
            },
            'average_score': round(avg_score, 2),
            'event_counts': event_counts,
            'total_events': len(all_events)
        }
