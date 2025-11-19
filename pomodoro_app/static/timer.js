/**
 * Pomodoro Timer - Frontend Logic
 * Handles timer countdown, session management, settings, and backend logging
 */

// ============================================================================
// State Management
// ============================================================================

let timerState = {
    minutes: 25,
    seconds: 0,
    isRunning: false,
    isPaused: false,
    currentSession: 'work', // 'work', 'short_break', 'long_break'
    sessionCount: 1, // Tracks completed work sessions (1-4)
    intervalId: null,
    sessionStartTime: null,
    settings: {
        workDuration: 25,
        shortBreakDuration: 5,
        longBreakDuration: 15
    }
};

// ============================================================================
// DOM Elements
// ============================================================================

const timerDisplay = document.getElementById('timer-display');
const sessionTypeEl = document.getElementById('session-type');
const sessionCounterEl = document.getElementById('session-counter');
const startBtn = document.getElementById('start-btn');
const pauseBtn = document.getElementById('pause-btn');
const skipBtn = document.getElementById('skip-btn');
const resetBtn = document.getElementById('reset-btn');
const saveSettingsBtn = document.getElementById('save-settings-btn');
const statusMessage = document.getElementById('status-message');
const workDurationInput = document.getElementById('work-duration');
const shortBreakInput = document.getElementById('short-break-duration');
const longBreakInput = document.getElementById('long-break-duration');

// ============================================================================
// Initialization
// ============================================================================

function initTimer() {
    loadSettings();
    updateTimerDisplay(timerState.minutes, timerState.seconds);
    updateSessionInfo();
    attachEventListeners();
}

function attachEventListeners() {
    startBtn.addEventListener('click', startTimer);
    pauseBtn.addEventListener('click', pauseTimer);
    skipBtn.addEventListener('click', skipSession);
    resetBtn.addEventListener('click', resetTimer);
    saveSettingsBtn.addEventListener('click', saveSettings);
}

// ============================================================================
// Settings Management
// ============================================================================

function loadSettings() {
    const savedSettings = localStorage.getItem('pomodoroSettings');

    if (savedSettings) {
        try {
            const settings = JSON.parse(savedSettings);
            timerState.settings.workDuration = settings.workDuration || 25;
            timerState.settings.shortBreakDuration = settings.shortBreakDuration || 5;
            timerState.settings.longBreakDuration = settings.longBreakDuration || 15;
        } catch (e) {
            console.error('Failed to load settings:', e);
            setDefaultSettings();
        }
    } else {
        setDefaultSettings();
    }

    // Update input fields
    workDurationInput.value = timerState.settings.workDuration;
    shortBreakInput.value = timerState.settings.shortBreakDuration;
    longBreakInput.value = timerState.settings.longBreakDuration;

    // Set initial timer based on current session
    if (timerState.currentSession === 'work') {
        timerState.minutes = timerState.settings.workDuration;
    } else if (timerState.currentSession === 'short_break') {
        timerState.minutes = timerState.settings.shortBreakDuration;
    } else {
        timerState.minutes = timerState.settings.longBreakDuration;
    }
    timerState.seconds = 0;
}

function setDefaultSettings() {
    timerState.settings = {
        workDuration: 25,
        shortBreakDuration: 5,
        longBreakDuration: 15
    };
}

function saveSettings() {
    const workDuration = parseInt(workDurationInput.value);
    const shortBreakDuration = parseInt(shortBreakInput.value);
    const longBreakDuration = parseInt(longBreakInput.value);

    // Validate inputs
    if (workDuration < 1 || workDuration > 60 ||
        shortBreakDuration < 1 || shortBreakDuration > 30 ||
        longBreakDuration < 1 || longBreakDuration > 60) {
        showStatusMessage('Invalid duration values. Please check your inputs.', 'error');
        return;
    }

    timerState.settings = {
        workDuration,
        shortBreakDuration,
        longBreakDuration
    };

    // Save to localStorage
    localStorage.setItem('pomodoroSettings', JSON.stringify(timerState.settings));

    // If timer is not running, update the current session duration
    if (!timerState.isRunning) {
        if (timerState.currentSession === 'work') {
            timerState.minutes = workDuration;
        } else if (timerState.currentSession === 'short_break') {
            timerState.minutes = shortBreakDuration;
        } else {
            timerState.minutes = longBreakDuration;
        }
        timerState.seconds = 0;
        updateTimerDisplay(timerState.minutes, timerState.seconds);
    }

    showStatusMessage('Settings saved successfully!', 'success');
}

// ============================================================================
// Timer Control Functions
// ============================================================================

function startTimer() {
    if (!timerState.isRunning) {
        timerState.isRunning = true;
        timerState.isPaused = false;
        timerState.sessionStartTime = new Date().toISOString();

        timerState.intervalId = setInterval(tick, 1000);

        // Update button states
        startBtn.disabled = true;
        pauseBtn.disabled = false;

        showStatusMessage('Timer started!', 'info');
    }
}

function pauseTimer() {
    if (timerState.isRunning && !timerState.isPaused) {
        clearInterval(timerState.intervalId);
        timerState.isPaused = true;
        timerState.isRunning = false;

        // Update button states
        startBtn.disabled = false;
        startBtn.textContent = 'Resume';
        pauseBtn.disabled = true;

        showStatusMessage('Timer paused', 'info');
    }
}

function resumeTimer() {
    if (timerState.isPaused) {
        timerState.isRunning = true;
        timerState.isPaused = false;

        timerState.intervalId = setInterval(tick, 1000);

        // Update button states
        startBtn.disabled = true;
        startBtn.textContent = 'Start';
        pauseBtn.disabled = false;

        showStatusMessage('Timer resumed!', 'info');
    }
}

