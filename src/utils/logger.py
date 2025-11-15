import os
import json
import datetime
import logging
from pathlib import Path
from ..core.config import LOGS_DIR, LOG_INTERVAL
from .utils import get_timestamp, time_difference_in_seconds, create_log_file_path

def setup_logger(name="ReceptionistAI", level=logging.INFO):
    """Setup and return a logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = create_log_file_path('system')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.setLevel(level)
    
    return logger

class Logger:
    def __init__(self):
        """Initialize the logger"""
        self.last_log_times = {}  # Dictionary to track last log time for each person
        self.log_file = create_log_file_path('reception')
        
        # Ensure log directory exists
        os.makedirs(LOGS_DIR, exist_ok=True)
        
        # Initialize log file with header if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"# Reception Log - Created on {get_timestamp()}\n")
                f.write("timestamp,person_id,person_name,recognition_type,confidence,action\n")
    
    def should_log(self, person_id):
        """Determine if we should log this person based on time interval"""
        if person_id not in self.last_log_times:
            return True
        
        current_time = datetime.datetime.now()
        last_log_time = self.last_log_times.get(person_id)
        
        # If enough time has passed since the last log for this person, log again
        if time_difference_in_seconds(last_log_time, current_time) >= LOG_INTERVAL:
            return True
            
        return False
    
    def log_recognition(self, person_id, person_name, recognition_type, confidence, action="detected"):
        """Log a recognition event if it meets the logging criteria"""
        # Check if we should log this person based on time interval
        if not self.should_log(person_id):
            return False
        
        # Update the last log time for this person
        self.last_log_times[person_id] = datetime.datetime.now()
        
        # Create log entry
        timestamp = get_timestamp()
        log_entry = f"{timestamp},{person_id},{person_name},{recognition_type},{confidence:.2f},{action}\n"
        
        # Write to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Also create a detailed JSON log with more information
        self._write_detailed_log({
            'timestamp': timestamp,
            'person_id': person_id,
            'person_name': person_name,
            'recognition_type': recognition_type,
            'confidence': round(confidence, 2),
            'action': action
        })
        
        return True
    
    def _write_detailed_log(self, log_data):
        """Write detailed log data in JSON format"""
        detailed_log_file = create_log_file_path('detailed')
        
        # Create file with initial structure if it doesn't exist
        if not os.path.exists(detailed_log_file):
            with open(detailed_log_file, 'w', encoding='utf-8') as f:
                json.dump({'logs': []}, f, ensure_ascii=False, indent=2)
        
        # Read existing logs
        with open(detailed_log_file, 'r', encoding='utf-8') as f:
            try:
                log_content = json.load(f)
            except json.JSONDecodeError:
                log_content = {'logs': []}
        
        # Append new log
        log_content['logs'].append(log_data)
        
        # Write updated logs
        with open(detailed_log_file, 'w', encoding='utf-8') as f:
            json.dump(log_content, f, ensure_ascii=False, indent=2)
    
    def log_system_event(self, event_type, description):
        """Log system events like startup, shutdown, errors, etc."""
        system_log_file = create_log_file_path('system')
        
        timestamp = get_timestamp()
        log_entry = f"{timestamp},{event_type},{description}\n"
        
        with open(system_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)