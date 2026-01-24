# database.py - Database management for quiz system

import aiosqlite
import logging
from datetime import datetime
from typing import Optional, List, Dict
import os

logger = logging.getLogger('TranslatorBot.Database')

class QuizDatabase:
    def __init__(self, db_path: str = "quiz_data.db"):
        self.db_path = db_path
        
    async def initialize(self):
        """Initialize database and create tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table - stores XP, level, streak
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    current_streak INTEGER DEFAULT 0,
                    best_streak INTEGER DEFAULT 0,
                    total_questions INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    wrong_answers INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_quiz TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Quiz history table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS quiz_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    language TEXT,
                    difficulty TEXT,
                    question TEXT,
                    correct_answer TEXT,
                    user_answer TEXT,
                    is_correct BOOLEAN,
                    xp_gained INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Achievements table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    achievement_name TEXT,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def get_user(self, user_id: int, username: str = None) -> Dict:
        """Get user data, create if doesn't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute(
                'SELECT * FROM users WHERE user_id = ?', (user_id,)
            ) as cursor:
                user = await cursor.fetchone()
            
            if user is None:
                # Create new user
                await db.execute('''
                    INSERT INTO users (user_id, username, xp, level, current_streak, best_streak)
                    VALUES (?, ?, 0, 1, 0, 0)
                ''', (user_id, username or "Unknown"))
                await db.commit()
                
                # Fetch the newly created user
                async with db.execute(
                    'SELECT * FROM users WHERE user_id = ?', (user_id,)
                ) as cursor:
                    user = await cursor.fetchone()
            
            return dict(user) if user else None
    
    async def update_user_stats(self, user_id: int, xp_gained: int, is_correct: bool):
        """Update user statistics after quiz"""
        async with aiosqlite.connect(self.db_path) as db:
            user = await self.get_user(user_id)
            
            new_xp = user['xp'] + xp_gained
            new_streak = user['current_streak'] + 1 if is_correct else 0
            new_best_streak = max(user['best_streak'], new_streak)
            
            # Calculate new level
            from cogs.quiz.quiz_data import calculate_level
            new_level = calculate_level(new_xp)
            
            await db.execute('''
                UPDATE users 
                SET xp = ?,
                    level = ?,
                    current_streak = ?,
                    best_streak = ?,
                    total_questions = total_questions + 1,
                    correct_answers = correct_answers + ?,
                    wrong_answers = wrong_answers + ?,
                    last_quiz = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_xp, new_level, new_streak, new_best_streak, 
                  1 if is_correct else 0, 0 if is_correct else 1, user_id))
            
            await db.commit()
            
            # Check for level up
            level_up = new_level > user['level']
            
            return {
                'new_xp': new_xp,
                'new_level': new_level,
                'new_streak': new_streak,
                'level_up': level_up,
                'old_level': user['level']
            }
    
    async def add_quiz_history(self, user_id: int, language: str, difficulty: str, 
                               question: str, correct_answer: str, user_answer: str, 
                               is_correct: bool, xp_gained: int):
        """Record quiz attempt"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO quiz_history 
                (user_id, language, difficulty, question, correct_answer, user_answer, is_correct, xp_gained)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, language, difficulty, question, correct_answer, user_answer, is_correct, xp_gained))
            await db.commit()
    
    async def get_leaderboard(self, limit: int = 10, by: str = "xp") -> List[Dict]:
        """Get top players by XP or streak"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            order_column = "xp" if by == "xp" else "best_streak"
            
            async with db.execute(f'''
                SELECT user_id, username, xp, level, best_streak, 
                       correct_answers, total_questions
                FROM users
                ORDER BY {order_column} DESC
                LIMIT ?
            ''', (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_user_rank(self, user_id: int) -> int:
        """Get user's rank on leaderboard"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT COUNT(*) + 1 as rank
                FROM users
                WHERE xp > (SELECT xp FROM users WHERE user_id = ?)
            ''', (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get detailed user statistics"""
        user = await self.get_user(user_id)
        rank = await self.get_user_rank(user_id)
        
        accuracy = 0
        if user['total_questions'] > 0:
            accuracy = (user['correct_answers'] / user['total_questions']) * 100
        
        return {
            **user,
            'rank': rank,
            'accuracy': round(accuracy, 1)
        }
    
    async def unlock_achievement(self, user_id: int, achievement_name: str) -> bool:
        """Unlock achievement for user, returns True if newly unlocked"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if already unlocked
            async with db.execute('''
                SELECT id FROM achievements 
                WHERE user_id = ? AND achievement_name = ?
            ''', (user_id, achievement_name)) as cursor:
                existing = await cursor.fetchone()
            
            if existing:
                return False  # Already unlocked
            
            # Unlock achievement
            await db.execute('''
                INSERT INTO achievements (user_id, achievement_name)
                VALUES (?, ?)
            ''', (user_id, achievement_name))
            await db.commit()
            return True
    
    async def get_user_achievements(self, user_id: int) -> List[str]:
        """Get list of user's achievements"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT achievement_name FROM achievements
                WHERE user_id = ?
                ORDER BY unlocked_at DESC
            ''', (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    async def check_achievements(self, user_id: int, stats: Dict) -> List[str]:
        """Check and unlock achievements based on stats"""
        new_achievements = []
        
        achievements_to_check = [
            ("first_quiz", stats['total_questions'] >= 1, "🎯 First Steps"),
            ("10_quizzes", stats['total_questions'] >= 10, "📚 Dedicated Learner"),
            ("50_quizzes", stats['total_questions'] >= 50, "🎓 Quiz Master"),
            ("100_quizzes", stats['total_questions'] >= 100, "🏆 Century Club"),
            ("streak_5", stats['best_streak'] >= 5, "🔥 Hot Streak"),
            ("streak_10", stats['best_streak'] >= 10, "⚡ Lightning Round"),
            ("streak_20", stats['best_streak'] >= 20, "💫 Unstoppable"),
            ("level_5", stats['level'] >= 5, "⭐ Rising Star"),
            ("level_10", stats['level'] >= 10, "🌟 Expert"),
            ("level_20", stats['level'] >= 20, "👑 Legend"),
            ("perfect_10", stats['correct_answers'] >= 10 and stats['accuracy'] == 100, "💯 Perfectionist"),
        ]
        
        for achievement_id, condition, achievement_name in achievements_to_check:
            if condition:
                unlocked = await self.unlock_achievement(user_id, achievement_name)
                if unlocked:
                    new_achievements.append(achievement_name)
        
        return new_achievements