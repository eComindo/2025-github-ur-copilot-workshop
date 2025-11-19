"""
Pytest fixtures and configuration for Pomodoro Timer tests
"""

import pytest
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pomodoro_app.app import app as flask_app


@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def tmp_log_file(tmp_path):
    """Create a temporary log file for testing."""
    log_file = tmp_path / "test_pomodoro_log.txt"
    return str(log_file)


@pytest.fixture
def sample_session_data():
    """Provide valid sample session data for testing."""
    return {
        'session_type': 'work',
        'action': 'complete',
        'started_at': '2025-11-19T10:00:00Z',
        'ended_at': '2025-11-19T10:25:00Z'
    }
