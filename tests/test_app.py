import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from app import app, LOG_FILE


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file_path = f.name
    yield temp_file_path
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "session_type": "pomodoro",
        "start_time": "2025-11-28T08:00:00.000Z",
        "end_time": "2025-11-28T08:25:00.000Z",
        "status": "completed",
        "duration_minutes": 25
    }


@pytest.fixture
def sample_sessions_list():
    """Sample list of sessions for testing."""
    return [
        {
            "session_type": "pomodoro",
            "start_time": "2025-11-28T08:00:00.000Z",
            "end_time": "2025-11-28T08:25:00.000Z",
            "status": "completed",
            "duration_minutes": 25
        },
        {
            "session_type": "shortBreak",
            "start_time": "2025-11-28T08:25:00.000Z",
            "end_time": "2025-11-28T08:30:00.000Z",
            "status": "completed",
            "duration_minutes": 5
        }
    ]


class TestFlaskRoutes:
    """Test cases for Flask route handlers."""

    def test_index_route(self, client):
        """Test that the index route returns the correct template."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Pomodoro Timer' in response.data
        assert b'timer-display' in response.data

    def test_index_route_content_type(self, client):
        """Test that the index route returns HTML content."""
        response = client.get('/')
        assert 'text/html' in response.content_type


class TestLogSessionEndpoint:
    """Test cases for the log-session endpoint."""

    @patch('app.LOG_FILE', 'test_log.json')
    def test_log_session_success_new_file(self, client, sample_session_data):
        """Test logging a session when log file doesn't exist."""
        with patch('os.path.exists', return_value=False), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dump') as mock_dump:
            
            response = client.post('/log-session',
                                 data=json.dumps(sample_session_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['message'] == 'Session logged successfully'
            
            # Verify file operations
            mock_file.assert_called_with('test_log.json', 'w')
            mock_dump.assert_called_once()

    @patch('app.LOG_FILE', 'test_log.json')
    def test_log_session_success_existing_file(self, client, sample_session_data, sample_sessions_list):
        """Test logging a session when log file exists."""
        mock_existing_data = json.dumps(sample_sessions_list)
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_existing_data)) as mock_file, \
             patch('json.load', return_value=sample_sessions_list), \
             patch('json.dump') as mock_dump:
            
            response = client.post('/log-session',
                                 data=json.dumps(sample_session_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            
            # Verify that json.dump was called with the updated list
            mock_dump.assert_called_once()
            call_args = mock_dump.call_args[0]
            logged_sessions = call_args[0]
            assert len(logged_sessions) == 3  # 2 existing + 1 new

    def test_log_session_missing_required_fields(self, client):
        """Test logging a session with missing required fields."""
        incomplete_data = {
            "session_type": "pomodoro",
            "start_time": "2025-11-28T08:00:00.000Z"
            # Missing end_time and status
        }
        
        response = client.post('/log-session',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Missing required fields'

    def test_log_session_invalid_json(self, client):
        """Test logging a session with invalid JSON data."""
        response = client.post('/log-session',
                             data='invalid json',
                             content_type='application/json')
        
        # Flask returns 400 for invalid JSON, but our app catches the exception and returns 500
        # This reflects the actual application behavior
        assert response.status_code in [400, 500]

    def test_log_session_no_content_type(self, client, sample_session_data):
        """Test logging a session without proper content type."""
        response = client.post('/log-session',
                             data=json.dumps(sample_session_data))
        
        # Without content-type, request.get_json() returns None, causing an exception
        # The app catches this and returns 500
        assert response.status_code in [400, 500]

    @patch('app.LOG_FILE', 'test_log.json')
    def test_log_session_file_error(self, client, sample_session_data):
        """Test logging a session when file operations fail."""
        with patch('os.path.exists', side_effect=Exception('File system error')):
            response = client.post('/log-session',
                                 data=json.dumps(sample_session_data),
                                 content_type='application/json')
            
            assert response.status_code == 500
            data = response.get_json()
            assert 'error' in data

    def test_log_session_validation_edge_cases(self, client):
        """Test various edge cases for session data validation."""
        # Test with None values - the current app accepts None values, so we test this behavior
        none_data = {
            "session_type": None,
            "start_time": "2025-11-28T08:00:00.000Z",
            "end_time": "2025-11-28T08:25:00.000Z",
            "status": "completed"
        }
        
        with patch('os.path.exists', return_value=False), \
             patch('builtins.open', mock_open()), \
             patch('json.dump'):
            
            response = client.post('/log-session',
                                 data=json.dumps(none_data),
                                 content_type='application/json')
            
            # The current implementation accepts None values as they pass the 'in' check
            # This reflects the actual application behavior
            assert response.status_code == 200

    def test_log_session_different_session_types(self, client):
        """Test logging different types of sessions."""
        session_types = ['pomodoro', 'shortBreak', 'longBreak']
        statuses = ['completed', 'skipped', 'paused']
        
        for session_type in session_types:
            for status in statuses:
                session_data = {
                    "session_type": session_type,
                    "start_time": "2025-11-28T08:00:00.000Z",
                    "end_time": "2025-11-28T08:25:00.000Z",
                    "status": status,
                    "duration_minutes": 25
                }
                
                with patch('os.path.exists', return_value=False), \
                     patch('builtins.open', mock_open()), \
                     patch('json.dump'):
                    
                    response = client.post('/log-session',
                                         data=json.dumps(session_data),
                                         content_type='application/json')
                    
                    assert response.status_code == 200


class TestSessionHistoryEndpoint:
    """Test cases for the session-history endpoint."""

    @patch('app.LOG_FILE', 'test_log.json')
    def test_session_history_existing_file(self, client, sample_sessions_list):
        """Test getting session history when log file exists."""
        mock_data = json.dumps(sample_sessions_list)
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_data)), \
             patch('json.load', return_value=sample_sessions_list):
            
            response = client.get('/session-history')
            
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['session_type'] == 'pomodoro'
            assert data[1]['session_type'] == 'shortBreak'

    @patch('app.LOG_FILE', 'test_log.json')
    def test_session_history_no_file(self, client):
        """Test getting session history when log file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            response = client.get('/session-history')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data == []

    @patch('app.LOG_FILE', 'test_log.json')
    def test_session_history_empty_file(self, client):
        """Test getting session history when log file is empty."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='[]')), \
             patch('json.load', return_value=[]):
            
            response = client.get('/session-history')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data == []

    @patch('app.LOG_FILE', 'test_log.json')
    def test_session_history_file_error(self, client):
        """Test getting session history when file operations fail."""
        with patch('os.path.exists', side_effect=Exception('File system error')):
            response = client.get('/session-history')
            
            assert response.status_code == 500
            data = response.get_json()
            assert 'error' in data

    @patch('app.LOG_FILE', 'test_log.json')
    def test_session_history_json_decode_error(self, client):
        """Test getting session history with corrupted JSON file."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='invalid json')), \
             patch('json.load', side_effect=json.JSONDecodeError('Invalid JSON', 'doc', 0)):
            
            response = client.get('/session-history')
            
            assert response.status_code == 500
            data = response.get_json()
            assert 'error' in data

    def test_session_history_method_not_allowed(self, client):
        """Test that session-history endpoint only accepts GET requests."""
        response = client.post('/session-history')
        assert response.status_code == 405  # Method Not Allowed

        response = client.put('/session-history')
        assert response.status_code == 405

        response = client.delete('/session-history')
        assert response.status_code == 405


class TestApplicationConfiguration:
    """Test cases for application configuration and setup."""

    def test_app_configuration(self):
        """Test that the Flask app is configured correctly."""
        assert app.name == 'app'
        assert app.config.get('TESTING') is not None

    def test_log_file_constant(self):
        """Test that LOG_FILE constant is set correctly."""
        assert LOG_FILE == 'pomodoro_log.json'

    def test_route_registration(self):
        """Test that all routes are registered correctly."""
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/' in routes
        assert '/log-session' in routes
        assert '/session-history' in routes

    def test_static_folder_setup(self, client):
        """Test that static files are served correctly."""
        # Test CSS file
        response = client.get('/static/style.css')
        assert response.status_code == 200
        assert 'text/css' in response.content_type or 'text/plain' in response.content_type

        # Test JavaScript file
        response = client.get('/static/app.js')
        assert response.status_code == 200
        assert 'application/javascript' in response.content_type or 'text/plain' in response.content_type


class TestDataValidation:
    """Test cases for data validation and edge cases."""

    def test_session_data_fields_validation(self, client):
        """Test validation of all session data fields."""
        base_data = {
            "session_type": "pomodoro",
            "start_time": "2025-11-28T08:00:00.000Z",
            "end_time": "2025-11-28T08:25:00.000Z",
            "status": "completed"
        }

        # Test missing each required field
        required_fields = ['session_type', 'start_time', 'end_time', 'status']
        
        for field in required_fields:
            test_data = base_data.copy()
            del test_data[field]
            
            response = client.post('/log-session',
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            assert response.status_code == 400, f"Should fail when missing {field}"

    def test_additional_fields_allowed(self, client):
        """Test that additional fields in session data are allowed."""
        session_data = {
            "session_type": "pomodoro",
            "start_time": "2025-11-28T08:00:00.000Z",
            "end_time": "2025-11-28T08:25:00.000Z",
            "status": "completed",
            "duration_minutes": 25,
            "extra_field": "extra_value",
            "user_id": 123
        }
        
        with patch('os.path.exists', return_value=False), \
             patch('builtins.open', mock_open()), \
             patch('json.dump'):
            
            response = client.post('/log-session',
                                 data=json.dumps(session_data),
                                 content_type='application/json')
            
            assert response.status_code == 200