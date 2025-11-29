// Pomodoro Timer JavaScript Implementation

class PomodoroTimer {
    constructor() {
        // Timer state
        this.isRunning = false;
        this.isPaused = false;
        this.currentTime = 0; // in seconds
        this.intervalId = null;
        this.tickIntervalId = null;
        
        // Session management
        this.currentSession = 1;
        this.maxSessions = 4;
        this.sessionType = 'work'; // 'work', 'short_break', 'long_break'
        
        // Duration settings (in seconds)
        this.settings = {
            workDuration: 25 * 60,
            shortBreakDuration: 5 * 60,
            longBreakDuration: 15 * 60,
            theme: 'light',
            soundStart: true,
            soundEnd: true,
            soundTick: false
        };
        
        // Audio context for sounds
        this.audioContext = null;
        
        // DOM elements
        this.initializeElements();
        this.loadSettings();
        this.applyTheme();
        this.resetTimer();
        this.bindEvents();
    }
    
    initializeElements() {
        this.timerTimeEl = document.getElementById('timer-time');
        this.timerStatusEl = document.getElementById('timer-status');
        this.sessionTypeEl = document.getElementById('session-type');
        this.sessionCountEl = document.getElementById('session-count');
        this.timerCircleEl = document.querySelector('.timer-circle');
        this.progressDotsEl = document.getElementById('progress-dots');
        
        // Buttons
        this.startBtn = document.getElementById('start-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.skipBtn = document.getElementById('skip-btn');
        this.settingsBtn = document.getElementById('settings-btn');
        
        // Settings panel
        this.settingsPanel = document.getElementById('settings-panel');
        this.workDurationInput = document.getElementById('work-duration');
        this.shortBreakInput = document.getElementById('short-break-duration');
        this.longBreakInput = document.getElementById('long-break-duration');
        this.saveSettingsBtn = document.getElementById('save-settings-btn');
        this.cancelSettingsBtn = document.getElementById('cancel-settings-btn');
        
        // New settings elements
        this.themeSelect = document.getElementById('theme-select');
        this.soundStartCheckbox = document.getElementById('sound-start');
        this.soundEndCheckbox = document.getElementById('sound-end');
        this.soundTickCheckbox = document.getElementById('sound-tick');
        
        // Preset buttons
        this.workPresetBtns = document.querySelectorAll('.preset-buttons [data-duration]');
        this.breakPresetBtns = document.querySelectorAll('.preset-buttons [data-break-duration]');
    }
    
    loadSettings() {
        // Load settings from localStorage if available
        const saved = localStorage.getItem('pomodoroSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            this.settings.workDuration = settings.workDuration * 60;
            this.settings.shortBreakDuration = settings.shortBreakDuration * 60;
            this.settings.longBreakDuration = settings.longBreakDuration * 60;
            this.settings.theme = settings.theme || 'light';
            this.settings.soundStart = settings.soundStart !== undefined ? settings.soundStart : true;
            this.settings.soundEnd = settings.soundEnd !== undefined ? settings.soundEnd : true;
            this.settings.soundTick = settings.soundTick !== undefined ? settings.soundTick : false;
        }
        
        // Update input fields
        this.workDurationInput.value = Math.floor(this.settings.workDuration / 60);
        this.shortBreakInput.value = Math.floor(this.settings.shortBreakDuration / 60);
        this.longBreakInput.value = Math.floor(this.settings.longBreakDuration / 60);
        
        // Update theme select
        this.themeSelect.value = this.settings.theme;
        
        // Update sound checkboxes
        this.soundStartCheckbox.checked = this.settings.soundStart;
        this.soundEndCheckbox.checked = this.settings.soundEnd;
        this.soundTickCheckbox.checked = this.settings.soundTick;
        
        // Update preset button states
        this.updatePresetButtons();
    }
    
    saveSettings() {
        // Get values from preset buttons or inputs
        const workDuration = parseInt(this.workDurationInput.value);
        const shortBreakDuration = parseInt(this.shortBreakInput.value);
        const longBreakDuration = parseInt(this.longBreakInput.value);
        
        const settings = {
            workDuration: workDuration,
            shortBreakDuration: shortBreakDuration,
            longBreakDuration: longBreakDuration,
            theme: this.themeSelect.value,
            soundStart: this.soundStartCheckbox.checked,
            soundEnd: this.soundEndCheckbox.checked,
            soundTick: this.soundTickCheckbox.checked
        };
        
        this.settings.workDuration = settings.workDuration * 60;
        this.settings.shortBreakDuration = settings.shortBreakDuration * 60;
        this.settings.longBreakDuration = settings.longBreakDuration * 60;
        this.settings.theme = settings.theme;
        this.settings.soundStart = settings.soundStart;
        this.settings.soundEnd = settings.soundEnd;
        this.settings.soundTick = settings.soundTick;
        
        localStorage.setItem('pomodoroSettings', JSON.stringify(settings));
        this.applyTheme();
        this.hideSettings();
        this.resetTimer();
    }
    
    bindEvents() {
        this.startBtn.addEventListener('click', () => this.toggleTimer());
        this.resetBtn.addEventListener('click', () => this.resetTimer());
        this.skipBtn.addEventListener('click', () => this.skipSession());
        this.settingsBtn.addEventListener('click', () => this.showSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        this.cancelSettingsBtn.addEventListener('click', () => this.hideSettings());
        
        // Bind preset button events
        this.workPresetBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.workPresetBtns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.workDurationInput.value = e.target.dataset.duration;
            });
        });
        
        this.breakPresetBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.breakPresetBtns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.shortBreakInput.value = e.target.dataset.breakDuration;
            });
        });
    }
    
    getCurrentDuration() {
        if (this.sessionType === 'work') {
            return this.settings.workDuration;
        } else if (this.sessionType === 'short_break') {
            return this.settings.shortBreakDuration;
        } else {
            return this.settings.longBreakDuration;
        }
    }
    
    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    updateDisplay() {
        this.timerTimeEl.textContent = this.formatTime(this.currentTime);
        
        // Update session info
        if (this.sessionType === 'work') {
            this.sessionTypeEl.textContent = 'Work Session';
            this.sessionCountEl.textContent = `Session ${this.currentSession} of ${this.maxSessions}`;
            this.timerCircleEl.className = 'timer-circle active';
        } else if (this.sessionType === 'short_break') {
            this.sessionTypeEl.textContent = 'Short Break';
            this.sessionCountEl.textContent = `After Session ${this.currentSession - 1}`;
            this.timerCircleEl.className = 'timer-circle break';
        } else {
            this.sessionTypeEl.textContent = 'Long Break';
            this.sessionCountEl.textContent = `After ${this.maxSessions} Sessions`;
            this.timerCircleEl.className = 'timer-circle break';
        }
        
        // Update status
        if (!this.isRunning && this.currentTime === this.getCurrentDuration()) {
            this.timerStatusEl.textContent = 'Ready to start';
        } else if (this.isRunning) {
            this.timerStatusEl.textContent = 'Focus time';
        } else if (this.isPaused) {
            this.timerStatusEl.textContent = 'Paused';
        } else {
            this.timerStatusEl.textContent = 'Ready';
        }
        
        // Update progress dots
        this.updateProgressDots();
    }
    
    updateProgressDots() {
        const dots = this.progressDotsEl.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            const sessionNum = index + 1;
            if (sessionNum < this.currentSession) {
                dot.className = 'dot completed';
            } else if (sessionNum === this.currentSession && this.sessionType === 'work') {
                dot.className = 'dot active';
            } else {
                dot.className = 'dot';
            }
        });
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
        this.startBtn.textContent = 'Pause';
        
        // Play start sound
        if (this.settings.soundStart) {
            this.playSound('start');
        }
        
        this.intervalId = setInterval(() => {
            if (this.currentTime > 0) {
                this.currentTime--;
                this.updateDisplay();
                
                // Play tick sound if enabled
                if (this.settings.soundTick) {
                    this.playSound('tick');
                }
            } else {
                this.completeSession();
            }
        }, 1000);
        
        this.updateDisplay();
    }
    
    pauseTimer() {
        this.isRunning = false;
        this.isPaused = true;
        this.startBtn.textContent = 'Start';
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        this.updateDisplay();
    }
    
    resetTimer() {
        this.isRunning = false;
        this.isPaused = false;
        this.startBtn.textContent = 'Start';
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        this.currentTime = this.getCurrentDuration();
        this.updateDisplay();
    }
    
    async completeSession() {
        this.pauseTimer();
        
        // Play end sound
        if (this.settings.soundEnd) {
            this.playSound('end');
        }
        
        // Log the completed session
        await this.logSession('completed');
        
        // Play notification sound (optional - browser notification)
        this.showNotification(`${this.sessionType === 'work' ? 'Work session' : 'Break'} completed!`);
        
        // Move to next session
        this.nextSession();
    }
    
    async skipSession() {
        if (this.isRunning || this.isPaused) {
            this.pauseTimer();
            
            // Log the skipped session
            await this.logSession('skipped');
            
            // Move to next session
            this.nextSession();
        }
    }
    
    nextSession() {
        if (this.sessionType === 'work') {
            // After work session
            if (this.currentSession >= this.maxSessions) {
                // Long break after 4 sessions
                this.sessionType = 'long_break';
            } else {
                // Short break
                this.sessionType = 'short_break';
            }
        } else {
            // After break, start next work session
            if (this.sessionType === 'short_break') {
                this.currentSession++;
            } else if (this.sessionType === 'long_break') {
                this.currentSession = 1; // Reset for next cycle
            }
            this.sessionType = 'work';
        }
        
        this.resetTimer();
    }
    
    async logSession(action) {
        try {
            const sessionData = {
                session_type: this.sessionType,
                action: action,
                session_number: this.currentSession
            };
            
            const response = await fetch('/log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(sessionData)
            });
            
            if (!response.ok) {
                console.error('Failed to log session:', response.statusText);
            }
        } catch (error) {
            console.error('Error logging session:', error);
        }
    }
    
    showNotification(message) {
        // Browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Pomodoro Timer', {
                body: message,
                icon: '/static/favicon.ico' // Optional
            });
        } else if ('Notification' in window && Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification('Pomodoro Timer', {
                        body: message,
                        icon: '/static/favicon.ico'
                    });
                }
            });
        }
        
        // Visual notification (simple alert for now)
        // You could replace this with a custom modal
        setTimeout(() => {
            alert(message);
        }, 100);
    }
    
    showSettings() {
        this.settingsPanel.style.display = 'block';
    }
    
    hideSettings() {
        this.settingsPanel.style.display = 'none';
    }
    
    applyTheme() {
        // Remove all theme classes
        document.body.classList.remove('light-theme', 'dark-theme', 'focus-theme');
        // Add the selected theme class
        document.body.classList.add(`${this.settings.theme}-theme`);
    }
    
    updatePresetButtons() {
        const workMinutes = Math.floor(this.settings.workDuration / 60);
        const breakMinutes = Math.floor(this.settings.shortBreakDuration / 60);
        
        // Update work preset buttons
        this.workPresetBtns.forEach(btn => {
            if (parseInt(btn.dataset.duration) === workMinutes) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update break preset buttons
        this.breakPresetBtns.forEach(btn => {
            if (parseInt(btn.dataset.breakDuration) === breakMinutes) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }
    
    playSound(type) {
        // Simple beep sounds using Web Audio API
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        // Different frequencies for different sounds
        switch(type) {
            case 'start':
                oscillator.frequency.value = 800;
                gainNode.gain.value = 0.1;
                oscillator.start();
                oscillator.stop(this.audioContext.currentTime + 0.1);
                break;
            case 'end':
                oscillator.frequency.value = 600;
                gainNode.gain.value = 0.1;
                oscillator.start();
                oscillator.stop(this.audioContext.currentTime + 0.3);
                break;
            case 'tick':
                oscillator.frequency.value = 400;
                gainNode.gain.value = 0.02;
                oscillator.start();
                oscillator.stop(this.audioContext.currentTime + 0.05);
                break;
        }
    }
}

// Initialize the timer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
});