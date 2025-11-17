from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
from gamification import GamificationSystem

app = Flask(__name__)

# Ensure log file exists
LOG_FILE = 'pomodoro_log.txt'
GAMIFICATION_DATA_FILE = 'gamification_data.json'

# Initialize gamification system
gamification = GamificationSystem(LOG_FILE, GAMIFICATION_DATA_FILE)

@app.route('/')
def index():
    """Serve the main timer page"""
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log_session():
    """Log pomodoro session events"""
    try:
        data = request.get_json()
        
        # Extract session data
        session_type = data.get('session_type', 'work')  # work, short_break, long_break
        action = data.get('action', 'completed')  # completed, skipped
        session_number = data.get('session_number', 1)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Log entry format: timestamp | session_type | action | session_number
        log_entry = f"{timestamp} | {session_type} | {action} | session_{session_number}\n"
        
        # Append to log file
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        # Award XP and check for achievements
        gamification_update = gamification.award_xp(session_type, action)
        
        return jsonify({
            'status': 'success',
            'message': 'Session logged successfully',
            'gamification': gamification_update
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/history')
def get_history():
    """Optional endpoint to retrieve session history"""
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({'sessions': []})
        
        sessions = []
        with open(LOG_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(' | ')
                    if len(parts) == 4:
                        sessions.append({
                            'timestamp': parts[0],
                            'session_type': parts[1],
                            'action': parts[2],
                            'session_number': parts[3]
                        })
        
        return jsonify({'sessions': sessions})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/gamification/stats')
def get_gamification_stats():
    """Get comprehensive gamification data"""
    try:
        data = gamification.get_gamification_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/gamification/achievements')
def get_achievements():
    """Get all achievements with unlock status"""
    try:
        achievements = gamification.get_all_achievements()
        return jsonify({'achievements': achievements})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Use environment variables for production deployment
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)