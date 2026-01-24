
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Bot Configuration"""
    
    # Discord
    TOKEN = os.getenv("DISCORD_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))
    
    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    
    # Database
    DB_PATH = "data/translations.db"
    
    # Cache TTL (in seconds)
    CACHE_TTL: Dict[str, int] = {
        "translation": 604800,      # 7 days
        "language_detect": 2592000, # 30 days
        "rate_limit": 60,           # 1 minute
        "session": 600,             # 10 minutes
        "tts": 2592000,             # 30 days
        "user_settings": 3600,      # 1 hour
    }
    
    # Rate Limits
    RATE_LIMITS: Dict[str, Dict[str, Any]] = {
        "translate": {"limit": 30, "window": 60},      # 30 per minute
        "quiz": {"limit": 5, "window": 60},            # 5 per minute
        "pronounce": {"limit": 10, "window": 60},      # 10 per minute
        "word_of_day": {"limit": 20, "window": 3600},  # 20 per hour
    }
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {
        "ru": {"name": "Русский", "flag": "🇷🇺", "tts_code": "ru"},
        "en": {"name": "English", "flag": "🇬🇧", "tts_code": "en"},
        "ko": {"name": "한국어", "flag": "🇰🇷", "tts_code": "ko"},
        "pt": {"name": "Português", "flag": "🇵🇹", "tts_code": "pt"},
        "es": {"name": "Español", "flag": "🇪🇸", "tts_code": "es"},
        "de": {"name": "Deutsch", "flag": "🇩🇪", "tts_code": "de"},
    }
    
    # XP System
    XP_REWARDS = {
        "translation": 5,
        "word_of_day_view": 10,
        "word_save": 5,
        "quiz_easy": 50,
        "quiz_medium": 100,
        "quiz_hard": 200,
        "quiz_perfect": 150,
        "daily_streak": 20,
        "find_partner": 100,
        "cultural_note": 30,
        "voice_event": 50,
    }
    
    # Levels
    LEVEL_THRESHOLDS = {
        1: 0,
        2: 100,
        3: 250,
        4: 500,
        5: 1000,   # Polyglot
        6: 2000,
        7: 3500,
        8: 5500,
        9: 8000,
        10: 12000, # Language Master
        # ... extend as needed
    }
    
    # Word of Day
    WORD_OF_DAY_TIME = "10:00"  # UTC
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/bot.log"
    
    # Paths
    AUDIO_CACHE_DIR = "audio_cache"
    
    # Feature flags
    FEATURES = {
        "tts_enabled": True,
        "quiz_enabled": True,
        "word_of_day_enabled": True,
        "language_exchange_enabled": True,
        "voice_rooms_enabled": True,
        "tournaments_enabled": True,
    }
