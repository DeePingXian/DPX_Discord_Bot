import redis
import logging
import json

class CacheService:
    """Redis Cache and State Management Service"""
    
    def __init__(self, redis_url):
        self.logger = logging.getLogger("Cache")
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.client.ping()
            self.logger.info("Connected to Redis cache.")
        except Exception as e:
            self.logger.critical(f"Redis connection failed: {e}")
            raise

    def set_json(self, key, data, ex=None):
        """Store dictionary as JSON string"""
        self.client.set(key, json.dumps(data), ex=ex)

    def get_json(self, key):
        """Retrieve JSON string as dictionary"""
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except (json.JSONDecodeError, TypeError):
            return None

    # --- Music Queue Management ---
    def push_queue(self, guild_id, music_data):
        self.client.rpush(f"music_queue:{guild_id}", json.dumps(music_data))

    def pop_queue(self, guild_id):
        data = self.client.lpop(f"music_queue:{guild_id}")
        return json.loads(data) if data else None

    def get_queue(self, guild_id):
        items = self.client.lrange(f"music_queue:{guild_id}", 0, -1)
        results = []
        for i in items:
            try:
                results.append(json.loads(i))
            except json.JSONDecodeError:
                continue
        return results

    def get_queue_len(self, guild_id):
        return self.client.llen(f"music_queue:{guild_id}")

    def clear_queue(self, guild_id):
        self.client.delete(f"music_queue:{guild_id}")

    # --- Music State Operations ---
    def set_current_music(self, guild_id, music_data):
        self.set_json(f"music_current:{guild_id}", music_data)

    def get_current_music(self, guild_id):
        return self.get_json(f"music_current:{guild_id}")

    def clear_current_music(self, guild_id):
        self.client.delete(f"music_current:{guild_id}")

    def set_loop(self, guild_id, state: bool):
        self.client.set(f"music_loop:{guild_id}", 1 if state else 0)

    def get_loop(self, guild_id) -> bool:
        state = self.client.get(f"music_loop:{guild_id}")
        return state == "1"

    def clear_all_music_data(self, guild_id):
        """Cleanup all music related data for a guild"""
        keys = [
            f"music_queue:{guild_id}",
            f"music_current:{guild_id}",
            f"music_loop:{guild_id}"
        ]
        self.client.delete(*keys)

    def scan_and_delete_music_data(self):
        """Safer way to clear all music data across all guilds using SCAN (Non-blocking)"""
        cursor = 0
        while True:
            cursor, keys = self.client.scan(cursor=cursor, match="music_*", count=100)
            if keys:
                self.client.delete(*keys)
            if cursor == 0:
                break