function skipSession() {
    if (timerState.isRunning) {
        const sessionEndTime = new Date().toISOString();

        // Log the skipped session
        logSession(timerState.currentSession, 'skip', timerState.sessionStartTime, sessionEndTime);

        stopTimer();
        switchToNextSession();
        showStatusMessage('Session skipped!', 'info');
    } else {
        showStatusMessage('Start the timer before skipping', 'warning');
    }
}

function resetTimer() {
    stopTimer();

    // Reset to initial state
    timerState.currentSession = 'work';
    timerState.sessionCount = 1;
    timerState.isPaused = false;
    timerState.minutes = timerState.settings.workDuration;
    timerState.seconds = 0;

    updateTimerDisplay(timerState.minutes, timerState.seconds);
    updateSessionInfo();

    // Reset button states
    startBtn.disabled = false;
    startBtn.textContent = 'Start';
    pauseBtn.disabled = true;

    showStatusMessage('Timer reset!', 'info');
}

function stopTimer() {
    if (timerState.intervalId) {
        clearInterval(timerState.intervalId);
        timerState.intervalId = null;
    }
    timerState.isRunning = false;
}

// ============================================================================
// Timer Mechanics
// ============================================================================

function tick() {
    if (timerState.seconds === 0) {
        if (timerState.minutes === 0) {
            // Timer completed
            handleSessionComplete();
            return;
        }
        timerState.minutes--;
        timerState.seconds = 59;
    } else {
        timerState.seconds--;
    }

    updateTimerDisplay(timerState.minutes, timerState.seconds);
}

function handleSessionComplete() {
    stopTimer();

    const sessionEndTime = new Date().toISOString();

    // Log the completed session
    logSession(timerState.currentSession, 'complete', timerState.sessionStartTime, sessionEndTime);

    showStatusMessage('Session completed! Great job!', 'success');

    // Move to next session
    switchToNextSession();
}

// ============================================================================
// Session Management
// ============================================================================

function switchToNextSession() {
    const nextSession = determineNextSession();
    switchSession(nextSession);
}

function determineNextSession() {
    if (timerState.currentSession === 'work') {
        // After work session, go to break
        if (timerState.sessionCount >= 4) {
            return 'long_break';
        } else {
            return 'short_break';
        }
    } else {
        // After break, go back to work
        if (timerState.currentSession === 'long_break') {
            // Reset session count after long break
            timerState.sessionCount = 0;
        }
        return 'work';
    }
}

function switchSession(sessionType) {
    timerState.currentSession = sessionType;

    // Set duration based on session type
    if (sessionType === 'work') {
        timerState.minutes = timerState.settings.workDuration;
        incrementSessionCount();
    } else if (sessionType === 'short_break') {
        timerState.minutes = timerState.settings.shortBreakDuration;
    } else if (sessionType === 'long_break') {
        timerState.minutes = timerState.settings.longBreakDuration;
    }

    timerState.seconds = 0;

    updateTimerDisplay(timerState.minutes, timerState.seconds);
    updateSessionInfo();

    // Reset button states
    startBtn.disabled = false;
    startBtn.textContent = 'Start';
    pauseBtn.disabled = true;
}

function incrementSessionCount() {
    if (timerState.currentSession === 'work') {
        timerState.sessionCount++;
        if (timerState.sessionCount > 4) {
            timerState.sessionCount = 1;
        }
    }
}

// ============================================================================
// UI Update Functions
// ============================================================================

function updateTimerDisplay(minutes, seconds) {
    const formattedMinutes = String(minutes).padStart(2, '0');
    const formattedSeconds = String(seconds).padStart(2, '0');
    timerDisplay.querySelector('.time').textContent = `${formattedMinutes}:${formattedSeconds}`;
}

function updateSessionInfo() {
    // Update session type text
    let sessionText = '';
    if (timerState.currentSession === 'work') {
        sessionText = 'Work Session';
        timerDisplay.className = 'timer-display work';
    } else if (timerState.currentSession === 'short_break') {
        sessionText = 'Short Break';
        timerDisplay.className = 'timer-display short-break';
    } else if (timerState.currentSession === 'long_break') {
        sessionText = 'Long Break';
        timerDisplay.className = 'timer-display long-break';
    }

    sessionTypeEl.textContent = sessionText;

    // Update session counter
    if (timerState.currentSession === 'work') {
        sessionCounterEl.textContent = `Session ${timerState.sessionCount} of 4`;
    } else {
        sessionCounterEl.textContent = 'Take a break!';
    }
}

function showStatusMessage(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';

    // Auto-hide after 3 seconds
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 3000);
}

// ============================================================================
// Backend Integration - API Communication
// ============================================================================

async function logSession(sessionType, action, startedAt, endedAt) {
    const sessionData = {
        session_type: sessionType,
        action: action,
        started_at: startedAt,
        ended_at: endedAt
    };

    try {
        const response = await fetch('/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sessionData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            handleLogError(errorData.error || 'Failed to log session');
        }
    } catch (error) {
        handleLogError(error.message);
    }
}

async function fetchHistory() {
    try {
        const response = await fetch('/history');

        if (!response.ok) {
            throw new Error('Failed to fetch history');
        }

        const history = await response.json();
        return history;
    } catch (error) {
        console.error('Error fetching history:', error);
        return [];
    }
}

function handleLogError(error) {
    console.error('Logging error:', error);
    // Don't show error to user unless critical - timer should continue working
}

// ============================================================================
// Initialize on page load
// ============================================================================

document.addEventListener('DOMContentLoaded', initTimer);

// Handle Resume button functionality
startBtn.addEventListener('click', () => {
    if (timerState.isPaused) {
        resumeTimer();
    }
});
