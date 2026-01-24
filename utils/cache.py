
import redis.asyncio as redis
from typing import Optional, Any
import hashlib
import json
import logging
from config import Config

logger = logging.getLogger('TranslatorBot')

class RedisCache:
    def __init__(self):
        self.url = f"redis://{Config.REDIS_PASSWORD}@{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}"
        if not Config.REDIS_PASSWORD:
             self.url = f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}"
             
        self.redis: Optional[redis.Redis] = None
        self.connected = False
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            await self.redis.ping()
            self.connected = True
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.error(f"❌ Redis unavailable: {e}")
            self.connected = False
    
    async def close(self):
        if self.redis:
            await self.redis.close()
            logger.info("Redis disconnected")
    
    def _hash_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    async def get_translation(self, text: str, source: str, target: str) -> Optional[str]:
        if not self.connected: 
            return None
        try:
            key = f"translate:{self._hash_key(text)}:{source}:{target}"
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set_translation(self, text: str, source: str, target: str, translation: str) -> bool:
        if not self.connected:
            return False
        try:
            key = f"translate:{self._hash_key(text)}:{source}:{target}"
            await self.redis.setex(key, Config.CACHE_TTL["translation"], translation)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def get_detected_language(self, text: str) -> Optional[str]:
        if not self.connected:
            return None
        try:
            key = f"detect:{self._hash_key(text)}"
            return await self.redis.get(key)
        except:
            return None

    async def set_detected_language(self, text: str, language: str) -> bool:
        if not self.connected: 
             return False
        try:
            key = f"detect:{self._hash_key(text)}"
            await self.redis.setex(key, Config.CACHE_TTL["language_detect"], language)
            return True
        except:
            return False

    async def get_user_settings(self, user_id: int) -> Optional[dict]:
        if not self.connected:
            return None
        try:
            key = f"user:{user_id}:settings"
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except:
            return None
            
    async def set_user_settings(self, user_id: int, settings: dict) -> bool:
        if not self.connected:
            return False
        try:
            key = f"user:{user_id}:settings"
            await self.redis.setex(key, Config.CACHE_TTL["user_settings"], json.dumps(settings))
            return True
        except:
            return False
            
cache = RedisCache()
