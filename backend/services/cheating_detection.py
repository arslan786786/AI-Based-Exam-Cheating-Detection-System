"""
Cheating detection and scoring service
"""
from typing import Dict, List
from datetime import datetime, timedelta
import numpy as np

class CheatingDetectionService:
    """Service for analyzing behavior and calculating cheating scores"""
    
    def __init__(self, config):
        """
        Initialize cheating detection service with configuration
        
        Args:
            config: Application configuration object
        """
        self.config = config
        
        # Thresholds
        self.head_turn_angle = config.HEAD_TURN_ANGLE_THRESHOLD
        self.head_turn_duration = config.HEAD_TURN_DURATION_THRESHOLD
        self.gaze_deviation_threshold = config.GAZE_DEVIATION_THRESHOLD
        self.face_missing_threshold = config.FACE_MISSING_THRESHOLD
        
        # Scores
        self.score_no_face = config.SCORE_NO_FACE
        self.score_multiple_faces = config.SCORE_MULTIPLE_FACES
        self.score_head_movement = config.SCORE_HEAD_MOVEMENT
        self.score_eye_gaze = config.SCORE_EYE_GAZE_DEVIATION
        self.score_mobile_phone = config.SCORE_MOBILE_PHONE
        
        # Risk thresholds
        self.risk_low = config.RISK_LOW_THRESHOLD
        self.risk_medium = config.RISK_MEDIUM_THRESHOLD
        self.risk_high = config.RISK_HIGH_THRESHOLD
        
        # Tracking state
        self.state_tracker = {}
    
    def init_session_state(self, session_id: int):
        """
        Initialize state tracking for a session
        
        Args:
            session_id: Exam session ID
        """
        self.state_tracker[session_id] = {
            'face_missing_start': None,
            'face_missing_duration': 0,
            'head_turn_start': None,
            'head_turn_duration': 0,
            'gaze_deviation_count': 0,
            'last_head_angles': [],
            'last_gaze_positions': [],
            'total_score': 0,
            'events': []
        }
    
    def analyze_face_detection(self, session_id: int, face_result: Dict) -> List[Dict]:
        """
        Analyze face detection results and generate events
        
        Args:
            session_id: Exam session ID
            face_result: Face detection result dictionary
            
        Returns:
            List of cheating events detected
        """
        if session_id not in self.state_tracker:
            self.init_session_state(session_id)
        
        state = self.state_tracker[session_id]
        events = []
        current_time = datetime.utcnow()
        
        face_count = face_result.get('face_count', 0)
        
        # Check for no face
        if face_count == 0:
            if state['face_missing_start'] is None:
                state['face_missing_start'] = current_time
            else:
                duration = (current_time - state['face_missing_start']).total_seconds()
                state['face_missing_duration'] = duration
                
                # Trigger event if threshold exceeded
                if duration >= self.face_missing_threshold:
                    events.append({
                        'event_type': 'no_face',
                        'score': self.score_no_face,
                        'details': {
                            'duration': duration,
                            'message': f'No face detected for {duration:.1f} seconds'
                        }
                    })
                    # Reset to avoid multiple triggers
                    state['face_missing_start'] = current_time
        else:
            state['face_missing_start'] = None
            state['face_missing_duration'] = 0
        
        # Check for multiple faces
        if face_count > 1:
            events.append({
                'event_type': 'multiple_faces',
                'score': self.score_multiple_faces,
                'details': {
                    'face_count': face_count,
                    'message': f'{face_count} faces detected in frame'
                }
            })
        
        return events
    
    def analyze_head_pose(self, session_id: int, pose_result: Dict) -> List[Dict]:
        """
        Analyze head pose and detect suspicious movements
        
        Args:
            session_id: Exam session ID
            pose_result: Head pose estimation result
            
        Returns:
            List of cheating events detected
        """
        if session_id not in self.state_tracker:
            self.init_session_state(session_id)
        
        state = self.state_tracker[session_id]
        events = []
        current_time = datetime.utcnow()
        
        if pose_result.get('status') != 'ok':
            return events
        
        yaw = pose_result.get('yaw', 0)
        pitch = pose_result.get('pitch', 0)
        
        # Check if head is turned significantly
        head_turned = (abs(yaw) > self.head_turn_angle or 
                      abs(pitch) > self.head_turn_angle)
        
        if head_turned:
            if state['head_turn_start'] is None:
                state['head_turn_start'] = current_time
            else:
                duration = (current_time - state['head_turn_start']).total_seconds()
                state['head_turn_duration'] = duration
                
                # Trigger event if threshold exceeded
                if duration >= self.head_turn_duration:
                    events.append({
                        'event_type': 'head_movement',
                        'score': self.score_head_movement,
                        'details': {
                            'yaw': yaw,
                            'pitch': pitch,
                            'duration': duration,
                            'message': f'Head turned (yaw: {yaw:.1f}°, pitch: {pitch:.1f}°) for {duration:.1f}s'
                        }
                    })
                    # Reset to avoid multiple triggers
                    state['head_turn_start'] = current_time
        else:
            state['head_turn_start'] = None
            state['head_turn_duration'] = 0
        
        # Track head movement history
        state['last_head_angles'].append({
            'yaw': yaw,
            'pitch': pitch,
            'timestamp': current_time
        })
        
        # Keep only recent history (last 30 seconds)
        cutoff_time = current_time - timedelta(seconds=30)
        state['last_head_angles'] = [
            angle for angle in state['last_head_angles']
            if angle['timestamp'] > cutoff_time
        ]
        
        return events
    
    def analyze_gaze_direction(self, session_id: int, gaze_result: Dict) -> List[Dict]:
        """
        Analyze gaze direction and detect off-screen looking
        
        Args:
            session_id: Exam session ID
            gaze_result: Gaze estimation result
            
        Returns:
            List of cheating events detected
        """
        if session_id not in self.state_tracker:
            self.init_session_state(session_id)
        
        state = self.state_tracker[session_id]
        events = []
        
        if gaze_result.get('status') != 'ok':
            return events
        
        looking_away = gaze_result.get('looking_away', False)
        deviation = gaze_result.get('deviation', 0)
        
        # Configurable threshold for consecutive gaze deviations
        GAZE_DEVIATION_COUNT_THRESHOLD = 5
        
        if looking_away or deviation > self.gaze_deviation_threshold:
            state['gaze_deviation_count'] += 1
            
            # Trigger event for frequent gaze deviations
            if state['gaze_deviation_count'] >= GAZE_DEVIATION_COUNT_THRESHOLD:
                events.append({
                    'event_type': 'gaze_deviation',
                    'score': self.score_eye_gaze,
                    'details': {
                        'gaze_x': gaze_result.get('gaze_x', 0),
                        'gaze_y': gaze_result.get('gaze_y', 0),
                        'deviation': deviation,
                        'message': 'Frequent gaze deviations detected'
                    }
                })
                state['gaze_deviation_count'] = 0  # Reset counter
        else:
            # Reset counter if looking at screen
            if state['gaze_deviation_count'] > 0:
                state['gaze_deviation_count'] -= 1
        
        return events
    
    def analyze_object_detection(self, session_id: int, object_result: Dict) -> List[Dict]:
        """
        Analyze object detection results for mobile phones
        
        Args:
            session_id: Exam session ID
            object_result: Object detection result
            
        Returns:
            List of cheating events detected
        """
        events = []
        
        if object_result.get('phone_detected', False):
            phone_count = object_result.get('phone_count', 0)
            events.append({
                'event_type': 'mobile_phone',
                'score': self.score_mobile_phone,
                'details': {
                    'phone_count': phone_count,
                    'detections': object_result.get('detections', []),
                    'message': f'Mobile phone detected in frame ({phone_count} phones)'
                }
            })
        
        return events
    
    def calculate_total_score(self, session_id: int, new_events: List[Dict]) -> float:
        """
        Calculate and update total cheating score for session
        
        Args:
            session_id: Exam session ID
            new_events: List of new cheating events
            
        Returns:
            Updated total cheating score
        """
        if session_id not in self.state_tracker:
            self.init_session_state(session_id)
        
        state = self.state_tracker[session_id]
        
        # Add scores from new events
        for event in new_events:
            state['total_score'] += event.get('score', 0)
            state['events'].append(event)
        
        return state['total_score']
    
    def get_risk_level(self, total_score: float) -> str:
        """
        Determine risk level based on total score
        
        Args:
            total_score: Total cheating score
            
        Returns:
            Risk level: 'low', 'medium', or 'high'
        """
        if total_score >= self.risk_high:
            return 'high'
        elif total_score >= self.risk_medium:
            return 'medium'
        elif total_score >= self.risk_low:
            return 'low'
        else:
            return 'low'
    
    def clear_session_state(self, session_id: int):
        """
        Clear state tracking for a completed session
        
        Args:
            session_id: Exam session ID
        """
        if session_id in self.state_tracker:
            del self.state_tracker[session_id]
