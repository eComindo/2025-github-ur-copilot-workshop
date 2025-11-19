# Pomodoro Timer Application - Technical Documentation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Application Components](#application-components)
- [User Flow](#user-flow)
- [Sequence Diagrams](#sequence-diagrams)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Frontend State Management](#frontend-state-management)

## Overview

The Pomodoro Timer is a web-based application that helps users improve productivity using the Pomodoro Technique. The application features a customizable timer that cycles through work sessions and breaks, with session logging capabilities.

### Key Features
- **Configurable Timer**: Customize work, short break, and long break durations
- **Session Tracking**: Tracks 4 work sessions before a long break
- **Session Logging**: Records completed and skipped sessions to a backend
- **Persistent Settings**: Saves user preferences in browser localStorage
- **Responsive Controls**: Start, pause, skip, and reset functionality

### Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Storage**: JSON Lines file format for session logs, localStorage for settings

---

## Architecture

The application follows a client-server architecture with a Flask backend serving both the static frontend and REST API endpoints.

```mermaid
graph TB
    subgraph "Client Browser"
        HTML[HTML Templates]
        CSS[CSS Stylesheets]
        JS[JavaScript Timer Logic]
        LS[localStorage]
    end
    
    subgraph "Flask Server"
        RT[Routes Handler]
        VAL[Validation Layer]
        LOG[Logging Functions]
    end
    
    subgraph "Storage"
        LOGFILE[pomodoro_log.txt<br/>JSON Lines Format]
    end
    
    HTML --> JS
    CSS --> HTML
    JS <--> LS
    JS <-->|HTTP/JSON| RT
    RT --> VAL
    VAL --> LOG
    LOG <--> LOGFILE
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| `app.py` | Flask server, routing, validation, file I/O |
| `timer.js` | Timer logic, state management, API communication |
| `index.html` | UI structure and layout |
| `style.css` | Visual styling and responsive design |
| `pomodoro_log.txt` | Persistent storage for session history |

---

## Application Components

### Backend (Flask)

#### Main Routes

1. **`GET /`** - Serves the main application page
2. **`GET /health`** - Health check endpoint (returns 200 OK)
3. **`POST /log`** - Logs a completed or skipped session
4. **`GET /history`** - Retrieves all logged sessions

#### Core Functions

- **`validate_session_data(data)`**: Validates session data before logging
- **`append_to_log(session_data)`**: Writes session data to log file
- **`read_log_history()`**: Reads and parses all logged sessions

### Frontend (JavaScript)

#### State Management

The application maintains a single `timerState` object:

```javascript
timerState = {
    minutes: 25,              // Current timer minutes
    seconds: 0,               // Current timer seconds
    isRunning: false,         // Timer active flag
    isPaused: false,          // Timer paused flag
    currentSession: 'work',   // Current session type
    sessionCount: 1,          // Work sessions completed (1-4)
    intervalId: null,         // setInterval reference
    sessionStartTime: null,   // ISO timestamp of session start
    settings: {               // User configurable settings
        workDuration: 25,
        shortBreakDuration: 5,
        longBreakDuration: 15
    }
}
```

#### Key Functions

- **Timer Control**: `startTimer()`, `pauseTimer()`, `resumeTimer()`, `stopTimer()`, `resetTimer()`
- **Session Management**: `switchSession()`, `determineNextSession()`, `handleSessionComplete()`
- **Settings**: `loadSettings()`, `saveSettings()`
- **API Communication**: `logSession()`, `fetchHistory()`
- **UI Updates**: `updateTimerDisplay()`, `updateSessionInfo()`, `showStatusMessage()`

---

## User Flow

### Main Application Flow

```mermaid
flowchart TD
    Start([User Opens App]) --> Load[Load Settings from localStorage]
    Load --> Display[Display Initial Timer<br/>25:00 Work Session]
    Display --> Choice{User Action?}
    
    Choice -->|Start| StartTimer[Start Timer<br/>Record Start Time]
    Choice -->|Skip| SkipCheck{Timer Running?}
    Choice -->|Reset| Reset[Reset to Initial State<br/>Work Session 1/4]
    Choice -->|Save Settings| SaveSettings[Validate & Save<br/>Update localStorage]
    
    SkipCheck -->|Yes| LogSkip[Log Skipped Session<br/>Switch to Next Session]
    SkipCheck -->|No| ShowWarning[Show Warning Message]
    
    StartTimer --> Running{Timer Running}
    Running -->|Each Second| Tick[Decrement Time<br/>Update Display]
    Running -->|Pause| Pause[Pause Timer<br/>Enable Resume]
    Running -->|Complete| Complete[Timer Reaches 00:00]
    
    Pause --> Resume{Resume?}
    Resume -->|Yes| Running
    Resume -->|No| Choice
    
    Tick --> Check{Time = 00:00?}
    Check -->|No| Running
    Check -->|Yes| Complete
    
    Complete --> LogComplete[Log Completed Session<br/>to Backend]
    LogComplete --> Determine{Determine<br/>Next Session}
    
    Determine -->|Work Session < 4| ShortBreak[Switch to<br/>Short Break<br/>5:00]
    Determine -->|Work Session = 4| LongBreak[Switch to<br/>Long Break<br/>15:00]
    Determine -->|After Break| WorkSession[Switch to<br/>Work Session<br/>25:00<br/>Increment Counter]
    
    ShortBreak --> Display
    LongBreak --> ResetCount[Reset Session Count]
    ResetCount --> Display
    WorkSession --> Display
    
    Reset --> Display
    SaveSettings --> Display
    LogSkip --> Display
    ShowWarning --> Choice
```

### Session Cycle Flow

```mermaid
flowchart LR
    W1[Work 1] --> SB1[Short Break]
    SB1 --> W2[Work 2]
    W2 --> SB2[Short Break]
    SB2 --> W3[Work 3]
    W3 --> SB3[Short Break]
    SB3 --> W4[Work 4]
    W4 --> LB[Long Break]
    LB --> W1
    
    style W1 fill:#ff6b6b
    style W2 fill:#ff6b6b
    style W3 fill:#ff6b6b
    style W4 fill:#ff6b6b
    style SB1 fill:#4ecdc4
    style SB2 fill:#4ecdc4
    style SB3 fill:#4ecdc4
    style LB fill:#45b7d1
```

---

## Sequence Diagrams

### Start Timer Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend UI
    participant Timer as Timer Logic
    participant State as Timer State
    
    User->>UI: Click "Start" Button
    UI->>Timer: startTimer()
    
    Timer->>State: Check isRunning
    State-->>Timer: false
    
    Timer->>State: Set isRunning = true
    Timer->>State: Set sessionStartTime = new Date()
    Timer->>Timer: setInterval(tick, 1000)
    
    Timer->>UI: Disable Start Button
    Timer->>UI: Enable Pause Button
    Timer->>UI: Show "Timer started!" message
    
    loop Every Second
        Timer->>Timer: tick()
        Timer->>State: Decrement seconds/minutes
        Timer->>UI: updateTimerDisplay()
    end
```

### Complete Session Sequence

```mermaid
sequenceDiagram
    actor User
    participant Timer as Timer Logic
    participant State as Timer State
    participant Backend as Flask Server
    participant Log as Log File
    
    Note over Timer: Timer reaches 00:00
    
    Timer->>Timer: handleSessionComplete()
    Timer->>Timer: stopTimer()
    Timer->>State: Get sessionStartTime
    Timer->>State: Set sessionEndTime
    
    Timer->>Backend: POST /log<br/>{session_type, action: 'complete',<br/>started_at, ended_at}
    
    Backend->>Backend: validate_session_data()
    alt Valid Data
        Backend->>Log: append_to_log()
        Log-->>Backend: Success
        Backend-->>Timer: 200 OK
    else Invalid Data
        Backend-->>Timer: 400 Bad Request
    end
    
    Timer->>UI: Show "Session completed!" message
    Timer->>State: Determine next session
    
    alt Work Session (count < 4)
        Timer->>State: currentSession = 'short_break'
    else Work Session (count = 4)
        Timer->>State: currentSession = 'long_break'
    else Break Session
        Timer->>State: currentSession = 'work'
        Timer->>State: Increment sessionCount
    end
    
    Timer->>State: Set minutes based on session type
    Timer->>UI: updateTimerDisplay()
    Timer->>UI: updateSessionInfo()
```

### Skip Session Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend UI
    participant Timer as Timer Logic
    participant State as Timer State
    participant Backend as Flask Server
    
    User->>UI: Click "Skip" Button
    UI->>Timer: skipSession()
    
    Timer->>State: Check isRunning
    
    alt Timer is Running
        State-->>Timer: true
        Timer->>State: Get sessionStartTime
        Timer->>State: Set sessionEndTime
        
        Timer->>Backend: POST /log<br/>{session_type, action: 'skip',<br/>started_at, ended_at}
        Backend-->>Timer: 200 OK
        
        Timer->>Timer: stopTimer()
        Timer->>Timer: switchToNextSession()
        Timer->>UI: Show "Session skipped!" message
        Timer->>UI: Update display
    else Timer Not Running
        State-->>Timer: false
        Timer->>UI: Show "Start timer before skipping" warning
    end
```

### Save Settings Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend UI
    participant Settings as Settings Module
    participant State as Timer State
    participant Storage as localStorage
    
    User->>UI: Modify duration inputs
    User->>UI: Click "Save Settings"
    
    UI->>Settings: saveSettings()
    Settings->>UI: Get input values
    
    Settings->>Settings: Validate inputs<br/>(work: 1-60, short: 1-30, long: 1-60)
    
    alt Valid Inputs
        Settings->>State: Update timerState.settings
        Settings->>Storage: localStorage.setItem('pomodoroSettings', JSON)
        
        alt Timer Not Running
            Settings->>State: Update current timer duration
            Settings->>UI: updateTimerDisplay()
        end
        
        Settings->>UI: Show "Settings saved!" success message
    else Invalid Inputs
        Settings->>UI: Show "Invalid duration values" error message
    end
```

### Fetch History Sequence

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Frontend
    participant Backend as Flask Server
    participant Log as Log File
    
    User->>Frontend: Request history (if implemented in UI)
    Frontend->>Backend: GET /history
    
    Backend->>Log: read_log_history()
    
    alt Log File Exists
        Log->>Backend: Read file line by line
        Backend->>Backend: Parse each JSON line
        Backend->>Backend: Collect sessions array
        Backend-->>Frontend: 200 OK<br/>[session objects]
    else Log File Not Found
        Backend-->>Frontend: 200 OK<br/>[] (empty array)
    else Read Error
        Backend-->>Frontend: 200 OK<br/>[] (empty array)
    end
    
    Frontend->>Frontend: Process history data
```

---

## API Endpoints

### POST /log

Logs a completed or skipped Pomodoro session.

**Request:**
```json
{
  "session_type": "work | short_break | long_break",
  "action": "complete | skip",
  "started_at": "2025-11-19T10:00:00.000Z",
  "ended_at": "2025-11-19T10:25:00.000Z"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Session logged successfully"
}
```

**Response (Error):**
```json
{
  "error": "Missing required field: session_type"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid data
- `500` - Server error

### GET /history

Retrieves all logged sessions.

**Response:**
```json
[
  {
    "session_type": "work",
    "action": "complete",
    "started_at": "2025-11-19T10:00:00.000Z",
    "ended_at": "2025-11-19T10:25:00.000Z"
  },
  {
    "session_type": "short_break",
    "action": "skip",
    "started_at": "2025-11-19T10:25:00.000Z",
    "ended_at": "2025-11-19T10:27:00.000Z"
  }
]
```

**Status Codes:**
- `200` - Success (returns empty array if no history)

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200` - Service is running

---

## Data Models

### Session Log Entry

Each line in `pomodoro_log.txt` is a JSON object:

```json
{
  "session_type": "work",
  "action": "complete",
  "started_at": "2025-11-19T10:00:00.000Z",
  "ended_at": "2025-11-19T10:25:00.000Z"
}
```

**Field Descriptions:**

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `session_type` | string | `work`, `short_break`, `long_break` | Type of session |
| `action` | string | `complete`, `skip` | How the session ended |
| `started_at` | string | ISO 8601 timestamp | When the session started |
| `ended_at` | string | ISO 8601 timestamp | When the session ended |

### Settings Object (localStorage)

Stored in browser's localStorage as `pomodoroSettings`:

```json
{
  "workDuration": 25,
  "shortBreakDuration": 5,
  "longBreakDuration": 15
}
```

**Field Constraints:**

| Field | Type | Range | Default |
|-------|------|-------|---------|
| `workDuration` | number | 1-60 minutes | 25 |
| `shortBreakDuration` | number | 1-30 minutes | 5 |
| `longBreakDuration` | number | 1-60 minutes | 15 |

---

## Frontend State Management

### State Transitions

```mermaid
stateDiagram-v2
    [*] --> Idle: App Loaded
    
    Idle --> Running: Start Button
    Running --> Paused: Pause Button
    Paused --> Running: Resume (Start Button)
    Running --> Idle: Reset Button
    Paused --> Idle: Reset Button
    
    Running --> SessionComplete: Timer = 00:00
    SessionComplete --> Idle: Auto-switch to Next Session
    
    Running --> SessionSkipped: Skip Button
    SessionSkipped --> Idle: Auto-switch to Next Session
    
    Idle --> Idle: Save Settings
    
    note right of Running
        Interval running
        Countdown active
        Start button disabled
    end note
    
    note right of Paused
        Interval cleared
        Timer frozen
        Resume available
    end note
    
    note right of Idle
        No interval
        Timer set to session duration
        All controls enabled
    end note
```

### Session Type State Machine

```mermaid
stateDiagram-v2
    [*] --> Work1
    
    Work1 --> ShortBreak1: Complete/Skip
    ShortBreak1 --> Work2: Complete/Skip
    
    Work2 --> ShortBreak2: Complete/Skip
    ShortBreak2 --> Work3: Complete/Skip
    
    Work3 --> ShortBreak3: Complete/Skip
    ShortBreak3 --> Work4: Complete/Skip
    
    Work4 --> LongBreak: Complete/Skip
    LongBreak --> Work1: Complete/Skip
    
    note right of Work1
        Session Count: 1
        Duration: workDuration
    end note
    
    note right of Work2
        Session Count: 2
        Duration: workDuration
    end note
    
    note right of Work3
        Session Count: 3
        Duration: workDuration
    end note
    
    note right of Work4
        Session Count: 4
        Duration: workDuration
    end note
    
    note right of ShortBreak1
        Duration: shortBreakDuration
    end note
    
    note right of LongBreak
        Duration: longBreakDuration
        Resets count to 0
    end note
```

---

## Running the Application

### Prerequisites
- Python 3.7+
- Flask
- Modern web browser

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Navigate to the app directory:
   ```bash
   cd pomodoro_app
   ```

3. Run the Flask server:
   ```bash
   python app.py
   ```

4. Open browser to:
   ```
   http://127.0.0.1:5000
   ```

### Project Structure

```
pomodoro_app/
├── app.py                 # Flask backend
├── pomodoro_log.txt      # Session logs (auto-generated)
├── static/
│   ├── style.css         # Styling
│   └── timer.js          # Frontend logic
└── templates/
    └── index.html        # Main UI
```

---

## Testing

The application includes comprehensive tests in `tests/test_app.py`:

- Route testing (/, /health, /log, /history)
- Validation testing
- Session logging
- Error handling

Run tests with:
```bash
pytest tests/
```

---

## Future Enhancements

Potential features for future development:

1. **Analytics Dashboard**: Visualize productivity patterns
2. **Sound Notifications**: Audio alerts for session completion
3. **Browser Notifications**: Desktop notifications when timer completes
4. **Statistics View**: Display session history in the UI
5. **Export Data**: Download session logs as CSV/JSON
6. **Dark Mode**: Theme switcher
7. **Multi-user Support**: User accounts and authentication
8. **Task Labels**: Associate sessions with specific tasks
9. **Progress Tracking**: Daily/weekly/monthly statistics
10. **Custom Session Cycles**: Configure number of sessions before long break

---

## License

This project is part of the GitHub Copilot Workshop 2025.

