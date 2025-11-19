# Pomodoro App

This directory contains the Pomodoro Timer web application.

## Running the Application

From the project root, activate the virtual environment and run:

```powershell
cd pomodoro_app
python app.py
```

Then open your browser to: http://127.0.0.1:5000

## Application Structure

- `app.py` - Flask backend with API endpoints
- `static/` - Static assets (CSS, JavaScript)
  - `style.css` - Application styling
  - `timer.js` - Timer logic and frontend functionality
- `templates/` - HTML templates
  - `index.html` - Main application page
- `pomodoro_log.txt` - Session logs (created automatically)
