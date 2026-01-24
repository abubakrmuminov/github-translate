
import aiosqlite
import logging
from typing import List, Optional, Any, Tuple
import os

logger = logging.getLogger('TranslatorBot')

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Connect to SQLite database"""
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        await self._init_tables()
        logger.info("✅ Database connected")

    async def close(self):
        if self.conn:
            await self.conn.close()
            logger.info("Database closed")

    async def execute(self, sql: str, parameters: Tuple = ()) -> None:
        if not self.conn: return
        await self.conn.execute(sql, parameters)
        await self.conn.commit()

    async def fetchval(self, sql: str, parameters: Tuple = ()) -> Any:
        if not self.conn: return None
        async with self.conn.execute(sql, parameters) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            return None

    async def fetchrow(self, sql: str, parameters: Tuple = ()) -> Optional[aiosqlite.Row]:
        if not self.conn: return None
        async with self.conn.execute(sql, parameters) as cursor:
            return await cursor.fetchone()

    async def fetchall(self, sql: str, parameters: Tuple = ()) -> List[aiosqlite.Row]:
        if not self.conn: return []
        async with self.conn.execute(sql, parameters) as cursor:
            return await cursor.fetchall()
            
    async def _init_tables(self):
        """Initialize database tables"""
        schema = """
        -- Users and Languages
        CREATE TABLE IF NOT EXISTS user_languages (
            user_id INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            proficiency_level TEXT, 
            is_native BOOLEAN DEFAULT FALSE,
            is_learning BOOLEAN DEFAULT FALSE,
            wants_practice BOOLEAN DEFAULT FALSE,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, language_code)
        );

        -- User Settings
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            preferred_language TEXT DEFAULT 'en',
            notifications_language_match BOOLEAN DEFAULT TRUE,
            notifications_word_of_day BOOLEAN DEFAULT TRUE,
            notifications_practice_reminder BOOLEAN DEFAULT TRUE,
            notifications_achievements BOOLEAN DEFAULT TRUE,
            timezone TEXT DEFAULT 'UTC',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Progression
        CREATE TABLE IF NOT EXISTS user_progression (
            user_id INTEGER PRIMARY KEY,
            total_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            current_streak INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            total_translations INTEGER DEFAULT 0,
            badges TEXT, -- JSON
            achievements TEXT, -- JSON
            last_active DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Words of Day
        CREATE TABLE IF NOT EXISTS words_of_day (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language_code TEXT NOT NULL,
            word TEXT NOT NULL,
            pronunciation TEXT,
            meaning TEXT NOT NULL,
            example TEXT,
            translations TEXT, 
            cultural_note TEXT,
            category TEXT DEFAULT 'common',
            last_shown DATE,
            times_shown INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Quiz Questions
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language_code TEXT NOT NULL,
            question_type TEXT NOT NULL, 
            difficulty TEXT NOT NULL, 
            question_text TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            wrong_answers TEXT, 
            explanation TEXT,
            points INTEGER DEFAULT 10,
            category TEXT, 
            times_answered INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self.conn.executescript(schema)
        await self.conn.commit()

    async def create_guild_settings(self, guild_id: int):
        await self.execute(
            "INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)",
            (guild_id,)
        )
