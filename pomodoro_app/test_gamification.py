"""
Unit tests for Gamification System
Tests XP, levels, achievements, stats, and streaks
"""
import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from gamification import GamificationSystem


@pytest.fixture
def temp_files():
    """Create temporary log and data files for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_log.txt') as log_file:
        log_path = log_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_data.json') as data_file:
        data_path = data_file.name
    
    yield log_path, data_path
    
    # Cleanup
    for path in [log_path, data_path]:
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture
def gamification_system(temp_files):
    """Create a gamification system with temp files"""
    log_file, data_file = temp_files
    return GamificationSystem(log_file, data_file)


class TestGamificationInitialization:
    """Tests for gamification system initialization"""
    
    def test_init_creates_default_data(self, gamification_system):
        """Test that initialization creates default data structure"""
        assert gamification_system.data['xp'] == 0
        assert gamification_system.data['level'] == 1
        assert gamification_system.data['achievements'] == []
        assert gamification_system.data['current_streak'] == 0
    
    def test_init_loads_existing_data(self, temp_files):
        """Test that initialization loads existing data"""
        log_file, data_file = temp_files
        
        # Create existing data
        existing_data = {
            'xp': 150,
            'level': 3,
            'achievements': ['first_pomodoro'],
            'current_streak': 5,
            'longest_streak': 5,
            'last_completion_date': '2024-01-01'
        }
        
        with open(data_file, 'w') as f:
            json.dump(existing_data, f)
        
        # Initialize system
        system = GamificationSystem(log_file, data_file)
        
        assert system.data['xp'] == 150
        assert system.data['level'] == 3
        assert 'first_pomodoro' in system.data['achievements']


class TestXPAndLevels:
    """Tests for XP calculation and level progression"""
    
    def test_no_sessions_gives_zero_xp(self, gamification_system):
        """Test that no sessions result in 0 XP"""
        xp_data = gamification_system.calculate_xp_and_level()
        assert xp_data['total_xp'] == 0
        assert xp_data['level'] == 1
    
    def test_completed_work_session_gives_xp(self, temp_files):
        """Test that completed work session awards XP"""
        log_file, data_file = temp_files
        
        # Write a completed work session
        with open(log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 | work | completed | session_1\n")
        
        system = GamificationSystem(log_file, data_file)
        xp_data = system.calculate_xp_and_level()
        
        assert xp_data['total_xp'] == 25  # XP_WORK_COMPLETED
        assert xp_data['level'] == 1
    
    def test_completed_break_gives_less_xp(self, temp_files):
        """Test that breaks give less XP than work sessions"""
        log_file, data_file = temp_files
        
        with open(log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 | short_break | completed | session_1\n")
        
        system = GamificationSystem(log_file, data_file)
        xp_data = system.calculate_xp_and_level()
        
        assert xp_data['total_xp'] == 5  # XP_BREAK_COMPLETED
    
    def test_skipped_session_gives_no_xp(self, temp_files):
        """Test that skipped sessions don't award XP"""
        log_file, data_file = temp_files
        
        with open(log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 | work | skipped | session_1\n")
        
        system = GamificationSystem(log_file, data_file)
        xp_data = system.calculate_xp_and_level()
        
        assert xp_data['total_xp'] == 0
    
    def test_level_progression(self, temp_files):
        """Test that XP correctly calculates level"""
        log_file, data_file = temp_files
        
        # Write enough sessions to reach level 2 (100 XP needed)
        with open(log_file, 'w') as f:
            for i in range(4):  # 4 * 25 = 100 XP
                f.write(f"2024-01-01 10:{i:02d}:00 | work | completed | session_{i+1}\n")
        
        system = GamificationSystem(log_file, data_file)
        xp_data = system.calculate_xp_and_level()
        
        assert xp_data['total_xp'] == 100
        assert xp_data['level'] == 2
    
    def test_xp_progress_calculation(self, temp_files):
        """Test XP progress within current level"""
        log_file, data_file = temp_files
        
        # Write 2 sessions (50 XP, level 1)
        with open(log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 | work | completed | session_1\n")
            f.write("2024-01-01 10:30:00 | work | completed | session_2\n")
        
        system = GamificationSystem(log_file, data_file)
        xp_data = system.calculate_xp_and_level()
        
        assert xp_data['level'] == 1
        assert xp_data['xp_in_level'] == 50
        assert xp_data['xp_for_next_level'] == 100  # Level 2 threshold
        assert xp_data['progress_percentage'] == 50.0


class TestStreaks:
    """Tests for streak calculation"""
    
    def test_no_sessions_gives_zero_streak(self, gamification_system):
        """Test that no sessions result in 0 streak"""
        streaks = gamification_system.calculate_streaks()
        assert streaks['current_streak'] == 0
        assert streaks['longest_streak'] == 0
    
    def test_single_day_gives_one_streak(self, temp_files):
        """Test that one day of activity gives streak of 1"""
        log_file, data_file = temp_files
        
        today = datetime.now()
        with open(log_file, 'w') as f:
            f.write(f"{today.strftime('%Y-%m-%d')} 10:00:00 | work | completed | session_1\n")
        
        system = GamificationSystem(log_file, data_file)
        streaks = system.calculate_streaks()
        
        assert streaks['current_streak'] >= 1
    
    def test_consecutive_days_increase_streak(self, temp_files):
        """Test that consecutive days increase streak"""
        log_file, data_file = temp_files
        
        today = datetime.now()
        with open(log_file, 'w') as f:
            for i in range(3):
                date = (today - timedelta(days=2-i)).strftime('%Y-%m-%d')
                f.write(f"{date} 10:00:00 | work | completed | session_1\n")
        
        system = GamificationSystem(log_file, data_file)
        streaks = system.calculate_streaks()
        
        assert streaks['current_streak'] == 3
    
    def test_gap_breaks_current_streak(self, temp_files):
        """Test that a gap breaks the current streak"""
        log_file, data_file = temp_files
        
        today = datetime.now()
        with open(log_file, 'w') as f:
            # Day 5 days ago
            date1 = (today - timedelta(days=5)).strftime('%Y-%m-%d')
            f.write(f"{date1} 10:00:00 | work | completed | session_1\n")
            # Gap of 3 days
            # Today
            date2 = today.strftime('%Y-%m-%d')
            f.write(f"{date2} 10:00:00 | work | completed | session_2\n")
        
        system = GamificationSystem(log_file, data_file)
        streaks = system.calculate_streaks()
        
        # Current streak should be 1 (just today)
        assert streaks['current_streak'] == 1
    
    def test_longest_streak_calculation(self, temp_files):
        """Test longest streak is calculated correctly"""
        log_file, data_file = temp_files
        
        today = datetime.now()
        with open(log_file, 'w') as f:
            # First streak: 4 days (10-13 days ago)
            for i in range(4):
                date = (today - timedelta(days=13-i)).strftime('%Y-%m-%d')
                f.write(f"{date} 10:00:00 | work | completed | session_{i+1}\n")
            
            # Gap
            
            # Second streak: 2 days (1-2 days ago)
            for i in range(2):
                date = (today - timedelta(days=2-i)).strftime('%Y-%m-%d')
                f.write(f"{date} 10:00:00 | work | completed | session_{i+5}\n")
        
        system = GamificationSystem(log_file, data_file)
        streaks = system.calculate_streaks()
        
        assert streaks['longest_streak'] == 4


class TestStatistics:
    """Tests for statistics calculation"""
    
    def test_empty_log_gives_zero_stats(self, gamification_system):
        """Test that empty log gives all zeros"""
        stats = gamification_system.calculate_statistics()
        assert stats['total_completed'] == 0
        assert stats['total_skipped'] == 0
        assert stats['total_focus_minutes'] == 0
    
    def test_completed_session_counts(self, temp_files):
        """Test that completed sessions are counted"""
        log_file, data_file = temp_files
        
        with open(log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 | work | completed | session_1\n")
            f.write("2024-01-01 10:30:00 | work | completed | session_2\n")
            f.write("2024-01-01 11:00:00 | work | skipped | session_3\n")
        
        system = GamificationSystem(log_file, data_file)
        stats = system.calculate_statistics()
        
        assert stats['total_completed'] == 2
        assert stats['total_skipped'] == 1
    
    def test_focus_time_calculation(self, temp_files):
        """Test that focus time is calculated correctly"""
        log_file, data_file = temp_files
        
        with open(log_file, 'w') as f:
            # 3 work sessions = 75 minutes
            f.write("2024-01-01 10:00:00 | work | completed | session_1\n")
            f.write("2024-01-01 10:30:00 | work | completed | session_2\n")
            f.write("2024-01-01 11:00:00 | work | completed | session_3\n")
            # Breaks don't count towards focus time
            f.write("2024-01-01 11:30:00 | short_break | completed | session_4\n")
        
        system = GamificationSystem(log_file, data_file)
        stats = system.calculate_statistics()
        
        assert stats['total_focus_minutes'] == 75
    
    def test_completion_rate_calculation(self, temp_files):
        """Test completion rate percentage"""
        log_file, data_file = temp_files
        
        with open(log_file, 'w') as f:
            # 3 completed, 1 skipped = 75% completion rate
            f.write("2024-01-01 10:00:00 | work | completed | session_1\n")
            f.write("2024-01-01 10:30:00 | work | completed | session_2\n")
            f.write("2024-01-01 11:00:00 | work | completed | session_3\n")
            f.write("2024-01-01 11:30:00 | work | skipped | session_4\n")
        
        system = GamificationSystem(log_file, data_file)
        stats = system.calculate_statistics()
        
        assert stats['completion_rate'] == 75.0
    
    def test_daily_counts(self, temp_files):
        """Test daily session counts"""
        log_file, data_file = temp_files
        
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        
        with open(log_file, 'w') as f:
            # 3 sessions today
            f.write(f"{today_str} 10:00:00 | work | completed | session_1\n")
            f.write(f"{today_str} 10:30:00 | work | completed | session_2\n")
            f.write(f"{today_str} 11:00:00 | work | completed | session_3\n")
        
        system = GamificationSystem(log_file, data_file)
        stats = system.calculate_statistics()
        
        assert stats['today_count'] == 3


class TestAchievements:
    """Tests for achievement system"""
    
    def test_first_pomodoro_achievement(self, temp_files):
        """Test that first pomodoro unlocks achievement"""
        log_file, data_file = temp_files
        
        with open(log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 | work | completed | session_1\n")
        
        system = GamificationSystem(log_file, data_file)
        achievements = system.check_achievements()
        
        # Should unlock 'first_pomodoro'
        achievement_ids = [a['id'] for a in achievements]
        assert 'first_pomodoro' in achievement_ids
    
    def test_streak_achievements(self, temp_files):
        """Test that streak achievements unlock"""
        log_file, data_file = temp_files
        
        today = datetime.now()
        with open(log_file, 'w') as f:
            # 3 consecutive days
            for i in range(3):
                date = (today - timedelta(days=2-i)).strftime('%Y-%m-%d')
                f.write(f"{date} 10:00:00 | work | completed | session_{i+1}\n")
        
        system = GamificationSystem(log_file, data_file)
        achievements = system.check_achievements()
        
        achievement_ids = [a['id'] for a in achievements]
        assert 'streak_3' in achievement_ids
    
    def test_weekly_achievement(self, temp_files):
        """Test that weekly achievements unlock"""
        log_file, data_file = temp_files
        
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        with open(log_file, 'w') as f:
            # 10 sessions this week
            for i in range(10):
                date = (week_start + timedelta(days=i % 5)).strftime('%Y-%m-%d')
                f.write(f"{date} {10+i}:00:00 | work | completed | session_{i+1}\n")
        
        system = GamificationSystem(log_file, data_file)
        achievements = system.check_achievements()
        
        achievement_ids = [a['id'] for a in achievements]
        assert 'week_10' in achievement_ids
    
    def test_get_all_achievements_includes_locked(self, gamification_system):
        """Test that all achievements are returned, including locked ones"""
        achievements = gamification_system.get_all_achievements()
        
        # Should have all defined achievements
        assert len(achievements) == len(GamificationSystem.ACHIEVEMENTS)
        
        # All should be locked initially
        locked = [a for a in achievements if not a['unlocked']]
        assert len(locked) == len(achievements)


class TestAwardXP:
    """Tests for XP awarding"""
    
    def test_award_xp_for_completed_work(self, temp_files):
        """Test that completing work awards XP"""
        log_file, data_file = temp_files
        
        system = GamificationSystem(log_file, data_file)
        
        # Manually add a log entry before calling award_xp
        with open(log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 | work | completed | session_1\n")
        
        result = system.award_xp('work', 'completed')
        
        assert result['xp_gained'] == 25
        assert result['total_xp'] == 25
        assert result['level'] == 1
    
    def test_no_xp_for_skipped(self, temp_files):
        """Test that skipped sessions don't award XP"""
        log_file, data_file = temp_files
        
        system = GamificationSystem(log_file, data_file)
        result = system.award_xp('work', 'skipped')
        
        assert result['xp_gained'] == 0
    
    def test_level_up_detection(self, temp_files):
        """Test that level ups are detected"""
        log_file, data_file = temp_files
        
        # Write sessions to reach just below level 2 (need 100 XP, write 75 XP worth)
        with open(log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 | work | completed | session_1\n")
            f.write("2024-01-01 10:30:00 | work | completed | session_2\n")
            f.write("2024-01-01 11:00:00 | work | completed | session_3\n")
        
        system = GamificationSystem(log_file, data_file)
        
        # Verify we're at level 1 with 75 XP
        before_data = system.calculate_xp_and_level()
        assert before_data['level'] == 1
        assert before_data['total_xp'] == 75
        
        # Add one more to trigger level up (75 + 25 = 100 = level 2)
        with open(log_file, 'a') as f:
            f.write("2024-01-01 12:00:00 | work | completed | session_4\n")
        
        result = system.award_xp('work', 'completed')
        
        assert result['leveled_up'] == True
        assert result['level'] == 2


class TestGamificationDataEndpoint:
    """Tests for comprehensive gamification data"""
    
    def test_get_gamification_data_structure(self, gamification_system):
        """Test that gamification data has correct structure"""
        data = gamification_system.get_gamification_data()
        
        assert 'xp' in data
        assert 'streaks' in data
        assert 'stats' in data
        assert 'achievements' in data
        
        # Check nested structures
        assert 'total_xp' in data['xp']
        assert 'level' in data['xp']
        assert 'current_streak' in data['streaks']
        assert 'total_completed' in data['stats']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
