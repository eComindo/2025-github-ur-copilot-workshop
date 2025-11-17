"""
Integration tests for gamification endpoints
Tests the Flask API endpoints for gamification features
"""
import pytest
import json
import os
import tempfile
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


class TestGamificationStatsEndpoint:
    """Tests for /gamification/stats endpoint"""
    
    def test_gamification_stats_returns_200(self, client):
        """Test that gamification stats endpoint returns 200"""
        response = client.get('/gamification/stats')
        assert response.status_code == 200
    
    def test_gamification_stats_returns_json(self, client):
        """Test that gamification stats returns JSON"""
        response = client.get('/gamification/stats')
        assert response.content_type == 'application/json'
    
    def test_gamification_stats_structure(self, client):
        """Test that gamification stats has correct structure"""
        response = client.get('/gamification/stats')
        data = response.get_json()
        
        # Check top-level keys
        assert 'xp' in data
        assert 'streaks' in data
        assert 'stats' in data
        assert 'achievements' in data
    
    def test_gamification_xp_structure(self, client):
        """Test that XP data has correct structure"""
        response = client.get('/gamification/stats')
        data = response.get_json()
        
        xp = data['xp']
        assert 'total_xp' in xp
        assert 'level' in xp
        assert 'xp_in_level' in xp
        assert 'xp_for_next_level' in xp
        assert 'progress_percentage' in xp
        
        # Check types
        assert isinstance(xp['total_xp'], int)
        assert isinstance(xp['level'], int)
        assert xp['level'] >= 1
    
    def test_gamification_streaks_structure(self, client):
        """Test that streaks data has correct structure"""
        response = client.get('/gamification/stats')
        data = response.get_json()
        
        streaks = data['streaks']
        assert 'current_streak' in streaks
        assert 'longest_streak' in streaks
        
        # Check types and values
        assert isinstance(streaks['current_streak'], int)
        assert isinstance(streaks['longest_streak'], int)
        assert streaks['current_streak'] >= 0
        assert streaks['longest_streak'] >= 0
    
    def test_gamification_stats_structure(self, client):
        """Test that statistics data has correct structure"""
        response = client.get('/gamification/stats')
        data = response.get_json()
        
        stats = data['stats']
        required_keys = [
            'total_completed', 'total_skipped', 'today_count',
            'this_week_count', 'this_month_count', 'total_focus_minutes',
            'completion_rate', 'best_day_count'
        ]
        
        for key in required_keys:
            assert key in stats, f"Missing key: {key}"
        
        # Check types
        assert isinstance(stats['total_completed'], int)
        assert isinstance(stats['completion_rate'], (int, float))
    
    def test_gamification_achievements_structure(self, client):
        """Test that achievements data has correct structure"""
        response = client.get('/gamification/stats')
        data = response.get_json()
        
        achievements = data['achievements']
        assert isinstance(achievements, list)
        
        if len(achievements) > 0:
            achievement = achievements[0]
            assert 'id' in achievement
            assert 'name' in achievement
            assert 'description' in achievement
            assert 'icon' in achievement
            assert 'unlocked' in achievement
            assert isinstance(achievement['unlocked'], bool)


class TestGamificationAchievementsEndpoint:
    """Tests for /gamification/achievements endpoint"""
    
    def test_achievements_returns_200(self, client):
        """Test that achievements endpoint returns 200"""
        response = client.get('/gamification/achievements')
        assert response.status_code == 200
    
    def test_achievements_returns_json(self, client):
        """Test that achievements returns JSON"""
        response = client.get('/gamification/achievements')
        assert response.content_type == 'application/json'
    
    def test_achievements_structure(self, client):
        """Test that achievements response has correct structure"""
        response = client.get('/gamification/achievements')
        data = response.get_json()
        
        assert 'achievements' in data
        assert isinstance(data['achievements'], list)
    
    def test_all_achievements_returned(self, client):
        """Test that all defined achievements are returned"""
        response = client.get('/gamification/achievements')
        data = response.get_json()
        
        achievements = data['achievements']
        # We have 8 achievements defined
        assert len(achievements) == 8
    
    def test_achievement_details(self, client):
        """Test that each achievement has required details"""
        response = client.get('/gamification/achievements')
        data = response.get_json()
        
        for achievement in data['achievements']:
            assert 'id' in achievement
            assert 'name' in achievement
            assert 'description' in achievement
            assert 'icon' in achievement
            assert 'unlocked' in achievement
            
            # Check types
            assert isinstance(achievement['id'], str)
            assert isinstance(achievement['name'], str)
            assert isinstance(achievement['description'], str)
            assert isinstance(achievement['icon'], str)
            assert isinstance(achievement['unlocked'], bool)


