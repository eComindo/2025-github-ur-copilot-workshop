# GitHub Copilot Workshop - Pomodoro Timer App

This is a sample repository for Github Copilot Workshop in Github Universe Recap 2025, Jakarta, Indonesia.

**✅ Complete Implementation** - A fully functional Pomodoro Timer web application built with Python Flask, JavaScript, HTML, and CSS.

## 🚀 Quick Start

### 1. Setup Virtual Environment

#### On Windows (PowerShell):
```powershell
# Create virtual environment
uv venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

#### On macOS/Linux:
```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Run the Application

```powershell
cd pomodoro_app
python app.py
```

Then open your browser to: **http://127.0.0.1:5000**

### 3. Run Tests

```powershell
python -m pytest tests/ -v --cov=pomodoro_app
```

## 📋 Features

- ⏱️ **Pomodoro Timer** - 25-minute work sessions with 5-minute breaks
- 🔄 **Automatic Transitions** - Cycles through work and break sessions
- ⚙️ **Customizable Settings** - Adjust work and break durations
- 💾 **Session Logging** - Tracks all completed and skipped sessions
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 🎨 **Modern UI** - Dark theme with smooth animations
- ✅ **90% Test Coverage** - 26 comprehensive tests

## 📁 Project Structure

```
pomodoro_app/          # Main application directory
├── app.py            # Flask backend with API endpoints
├── static/
│   ├── style.css     # Application styling
│   └── timer.js      # Timer logic and frontend functionality
└── templates/
    └── index.html    # Main application page

tests/                # Comprehensive test suite
├── conftest.py       # Pytest configuration
└── test_app.py       # Backend tests (26 tests, 90% coverage)
```

## 📚 Documentation

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete implementation summary
- **[architecture.md](architecture.md)** - Architecture and design principles
- **[plan.md](plan.md)** - Detailed development plan
- **[Pomodoro_Technique.md](Pomodoro_Technique.md)** - About the Pomodoro Technique

## 🛠️ Technologies

- **Backend:** Python 3.13, Flask 3.0.0
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Testing:** pytest 7.4.3 with coverage
- **Package Management:** uv

## 📦 Installation Details

### uv

`uv` is an extremely fast Python package and project manager, written in Rust. 

Install from: https://docs.astral.sh/uv/#installation

### Virtual Environment

The `.venv` directory contains an isolated Python environment for this project.

**Activate:**
- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

**Deactivate:**
```bash
deactivate
```

## ✨ What's Included

- ✅ Fully functional Pomodoro timer
- ✅ Session logging with JSON Lines format
- ✅ Settings persistence via localStorage
- ✅ REST API for session tracking
- ✅ Comprehensive test suite
- ✅ Modern, accessible UI
- ✅ Complete documentation

---

**Status:** ✅ Production Ready | **Coverage:** 90% | **Tests:** 26/26 Passing