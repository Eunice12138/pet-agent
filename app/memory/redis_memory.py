import json
import redis
from typing import List, Dict, Optional

from app.core.config import settings


class RedisMemory:
    """基于 Redis 的对话记忆管理"""

    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        self.ttl = settings.REDIS_MEMORY_TTL
        self.max_history = settings.REDIS_MAX_HISTORY

    def _key(self, user_id: int) -> str:
        """每个用户一个独立的 key"""
        return f"chat:history:{user_id}"

    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """获取用户的对话历史"""
        key = self._key(user_id)
        raw = self.client.lrange(key, 0, -1)
        # 存储时是 JSON 字符串，反序列化
        history = []
        for item in raw:
            try:
                history.append(json.loads(item))
            except json.JSONDecodeError:
                continue
        return history

    def append(self, user_id: int, role: str, content: str) -> None:
        """追加一条消息到历史"""
        key = self._key(user_id)
        message = {"role": role, "content": content}
        self.client.rpush(key, json.dumps(message, ensure_ascii=False))
        # 只保留最近 N 条（每轮 2 条：user + assistant）
        self.client.ltrim(key, -self.max_history * 2, -1)
        # 设置过期时间
        self.client.expire(key, self.ttl)

    def clear(self, user_id: int) -> None:
        """清空某个用户的对话历史"""
        self.client.delete(self._key(user_id))


# 单例
memory = RedisMemory()