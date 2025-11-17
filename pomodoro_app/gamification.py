"""
Gamification module for Pomodoro Timer
Handles XP, levels, achievements, stats, and streaks
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import os

class GamificationSystem:
    """Manages gamification features for the Pomodoro Timer"""
    
    # XP rewards
    XP_WORK_COMPLETED = 25
    XP_BREAK_COMPLETED = 5
    XP_STREAK_BONUS = 10
    
    # Level thresholds
    LEVEL_THRESHOLDS = [0, 100, 250, 500, 800, 1200, 1700, 2300, 3000, 3800, 4700]
    
    # Achievement definitions
    ACHIEVEMENTS = {
        'first_pomodoro': {
            'name': 'First Step',
            'description': 'Complete your first Pomodoro',
            'icon': '🍅',
            'condition': lambda stats: stats['total_completed'] >= 1
        },
        'streak_3': {
            'name': 'Consistency',
            'description': 'Complete Pomodoros for 3 consecutive days',
            'icon': '🔥',
            'condition': lambda stats: stats['current_streak'] >= 3
        },
        'streak_7': {
            'name': 'Week Warrior',
            'description': 'Complete Pomodoros for 7 consecutive days',
            'icon': '⚡',
            'condition': lambda stats: stats['current_streak'] >= 7
        },
        'week_10': {
            'name': 'Productive Week',
            'description': 'Complete 10 Pomodoros in a week',
            'icon': '📈',
            'condition': lambda stats: stats['this_week_count'] >= 10
        },
        'week_20': {
            'name': 'Focus Master',
            'description': 'Complete 20 Pomodoros in a week',
            'icon': '🎯',
            'condition': lambda stats: stats['this_week_count'] >= 20
        },
        'total_50': {
            'name': 'Half Century',
            'description': 'Complete 50 total Pomodoros',
            'icon': '⭐',
            'condition': lambda stats: stats['total_completed'] >= 50
        },
        'total_100': {
            'name': 'Centurion',
            'description': 'Complete 100 total Pomodoros',
            'icon': '👑',
            'condition': lambda stats: stats['total_completed'] >= 100
        },
        'perfect_day': {
            'name': 'Perfect Day',
            'description': 'Complete 8 Pomodoros in a single day',
            'icon': '💎',
            'condition': lambda stats: stats['best_day_count'] >= 8
        }
    }
    
    def __init__(self, log_file: str, data_file: str = 'gamification_data.json'):
        """Initialize the gamification system
        
        Args:
            log_file: Path to the pomodoro log file
            data_file: Path to store gamification data
        """
        self.log_file = log_file
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load gamification data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default data structure
        return {
            'xp': 0,
            'level': 1,
            'achievements': [],
            'last_completion_date': None,
            'current_streak': 0,
            'longest_streak': 0
        }
    
    def _save_data(self):
        """Save gamification data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving gamification data: {e}")
    
    def _parse_log_file(self) -> List[Dict[str, Any]]:
        """Parse the log file and return list of sessions"""
        sessions = []
        if not os.path.exists(self.log_file):
            return sessions
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(' | ')
                    if len(parts) == 4:
                        try:
                            timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                            sessions.append({
                                'timestamp': timestamp,
                                'session_type': parts[1],
                                'action': parts[2],
                                'session_number': parts[3]
                            })
                        except ValueError:
                            continue
        except IOError:
            pass
        
        return sessions
    
    def calculate_xp_and_level(self) -> Dict[str, Any]:
        """Calculate total XP and current level from sessions"""
        sessions = self._parse_log_file()
        total_xp = 0
        
        for session in sessions:
            if session['action'] == 'completed':
                if session['session_type'] == 'work':
                    total_xp += self.XP_WORK_COMPLETED
                else:  # short_break or long_break
                    total_xp += self.XP_BREAK_COMPLETED
        
        # Calculate level
        level = 1
        for i, threshold in enumerate(self.LEVEL_THRESHOLDS):
            if total_xp >= threshold:
                level = i + 1
        
        # Calculate XP for current level
        current_level_threshold = self.LEVEL_THRESHOLDS[level - 1] if level <= len(self.LEVEL_THRESHOLDS) else 0
        next_level_threshold = self.LEVEL_THRESHOLDS[level] if level < len(self.LEVEL_THRESHOLDS) else current_level_threshold + 1000
        xp_in_level = total_xp - current_level_threshold
        xp_for_next_level = next_level_threshold - current_level_threshold
        
        return {
            'total_xp': total_xp,
            'level': level,
            'xp_in_level': xp_in_level,
            'xp_for_next_level': xp_for_next_level,
            'progress_percentage': (xp_in_level / xp_for_next_level * 100) if xp_for_next_level > 0 else 100
        }
    
    def calculate_streaks(self) -> Dict[str, int]:
        """Calculate current and longest streaks"""
        sessions = self._parse_log_file()
        
        if not sessions:
            return {'current_streak': 0, 'longest_streak': 0}
        
        # Get unique dates with completed work sessions
        completed_dates = set()
        for session in sessions:
            if session['action'] == 'completed' and session['session_type'] == 'work':
                completed_dates.add(session['timestamp'].date())
        
        if not completed_dates:
            return {'current_streak': 0, 'longest_streak': 0}
        
        # Sort dates
        sorted_dates = sorted(completed_dates)
        
        # Calculate current streak (counting backwards from today)
        today = datetime.now().date()
        current_streak = 0
        
        # Check if user has activity today or yesterday (to maintain streak)
        if today in completed_dates or (today - timedelta(days=1)) in completed_dates:
            check_date = today if today in completed_dates else today - timedelta(days=1)
            
            while check_date in completed_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
        
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
        longest_streak = max(longest_streak, temp_streak)
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak
        }
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate comprehensive statistics"""
        sessions = self._parse_log_file()
        
        now = datetime.now()
        today = now.date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # Initialize counters
        stats = {
            'total_completed': 0,
            'total_skipped': 0,
            'today_count': 0,
            'this_week_count': 0,
            'this_month_count': 0,
            'total_focus_minutes': 0,
            'average_daily_sessions': 0,
            'completion_rate': 0,
            'best_day_count': 0,
            'daily_counts': {}  # For graphing
        }
        
        daily_counts = {}
        
        for session in sessions:
            session_date = session['timestamp'].date()
            
            # Count by action
            if session['action'] == 'completed':
                stats['total_completed'] += 1
                
                # Count work sessions for focus time
                if session['session_type'] == 'work':
                    stats['total_focus_minutes'] += 25
                
                # Daily counts
                date_str = session_date.isoformat()
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
                
                # Period counts
                if session_date == today:
                    stats['today_count'] += 1
                if session_date >= week_start:
                    stats['this_week_count'] += 1
                if session_date >= month_start:
                    stats['this_month_count'] += 1
            else:
                stats['total_skipped'] += 1
        
        # Calculate best day
        if daily_counts:
            stats['best_day_count'] = max(daily_counts.values())
        
        # Calculate completion rate
        total_sessions = stats['total_completed'] + stats['total_skipped']
        if total_sessions > 0:
            stats['completion_rate'] = round(stats['total_completed'] / total_sessions * 100, 1)
        
        # Calculate average daily sessions
        if sessions:
            first_session_date = min(s['timestamp'].date() for s in sessions)
            days_active = (today - first_session_date).days + 1
            if days_active > 0:
                stats['average_daily_sessions'] = round(stats['total_completed'] / days_active, 1)
        
        # Store daily counts for last 30 days
        stats['daily_counts'] = {}
        for i in range(30):
            date = today - timedelta(days=29-i)
            date_str = date.isoformat()
            stats['daily_counts'][date_str] = daily_counts.get(date_str, 0)
        
        return stats
    
    def check_achievements(self) -> List[Dict[str, Any]]:
        """Check which achievements are unlocked"""
        stats = self.calculate_statistics()
        streaks = self.calculate_streaks()
        
        # Merge stats with streaks
        combined_stats = {**stats, **streaks}
        
        unlocked = []
        for achievement_id, achievement_def in self.ACHIEVEMENTS.items():
            if achievement_def['condition'](combined_stats):
                if achievement_id not in self.data['achievements']:
                    self.data['achievements'].append(achievement_id)
                    self._save_data()
                
                unlocked.append({
                    'id': achievement_id,
                    'name': achievement_def['name'],
                    'description': achievement_def['description'],
                    'icon': achievement_def['icon'],
                    'unlocked': True
                })
        
        return unlocked
    
    def get_all_achievements(self) -> List[Dict[str, Any]]:
        """Get all achievements with unlock status"""
        stats = self.calculate_statistics()
        streaks = self.calculate_streaks()
        combined_stats = {**stats, **streaks}
        
        achievements = []
        for achievement_id, achievement_def in self.ACHIEVEMENTS.items():
            achievements.append({
                'id': achievement_id,
                'name': achievement_def['name'],
                'description': achievement_def['description'],
                'icon': achievement_def['icon'],
                'unlocked': achievement_id in self.data['achievements']
            })
        
        return achievements
    
    def get_gamification_data(self) -> Dict[str, Any]:
        """Get comprehensive gamification data for frontend"""
        xp_data = self.calculate_xp_and_level()
        streaks = self.calculate_streaks()
        stats = self.calculate_statistics()
        achievements = self.get_all_achievements()
        
        return {
            'xp': xp_data,
            'streaks': streaks,
            'stats': stats,
            'achievements': achievements
        }
    
    def award_xp(self, session_type: str, action: str) -> Dict[str, Any]:
        """Award XP for a completed session and check for level ups
        
        Note: This should be called after the session has been logged to the file
        """
        if action != 'completed':
            return {'xp_gained': 0, 'leveled_up': False}
        
        # Calculate XP gain
        xp_gained = 0
        if session_type == 'work':
            xp_gained = self.XP_WORK_COMPLETED
        elif session_type in ['short_break', 'long_break']:
            xp_gained = self.XP_BREAK_COMPLETED
        
        # Get current data (includes the new session already logged)
        current_data = self.calculate_xp_and_level()
        current_level = current_data['level']
        current_xp = current_data['total_xp']
        
        # Calculate what the level was before this session
        previous_xp = current_xp - xp_gained
        previous_level = 1
        for i, threshold in enumerate(self.LEVEL_THRESHOLDS):
            if previous_xp >= threshold:
                previous_level = i + 1
        
        # Check for level up
        leveled_up = current_level > previous_level
        
        # Check for new achievements
        new_achievements = self.check_achievements()
        
        return {
            'xp_gained': xp_gained,
            'total_xp': current_xp,
            'level': current_level,
            'leveled_up': leveled_up,
            'new_achievements': new_achievements
        }
