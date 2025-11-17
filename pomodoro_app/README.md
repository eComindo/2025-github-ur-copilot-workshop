# Pomodoro Timer Web App

A simple and elegant Pomodoro Timer web application built with Flask and vanilla JavaScript. This app helps you stay focused and productive using the Pomodoro Technique.

## Features

- **Timer Functionality**: 25-minute work sessions with 5-minute short breaks and 15-minute long breaks
- **Session Tracking**: Visual progress indicator showing completed sessions
- **Customizable Settings**: Adjust work and break durations to your preference
- **Session Logging**: Automatic logging of completed and skipped sessions
- **Responsive Design**: Works on desktop and mobile devices
- **Browser Notifications**: Get notified when sessions complete

### 🎮 Gamification Features (New!)

Enhance your motivation and track your progress with these gamification elements:

- **XP & Level System**: Earn experience points and level up as you complete Pomodoros
  - Work sessions: 25 XP
  - Break sessions: 5 XP
  - 11 levels with progressive requirements
  
- **Achievement Badges**: Unlock 8 different achievements
  - 🍅 **First Step**: Complete your first Pomodoro
  - 🔥 **Consistency**: Complete Pomodoros for 3 consecutive days
  - ⚡ **Week Warrior**: Complete Pomodoros for 7 consecutive days
  - 📈 **Productive Week**: Complete 10 Pomodoros in a week
  - 🎯 **Focus Master**: Complete 20 Pomodoros in a week
  - ⭐ **Half Century**: Complete 50 total Pomodoros
  - 👑 **Centurion**: Complete 100 total Pomodoros
  - 💎 **Perfect Day**: Complete 8 Pomodoros in a single day

- **Streak Tracking**: Build habits with consecutive day streaks
  - Current streak counter
  - Longest streak record

- **Comprehensive Statistics**:
  - Total completed sessions
  - Today's session count
  - This week's session count
  - Completion rate percentage
  - Total focus time (in hours/minutes)
  - Best day record
  - 30-day activity graph data

## Pomodoro Technique

The Pomodoro Technique uses a timer to break work into intervals:
1. 25 minutes of focused work
2. 5-minute short break
3. Repeat 4 times
4. Take a 15-minute long break after 4 sessions

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pomodoro_app
   ```

2. **Create virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   uv pip install Flask
   ```

## Running the Application

1. **Activate virtual environment** (if not already activated):
   ```bash
   source .venv/bin/activate
   ```

2. **Start the Flask application**:
   ```bash
   python app.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage

1. **Start a Session**: Click the "Start" button to begin a 25-minute work session
2. **Pause/Resume**: Click "Start" again to pause, and once more to resume
3. **Reset**: Click "Reset" to restart the current session
4. **Skip**: Click "Skip" to move to the next session (break or work)
5. **Settings**: Click "Settings" to customize session durations
6. **Progress**: Watch the dots at the bottom to track your progress through the 4-session cycle

## Project Structure

```
pomodoro_app/
├── app.py                     # Flask backend server
├── gamification.py            # Gamification system (XP, levels, achievements)
├── templates/
│   └── index.html            # Main HTML template with gamification UI
├── static/
│   ├── style.css             # CSS styling including gamification styles
│   └── timer.js              # JavaScript timer logic and gamification
├── pomodoro_log.txt          # Session log file (created automatically)
├── gamification_data.json    # Gamification data storage (created automatically)
├── test_pomodoro.py          # Unit tests for core functionality
├── test_gamification.py      # Unit tests for gamification system
├── test_gamification_endpoints.py  # Integration tests for API endpoints
└── README.md                 # This file
```

## API Endpoints

- `GET /` - Serves the main timer page
- `POST /log` - Logs session events and returns gamification updates (XP gained, level ups, achievements)
- `GET /history` - Returns session history
- `GET /gamification/stats` - Returns comprehensive gamification data (XP, level, streaks, stats, achievements)
- `GET /gamification/achievements` - Returns all achievements with unlock status

## Session Logging

The app automatically logs all session events to `pomodoro_log.txt` with the following format:
```
timestamp | session_type | action | session_number
```

Example:
```
2024-01-15 14:30:00 | work | completed | session_1
2024-01-15 14:55:00 | short_break | completed | session_1
```

## Customization

### Settings
- **Work Duration**: Default 25 minutes (adjustable 1-60 minutes)
- **Short Break**: Default 5 minutes (adjustable 1-30 minutes)  
- **Long Break**: Default 15 minutes (adjustable 1-60 minutes)

Settings are saved in your browser's localStorage and persist between sessions.

### Browser Notifications
The app requests permission for browser notifications to alert you when sessions complete. You can enable/disable this in your browser settings.

## Development

### Adding Features
- Modify `app.py` for backend changes
- Edit `timer.js` for timer logic updates
- Update `style.css` for styling changes
- Modify `index.html` for UI structure changes

### Testing
Run the Flask app in debug mode (default) to see detailed error messages and automatic reloading during development.

To run the test suite:
```bash
pytest -v  # Run all tests
pytest test_pomodoro.py -v  # Run core functionality tests
pytest test_gamification.py -v  # Run gamification system tests
pytest test_gamification_endpoints.py -v  # Run API endpoint tests
```

## How Gamification Works

### XP and Leveling
- Complete work sessions to earn 25 XP
- Complete break sessions to earn 5 XP
- Level up when you reach XP thresholds (100, 250, 500, 800, 1200, etc.)
- Visual progress bar shows your progress toward the next level
- Celebration modal appears when you level up

### Streaks
- Complete at least one work session per day to maintain your streak
- Streaks are counted for consecutive days with activity
- Missing a day breaks your current streak (but your longest streak is preserved)
- Streaks encourage daily habit building

### Achievements
- Achievements unlock automatically when you meet their conditions
- Unlocked achievements are highlighted in green
- Locked achievements appear grayed out
- Achievement unlock notifications appear as modals
- Hover over achievements to see their descriptions

### Statistics
- All stats update in real-time after each session
- Statistics persist across browser sessions
- Data is stored locally in `gamification_data.json`
- View your productivity trends at a glance

## Browser Support
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## License
MIT License - feel free to use and modify as needed.