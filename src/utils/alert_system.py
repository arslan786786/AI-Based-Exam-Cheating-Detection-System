"""
Alert System Module
Manages alerts and suspicious activity logging
"""
import os
import cv2
import json
from datetime import datetime
from typing import List, Dict
import config


class AlertSystem:
    def __init__(self):
        """Initialize alert system"""
        self.alerts = []
        self.last_alert_time = {}
        self.evidence_dir = config.EVIDENCE_DIR
        
        # Create evidence directory if it doesn't exist
        if config.SAVE_EVIDENCE and not os.path.exists(self.evidence_dir):
            os.makedirs(self.evidence_dir)
    
    def add_alert(self, alert_type: str, description: str, frame=None):
        """
        Add a new alert
        
        Args:
            alert_type: Type of suspicious activity
            description: Description of the alert
            frame: Optional frame to save as evidence
        """
        current_time = datetime.now()
        
        # Check cooldown to avoid spam
        if alert_type in self.last_alert_time:
            time_diff = (current_time - self.last_alert_time[alert_type]).total_seconds()
            if time_diff < config.ALERT_COOLDOWN:
                return
        
        # Create alert entry
        alert = {
            'timestamp': current_time.isoformat(),
            'type': alert_type,
            'description': description
        }
        
        self.alerts.append(alert)
        self.last_alert_time[alert_type] = current_time
        
        # Save evidence frame if provided
        if frame is not None and config.SAVE_EVIDENCE:
            filename = f"{alert_type}_{current_time.strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(self.evidence_dir, filename)
            cv2.imwrite(filepath, frame)
            alert['evidence_file'] = filename
        
        # Print alert to console
        print(f"[ALERT] {current_time.strftime('%H:%M:%S')} - {alert_type}: {description}")
    
    def get_alerts(self) -> List[Dict]:
        """
        Get all alerts
        
        Returns:
            List of alert dictionaries
        """
        return self.alerts
    
    def get_alert_count(self) -> int:
        """
        Get total number of alerts
        
        Returns:
            Number of alerts
        """
        return len(self.alerts)
    
    def save_report(self, filename: str = None):
        """
        Save alert report to JSON file
        
        Args:
            filename: Output filename (default: report_TIMESTAMP.json)
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.json"
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'total_alerts': len(self.alerts),
            'alerts': self.alerts
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"Report saved to {filename}")
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
        self.last_alert_time = {}
