from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Path to session log file
LOG_FILE = 'pomodoro_log.json'

@app.route('/')
def index():
    """Serve the main Pomodoro timer page."""
    return render_template('index.html')

@app.route('/log-session', methods=['POST'])
def log_session():
    """Log a completed Pomodoro session to a JSON file."""
    try:
        # Get session data from request
        session_data = request.get_json()
        
        # Validate required fields
        if not all(key in session_data for key in ['session_type', 'start_time', 'end_time', 'status']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Load existing logs or create new list
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Append new session
        logs.append(session_data)
        
        # Save back to file
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Session logged successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/session-history', methods=['GET'])
def session_history():
    """Get session history for analytics (optional feature)."""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
            return jsonify(logs), 200
        else:
            return jsonify([]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)