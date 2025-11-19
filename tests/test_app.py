"""
Backend Tests for Pomodoro Timer Flask Application
Tests route handlers and helper functions
"""

import pytest
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pomodoro_app.app import validate_session_data, append_to_log, read_log_history


# ============================================================================
# Route Tests
# ============================================================================

class TestRoutes:
    """Test Flask route handlers."""
    
    def test_index_route_returns_200(self, client):
        """Test that GET / returns 200 and renders HTML."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        assert b'Pomodoro Timer' in response.data
    
    def test_health_check_returns_200(self, client):
        """Test that health check endpoint returns 200."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_log_endpoint_with_valid_data(self, client, sample_session_data, tmp_log_file, monkeypatch):
        """Test POST /log with valid data returns 200."""
        # Monkeypatch the LOG_FILE to use temp file
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        response = client.post('/log',
                              data=json.dumps(sample_session_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'message' in data
    
    def test_log_endpoint_with_invalid_data(self, client):
        """Test POST /log with invalid data returns 400."""
        invalid_data = {
            'session_type': 'invalid_type',
            'action': 'complete',
            'started_at': '2025-11-19T10:00:00Z',
            'ended_at': '2025-11-19T10:25:00Z'
        }
        
        response = client.post('/log',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_log_endpoint_with_missing_fields(self, client):
        """Test POST /log with missing fields returns 400."""
        incomplete_data = {
            'session_type': 'work',
            'action': 'complete'
            # Missing started_at and ended_at
        }
        
        response = client.post('/log',
                              data=json.dumps(incomplete_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_history_endpoint_returns_json(self, client, tmp_log_file, monkeypatch):
        """Test GET /history returns JSON array."""
        # Monkeypatch the LOG_FILE to use temp file
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        response = client.get('/history')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_history_endpoint_with_empty_log(self, client, tmp_log_file, monkeypatch):
        """Test GET /history returns empty array when log is empty."""
        # Monkeypatch the LOG_FILE to use temp file
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        response = client.get('/history')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []


# ============================================================================
# Validation Tests
# ============================================================================

class TestValidation:
    """Test validate_session_data function."""
    
    def test_validate_with_valid_data(self, sample_session_data):
        """Test validation accepts valid inputs."""
        is_valid, error = validate_session_data(sample_session_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_rejects_missing_data(self):
        """Test validation rejects None/empty data."""
        is_valid, error = validate_session_data(None)
        assert is_valid is False
        assert 'No data provided' in error
    
    def test_validate_rejects_missing_session_type(self):
        """Test validation rejects missing session_type."""
        data = {
            'action': 'complete',
            'started_at': '2025-11-19T10:00:00Z',
            'ended_at': '2025-11-19T10:25:00Z'
        }
        is_valid, error = validate_session_data(data)
        assert is_valid is False
        assert 'session_type' in error
    
    def test_validate_rejects_invalid_session_type(self):
        """Test validation rejects invalid session types."""
        data = {
            'session_type': 'invalid_session',
            'action': 'complete',
            'started_at': '2025-11-19T10:00:00Z',
            'ended_at': '2025-11-19T10:25:00Z'
        }
        is_valid, error = validate_session_data(data)
        assert is_valid is False
        assert 'Invalid session_type' in error
    
    def test_validate_rejects_invalid_action(self):
        """Test validation rejects invalid actions."""
        data = {
            'session_type': 'work',
            'action': 'invalid_action',
            'started_at': '2025-11-19T10:00:00Z',
            'ended_at': '2025-11-19T10:25:00Z'
        }
        is_valid, error = validate_session_data(data)
        assert is_valid is False
        assert 'Invalid action' in error
    
    def test_validate_rejects_empty_timestamps(self):
        """Test validation rejects empty timestamp fields."""
        data = {
            'session_type': 'work',
            'action': 'complete',
            'started_at': '',
            'ended_at': '2025-11-19T10:25:00Z'
        }
        is_valid, error = validate_session_data(data)
        assert is_valid is False
        assert 'Timestamps cannot be empty' in error
    
    @pytest.mark.parametrize('session_type', ['work', 'short_break', 'long_break'])
    def test_validate_accepts_all_valid_session_types(self, session_type):
        """Test validation accepts all valid session types."""
        data = {
            'session_type': session_type,
            'action': 'complete',
            'started_at': '2025-11-19T10:00:00Z',
            'ended_at': '2025-11-19T10:25:00Z'
        }
        is_valid, error = validate_session_data(data)
        assert is_valid is True
        assert error is None
    
    @pytest.mark.parametrize('action', ['complete', 'skip'])
    def test_validate_accepts_all_valid_actions(self, action):
        """Test validation accepts all valid actions."""
        data = {
            'session_type': 'work',
            'action': action,
            'started_at': '2025-11-19T10:00:00Z',
            'ended_at': '2025-11-19T10:25:00Z'
        }
        is_valid, error = validate_session_data(data)
        assert is_valid is True
        assert error is None


# ============================================================================
# Logging Tests
# ============================================================================

class TestLogging:
    """Test session logging functions."""
    
    def test_append_creates_file_if_not_exists(self, tmp_log_file, sample_session_data, monkeypatch):
        """Test append_to_log creates file if it doesn't exist."""
        # Monkeypatch the LOG_FILE
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        result = append_to_log(sample_session_data)
        
        assert result is True
        assert os.path.exists(tmp_log_file)
    
    def test_append_to_existing_file(self, tmp_log_file, sample_session_data, monkeypatch):
        """Test append_to_log appends to existing file."""
        # Monkeypatch the LOG_FILE
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        # Create file with initial data
        with open(tmp_log_file, 'w') as f:
            json.dump({'test': 'data'}, f)
            f.write('\n')
        
        result = append_to_log(sample_session_data)
        
        assert result is True
        
        # Verify both entries exist
        with open(tmp_log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2
    
    def test_read_log_parses_json_lines(self, tmp_log_file, monkeypatch):
        """Test read_log_history parses JSON Lines correctly."""
        # Monkeypatch the LOG_FILE
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        # Create test data
        test_data = [
            {'session_type': 'work', 'action': 'complete'},
            {'session_type': 'short_break', 'action': 'skip'}
        ]
        
        with open(tmp_log_file, 'w') as f:
            for entry in test_data:
                json.dump(entry, f)
                f.write('\n')
        
        result = read_log_history()
        
        assert len(result) == 2
        assert result[0]['session_type'] == 'work'
        assert result[1]['session_type'] == 'short_break'
    
    def test_read_log_handles_corrupted_entries(self, tmp_log_file, monkeypatch):
        """Test read_log_history handles corrupted log entries."""
        # Monkeypatch the LOG_FILE
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        # Create file with valid and corrupted data
        with open(tmp_log_file, 'w') as f:
            json.dump({'session_type': 'work', 'action': 'complete'}, f)
            f.write('\n')
            f.write('corrupted json line\n')
            json.dump({'session_type': 'short_break', 'action': 'skip'}, f)
            f.write('\n')
        
        result = read_log_history()
        
        # Should return only valid entries, skipping corrupted one
        assert len(result) == 2
        assert result[0]['session_type'] == 'work'
        assert result[1]['session_type'] == 'short_break'
    
    def test_read_log_returns_empty_when_file_missing(self, tmp_log_file, monkeypatch):
        """Test read_log_history returns empty list when file doesn't exist."""
        # Monkeypatch the LOG_FILE to non-existent file
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file + '_nonexistent')
        
        result = read_log_history()
        
        assert result == []
    
    def test_read_log_skips_empty_lines(self, tmp_log_file, monkeypatch):
        """Test read_log_history skips empty lines."""
        # Monkeypatch the LOG_FILE
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        # Create file with empty lines
        with open(tmp_log_file, 'w') as f:
            json.dump({'session_type': 'work', 'action': 'complete'}, f)
            f.write('\n')
            f.write('\n')
            f.write('   \n')
            json.dump({'session_type': 'short_break', 'action': 'skip'}, f)
            f.write('\n')
        
        result = read_log_history()
        
        assert len(result) == 2


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Test complete workflows."""
    
    def test_complete_logging_workflow(self, client, tmp_log_file, monkeypatch):
        """Test complete workflow: log session then retrieve history."""
        # Monkeypatch the LOG_FILE
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        # Log a session
        session_data = {
            'session_type': 'work',
            'action': 'complete',
            'started_at': '2025-11-19T10:00:00Z',
            'ended_at': '2025-11-19T10:25:00Z'
        }
        
        response = client.post('/log',
                              data=json.dumps(session_data),
                              content_type='application/json')
        assert response.status_code == 200
        
        # Retrieve history
        response = client.get('/history')
        assert response.status_code == 200
        
        history = json.loads(response.data)
        assert len(history) == 1
        assert history[0]['session_type'] == 'work'
        assert history[0]['action'] == 'complete'
    
    def test_multiple_sessions_logged(self, client, tmp_log_file, monkeypatch):
        """Test logging multiple sessions."""
        # Monkeypatch the LOG_FILE
        import pomodoro_app.app as app_module
        monkeypatch.setattr(app_module, 'LOG_FILE', tmp_log_file)
        
        sessions = [
            {'session_type': 'work', 'action': 'complete', 
             'started_at': '2025-11-19T10:00:00Z', 'ended_at': '2025-11-19T10:25:00Z'},
            {'session_type': 'short_break', 'action': 'skip',
             'started_at': '2025-11-19T10:25:00Z', 'ended_at': '2025-11-19T10:27:00Z'},
            {'session_type': 'work', 'action': 'complete',
             'started_at': '2025-11-19T10:30:00Z', 'ended_at': '2025-11-19T10:55:00Z'}
        ]
        
        for session in sessions:
            response = client.post('/log',
                                  data=json.dumps(session),
                                  content_type='application/json')
            assert response.status_code == 200
        
        # Verify all sessions in history
        response = client.get('/history')
        history = json.loads(response.data)
        
        assert len(history) == 3
        assert history[0]['session_type'] == 'work'
        assert history[1]['session_type'] == 'short_break'
        assert history[2]['session_type'] == 'work'