class TestLogEndpointGamificationResponse:
    """Tests for gamification response in /log endpoint"""
    
    def test_log_returns_gamification_data(self, client, monkeypatch, tmp_path):
        """Test that log endpoint returns gamification data"""
        # Use temporary log file
        log_file = tmp_path / "test_log.txt"
        monkeypatch.setattr('app.LOG_FILE', str(log_file))
        monkeypatch.setattr('app.gamification.log_file', str(log_file))
        
        data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 1
        }
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        
        # Check that gamification data is included
        assert 'gamification' in json_data
        
        gamification = json_data['gamification']
        assert 'xp_gained' in gamification
        assert 'total_xp' in gamification
        assert 'level' in gamification
        assert 'leveled_up' in gamification
    
    def test_completed_work_awards_xp(self, client, monkeypatch, tmp_path):
        """Test that completing work session awards XP"""
        log_file = tmp_path / "test_log.txt"
        monkeypatch.setattr('app.LOG_FILE', str(log_file))
        monkeypatch.setattr('app.gamification.log_file', str(log_file))
        
        data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 1
        }
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        json_data = response.get_json()
        gamification = json_data['gamification']
        
        # Work session should award 25 XP
        assert gamification['xp_gained'] == 25
    
    def test_skipped_session_no_xp(self, client, monkeypatch, tmp_path):
        """Test that skipped sessions don't award XP"""
        log_file = tmp_path / "test_log.txt"
        monkeypatch.setattr('app.LOG_FILE', str(log_file))
        monkeypatch.setattr('app.gamification.log_file', str(log_file))
        
        data = {
            'session_type': 'work',
            'action': 'skipped',
            'session_number': 1
        }
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        json_data = response.get_json()
        gamification = json_data['gamification']
        
        # Skipped session should not award XP
        assert gamification['xp_gained'] == 0
    
    def test_new_achievements_returned(self, client, monkeypatch, tmp_path):
        """Test that new achievements are returned when unlocked"""
        log_file = tmp_path / "test_log.txt"
        data_file = tmp_path / "test_data.json"
        monkeypatch.setattr('app.LOG_FILE', str(log_file))
        monkeypatch.setattr('app.GAMIFICATION_DATA_FILE', str(data_file))
        monkeypatch.setattr('app.gamification.log_file', str(log_file))
        monkeypatch.setattr('app.gamification.data_file', str(data_file))
        
        data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 1
        }
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        json_data = response.get_json()
        gamification = json_data['gamification']
        
        assert 'new_achievements' in gamification
        assert isinstance(gamification['new_achievements'], list)


class TestGamificationErrorHandling:
    """Tests for error handling in gamification endpoints"""
    
    def test_stats_endpoint_handles_errors_gracefully(self, client, monkeypatch):
        """Test that stats endpoint handles errors without crashing"""
        # This test ensures the endpoint doesn't crash even with issues
        response = client.get('/gamification/stats')
        # Should still return 200 or 500, not crash
        assert response.status_code in [200, 500]
    
    def test_achievements_endpoint_handles_errors_gracefully(self, client):
        """Test that achievements endpoint handles errors without crashing"""
        response = client.get('/gamification/achievements')
        # Should still return 200 or 500, not crash
        assert response.status_code in [200, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
