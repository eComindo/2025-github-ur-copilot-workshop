"""
Pomodoro Timer Flask Backend
Serves the frontend and provides API endpoints for session logging.
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
LOG_FILE = os.path.join(os.path.dirname(__file__), 'pomodoro_log.txt')

# Valid values for validation
VALID_SESSION_TYPES = ['work', 'short_break', 'long_break']
VALID_ACTIONS = ['complete', 'skip']


def validate_session_data(data):
    """
    Validate incoming session data.
    
    Args:
        data: Dictionary containing session data
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"
    
    # Check required fields
    required_fields = ['session_type', 'action', 'started_at', 'ended_at']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate session_type
    if data['session_type'] not in VALID_SESSION_TYPES:
        return False, f"Invalid session_type. Must be one of: {', '.join(VALID_SESSION_TYPES)}"
    
    # Validate action
    if data['action'] not in VALID_ACTIONS:
        return False, f"Invalid action. Must be one of: {', '.join(VALID_ACTIONS)}"
    
    # Validate timestamps (basic check - should be non-empty strings)
    if not data['started_at'] or not data['ended_at']:
        return False, "Timestamps cannot be empty"
    
    return True, None


def append_to_log(session_data):
    """
    Append session data to the log file in JSON Lines format.
    
    Args:
        session_data: Dictionary containing validated session data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create log file if it doesn't exist
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            json.dump(session_data, f)
            f.write('\n')
        return True
    except Exception as e:
        print(f"Error writing to log file: {e}")
        return False


def read_log_history():
    """
    Read and parse the log file.
    
    Returns:
        list: List of session dictionaries, or empty list if file doesn't exist
    """
    if not os.path.exists(LOG_FILE):
        return []
    
    sessions = []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        session = json.loads(line)
                        sessions.append(session)
                    except json.JSONDecodeError:
                        # Skip corrupted lines
                        continue
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    return sessions


@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for testing."""
    return jsonify({"status": "healthy"}), 200


@app.route('/log', methods=['POST'])
def log_session():
    """
    Log a Pomodoro session event.
    
    Expected JSON payload:
    {
        "session_type": "work" | "short_break" | "long_break",
        "action": "complete" | "skip",
        "started_at": "ISO 8601 timestamp",
        "ended_at": "ISO 8601 timestamp"
    }
    """
    data = request.get_json()
    
    # Validate the data
    is_valid, error_message = validate_session_data(data)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    
    # Append to log file
    if append_to_log(data):
        return jsonify({"success": True, "message": "Session logged successfully"}), 200
    else:
        return jsonify({"error": "Failed to write to log file"}), 500


@app.route('/history', methods=['GET'])
def get_history():
    """
    Retrieve session history.
    
    Returns:
        JSON array of all logged sessions
    """
    sessions = read_log_history()
    return jsonify(sessions), 200


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
