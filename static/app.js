// Pomodoro Timer JavaScript Logic

class PomodoroTimer {
    constructor() {
        this.isRunning = false;
        this.isPaused = false;
        this.currentSession = 'pomodoro'; // 'pomodoro', 'shortBreak', 'longBreak'
        this.sessionNumber = 1;
        this.completedPomodoros = 0;
        
        // Timer settings (in minutes)
        this.settings = {
            pomodoro: 25,
            shortBreak: 5,
            longBreak: 15
        };
        
        // Timer state
        this.timeLeft = this.settings.pomodoro * 60; // in seconds
        this.totalTime = this.settings.pomodoro * 60;
        this.timerInterval = null;
        this.sessionStartTime = null;
        
        // DOM elements
        this.timerMinutes = document.getElementById('timer-minutes');
        this.timerSeconds = document.getElementById('timer-seconds');
        this.sessionLabel = document.getElementById('session-label');
        this.sessionNumber = document.getElementById('session-number');
        this.startPauseBtn = document.getElementById('start-pause-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.skipBtn = document.getElementById('skip-btn');
        this.statusMessage = document.getElementById('status-message');
        this.progressRing = document.querySelector('.progress-ring-progress');
        
        // Settings inputs
        this.pomodoroDurationInput = document.getElementById('pomodoro-duration');
        this.breakDurationInput = document.getElementById('break-duration');
        this.longBreakDurationInput = document.getElementById('long-break-duration');
        
        // Initialize
        this.initializeTimer();
        this.bindEvents();
        this.updateDisplay();
    }
    
    initializeTimer() {
        this.timeLeft = this.settings[this.currentSession] * 60;
        this.totalTime = this.settings[this.currentSession] * 60;
        this.updateDisplay();
        this.updateProgressRing();
    }
    
    bindEvents() {
        this.startPauseBtn.addEventListener('click', () => this.toggleTimer());
        this.resetBtn.addEventListener('click', () => this.resetTimer());
        this.skipBtn.addEventListener('click', () => this.skipSession());
        
        // Settings change events
        this.pomodoroDurationInput.addEventListener('change', () => this.updateSettings());
        this.breakDurationInput.addEventListener('change', () => this.updateSettings());
        this.longBreakDurationInput.addEventListener('change', () => this.updateSettings());
    }
    
    updateSettings() {
        this.settings.pomodoro = parseInt(this.pomodoroDurationInput.value);
        this.settings.shortBreak = parseInt(this.breakDurationInput.value);
        this.settings.longBreak = parseInt(this.longBreakDurationInput.value);
        
        if (!this.isRunning) {
            this.initializeTimer();
        }
    }
    
    toggleTimer() {
        if (this.isRunning) {
            this.pauseTimer();
        } else {
            this.startTimer();
        }
    }
    
    startTimer() {
        this.isRunning = true;
        this.isPaused = false;
        this.sessionStartTime = this.sessionStartTime || new Date();
        
        this.startPauseBtn.textContent = 'Pause';
        this.startPauseBtn.className = 'btn pause';
        this.statusMessage.textContent = `${this.getSessionDisplayName()} in progress...`;
        
        this.timerInterval = setInterval(() => {
            this.tick();
        }, 1000);
    }
    
    pauseTimer() {
        this.isRunning = false;
        this.isPaused = true;
        
        this.startPauseBtn.textContent = 'Resume';
        this.startPauseBtn.className = 'btn primary';
        this.statusMessage.textContent = `${this.getSessionDisplayName()} paused`;
        
        clearInterval(this.timerInterval);
    }
    
    resetTimer() {
        this.isRunning = false;
        this.isPaused = false;
        
        this.startPauseBtn.textContent = 'Start';
        this.startPauseBtn.className = 'btn primary';
        this.statusMessage.textContent = `Ready to start your ${this.getSessionDisplayName()}!`;
        
        clearInterval(this.timerInterval);
        this.sessionStartTime = null;
        this.initializeTimer();
    }
    
    skipSession() {
        if (this.isRunning || this.isPaused) {
            // Log the skipped session
            this.logSession('skipped');
        }
        
        this.completeSession(true);
    }
    
    tick() {
        this.timeLeft--;
        
        if (this.timeLeft <= 0) {
            // Session completed naturally
            this.logSession('completed');
            this.completeSession(false);
        } else {
            this.updateDisplay();
            this.updateProgressRing();
        }
    }
    
    completeSession(wasSkipped = false) {
        this.isRunning = false;
        this.isPaused = false;
        clearInterval(this.timerInterval);
        
        if (this.currentSession === 'pomodoro' && !wasSkipped) {
            this.completedPomodoros++;
        }
        
        // Determine next session type
        this.switchToNextSession();
        
        // Reset UI
        this.startPauseBtn.textContent = 'Start';
        this.startPauseBtn.className = 'btn primary';
        this.statusMessage.textContent = `Ready to start your ${this.getSessionDisplayName()}!`;
        
        // Play notification sound (optional)
        this.playNotificationSound();
        
        // Show browser notification (optional)
        this.showBrowserNotification();
        
        this.sessionStartTime = null;
        this.initializeTimer();
    }
    
    switchToNextSession() {
        if (this.currentSession === 'pomodoro') {
            // After pomodoro, go to break
            if (this.completedPomodoros % 4 === 0 && this.completedPomodoros > 0) {
                this.currentSession = 'longBreak';
            } else {
                this.currentSession = 'shortBreak';
            }
        } else {
            // After break, go back to pomodoro
            this.currentSession = 'pomodoro';
            this.sessionNumber++;
        }
        
        this.updateSessionDisplay();
    }
    
    updateSessionDisplay() {
        this.sessionLabel.textContent = this.getSessionDisplayName();
        this.sessionNumber.textContent = this.sessionNumber;
        
        // Update progress ring color based on session type
        const color = this.currentSession === 'pomodoro' ? '#ff6b6b' : '#4ecdc4';
        this.progressRing.setAttribute('stroke', color);
    }
    
    getSessionDisplayName() {
        const names = {
            'pomodoro': 'Pomodoro Session',
            'shortBreak': 'Short Break',
            'longBreak': 'Long Break'
        };
        return names[this.currentSession];
    }
    
    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        
        this.timerMinutes.textContent = minutes.toString().padStart(2, '0');
        this.timerSeconds.textContent = seconds.toString().padStart(2, '0');
        
        // Update document title
        document.title = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')} - ${this.getSessionDisplayName()}`;
    }
    
    updateProgressRing() {
        const circumference = 2 * Math.PI * 140; // radius = 140
        const progress = (this.totalTime - this.timeLeft) / this.totalTime;
        const offset = circumference - (progress * circumference);
        
        this.progressRing.style.strokeDashoffset = offset;
    }
    
    playNotificationSound() {
        // Create a simple notification sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.1);
            gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            console.log('Audio notification not available:', error);
        }
    }
    
    showBrowserNotification() {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Pomodoro Timer', {
                body: `${this.getSessionDisplayName()} completed!`,
                icon: '/favicon.ico'
            });
        }
    }
    
    async logSession(status) {
        if (!this.sessionStartTime) return;
        
        const sessionData = {
            session_type: this.currentSession,
            start_time: this.sessionStartTime.toISOString(),
            end_time: new Date().toISOString(),
            status: status,
            duration_minutes: Math.ceil((new Date() - this.sessionStartTime) / 60000)
        };
        
        try {
            const response = await fetch('/log-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(sessionData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Session logged:', result);
        } catch (error) {
            console.error('Error logging session:', error);
        }
    }
}

// Initialize the timer when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const timer = new PomodoroTimer();
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Make timer globally accessible for debugging
    window.pomodoroTimer = timer;
});