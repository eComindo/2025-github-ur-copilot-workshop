import pytest
import json
import os
import tempfile
import shutil
from app import app, LOG_FILE


@pytest.fixture(scope='function')
def temp_dir():
    """Create a temporary directory for integration tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def integration_client(temp_dir):
    """Create a test client with temporary file system."""
    app.config['TESTING'] = True
    
    # Use temporary log file with unique name per test
    import time
    temp_log_file = os.path.join(temp_dir, f'test_pomodoro_log_{int(time.time()*1000000)}.json')
    original_log_file = LOG_FILE
    
    # Patch the LOG_FILE constant
    import app as app_module
    app_module.LOG_FILE = temp_log_file
    
    with app.test_client() as client:
        yield client, temp_log_file
    
    # Cleanup and restore original LOG_FILE
    if os.path.exists(temp_log_file):
        os.unlink(temp_log_file)
    app_module.LOG_FILE = original_log_file


class TestBasicIntegration:
    """Basic integration tests for essential workflows."""

    def test_complete_session_workflow(self, integration_client):
        """Test a basic session logging workflow."""
        client, log_file = integration_client
        
        # Initial state - no history
        response = client.get('/session-history')
        assert response.status_code == 200
        assert response.get_json() == []
        
        # Log a pomodoro session
        pomodoro_data = {
            "session_type": "pomodoro",
            "start_time": "2025-11-28T08:00:00.000Z",
            "end_time": "2025-11-28T08:25:00.000Z",
            "status": "completed",
            "duration_minutes": 25
        }
        
        response = client.post('/log-session',
                             data=json.dumps(pomodoro_data),
                             content_type='application/json')
        assert response.status_code == 200
        
        # Verify log file was created
        assert os.path.exists(log_file)
        
        # Retrieve history
        response = client.get('/session-history')
        assert response.status_code == 200
        
        history = response.get_json()
        assert len(history) == 1
        assert history[0]['session_type'] == 'pomodoro'
        assert history[0]['status'] == 'completed'

    def test_multiple_sessions_logging(self, integration_client):
        """Test logging multiple sessions."""
        client, log_file = integration_client
        
        sessions = [
            {
                "session_type": "pomodoro",
                "start_time": "2025-11-28T09:00:00.000Z",
                "end_time": "2025-11-28T09:25:00.000Z",
                "status": "completed",
                "duration_minutes": 25
            },
            {
                "session_type": "shortBreak",
                "start_time": "2025-11-28T09:25:00.000Z",
                "end_time": "2025-11-28T09:30:00.000Z",
                "status": "completed",
                "duration_minutes": 5
            }
        ]
        
        # Log sessions
        for session in sessions:
            response = client.post('/log-session',
                                 data=json.dumps(session),
                                 content_type='application/json')
            assert response.status_code == 200
        
        # Verify all sessions were logged
        response = client.get('/session-history')
        assert response.status_code == 200
        history = response.get_json()
        assert len(history) == 2
        
        # Verify session order and data
        assert history[0]['session_type'] == 'pomodoro'
        assert history[1]['session_type'] == 'shortBreak'

    def test_error_handling_with_recovery(self, integration_client):
        """Test that invalid data doesn't corrupt the log file."""
        client, log_file = integration_client
        
        # Log a valid session first
        valid_session = {
            "session_type": "pomodoro",
            "start_time": "2025-11-28T11:00:00.000Z",
            "end_time": "2025-11-28T11:25:00.000Z",
            "status": "completed",
            "duration_minutes": 25
        }
        
        response = client.post('/log-session',
                             data=json.dumps(valid_session),
                             content_type='application/json')
        assert response.status_code == 200
        
        # Try to log invalid session
        invalid_session = {"invalid": "data"}
        response = client.post('/log-session',
                             data=json.dumps(invalid_session),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Verify that the valid session is still there
        response = client.get('/session-history')
        assert response.status_code == 200
        history = response.get_json()
        assert len(history) == 1
        assert history[0]['session_type'] == 'pomodoro'

    def test_file_system_operations(self, integration_client):
        """Test file system operations."""
        client, log_file = integration_client
        
        # Ensure log file doesn't exist initially
        assert not os.path.exists(log_file)
        
        # Log a session to trigger file creation
        session = {
            "session_type": "pomodoro",
            "start_time": "2025-11-28T12:00:00.000Z",
            "end_time": "2025-11-28T12:25:00.000Z",
            "status": "completed",
            "duration_minutes": 25
        }
        
        response = client.post('/log-session',
                             data=json.dumps(session),
                             content_type='application/json')
        assert response.status_code == 200
        
        # Verify file was created and is valid JSON
        assert os.path.exists(log_file)
        with open(log_file, 'r') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]['session_type'] == 'pomodoro'

    def test_json_format_integrity(self, integration_client):
        """Test that JSON file maintains proper format."""
        client, log_file = integration_client
        
        # Log a session
        session = {
            "session_type": "pomodoro",
            "start_time": "2025-11-28T13:00:00.000Z",
            "end_time": "2025-11-28T13:25:00.000Z",
            "status": "completed",
            "duration_minutes": 25
        }
        
        response = client.post('/log-session',
                             data=json.dumps(session),
                             content_type='application/json')
        assert response.status_code == 200
        
        # Verify JSON file format
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Should be valid JSON
        parsed_data = json.loads(content)
        assert isinstance(parsed_data, list)
        assert len(parsed_data) == 1
        
        # Verify indentation (should be formatted nicely)
        assert '  {' in content  # Indicates proper indentation
        
        # Verify session structure
        session_data = parsed_data[0]
        assert 'session_type' in session_data
        assert 'start_time' in session_data
        assert 'end_time' in session_data
        assert 'status' in session_data


class TestSessionTypes:
    """Test different session types and statuses."""

    def test_all_session_types(self, integration_client):
        """Test logging all different session types."""
        client, log_file = integration_client
        
        session_types = ['pomodoro', 'shortBreak', 'longBreak']
        
        for i, session_type in enumerate(session_types):
            session = {
                "session_type": session_type,
                "start_time": f"2025-11-28T14:{i:02d}:00.000Z",
                "end_time": f"2025-11-28T14:{i+1:02d}:00.000Z",
                "status": "completed",
                "duration_minutes": 25 if session_type == 'pomodoro' else (5 if session_type == 'shortBreak' else 15)
            }
            
            response = client.post('/log-session',
                                 data=json.dumps(session),
                                 content_type='application/json')
            assert response.status_code == 200
        
        # Verify all sessions were logged
        response = client.get('/session-history')
        assert response.status_code == 200
        history = response.get_json()
        assert len(history) == 3
        
        # Verify session types
        logged_types = [session['session_type'] for session in history]
        assert logged_types == session_types

    def test_all_session_statuses(self, integration_client):
        """Test logging all different session statuses."""
        client, log_file = integration_client
        
        statuses = ['completed', 'skipped']
        
        for i, status in enumerate(statuses):
            session = {
                "session_type": "pomodoro",
                "start_time": f"2025-11-28T15:{i:02d}:00.000Z",
                "end_time": f"2025-11-28T15:{i+1:02d}:00.000Z",
                "status": status,
                "duration_minutes": 25
            }
            
            response = client.post('/log-session',
                                 data=json.dumps(session),
                                 content_type='application/json')
            assert response.status_code == 200
        
        # Verify all sessions were logged
        response = client.get('/session-history')
        assert response.status_code == 200
        history = response.get_json()
        assert len(history) == 2
        
        # Verify statuses
        logged_statuses = [session['status'] for session in history]
        assert logged_statuses == statuses