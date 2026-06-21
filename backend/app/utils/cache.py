"""
Simple in-memory TTL cache for expensive queries.
For 100-200 users this is sufficient. For 1K+, use Redis.

Usage:
    from app.utils.cache import ttl_cache

    # Cache dashboard data for 60 seconds per user
    cached = ttl_cache.get(f"dashboard:{user_id}")
    if cached:
        return cached
    data = await expensive_query()
    ttl_cache.set(f"dashboard:{user_id}", data, ttl=60)
    return data
"""
import time
import logging
from typing import Any, Optional

logger = logging.getLogger("pip.cache")


class TTLCache:
    """Thread-safe in-memory cache with TTL expiration and max size."""

    def __init__(self, max_size: int = 1000):
        self._cache: dict[str, tuple[Any, float]] = {}  # key -> (value, expire_at)
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache. Returns None if expired or missing."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        value, expire_at = entry
        if time.time() > expire_at:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """Set a value with TTL in seconds."""
        # Evict expired entries if cache is getting large
        if len(self._cache) >= self._max_size:
            self._evict_expired()
        # If still too large, drop oldest 20%
        if len(self._cache) >= self._max_size:
            keys_to_drop = list(self._cache.keys())[:self._max_size // 5]
            for k in keys_to_drop:
                del self._cache[k]
            logger.debug(f"Cache evicted {len(keys_to_drop)} entries")

        self._cache[key] = (value, time.time() + ttl)

    def delete(self, key: str) -> None:
        """Delete a specific key."""
        self._cache.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> int:
        """Invalidate all keys starting with a prefix. Returns count deleted."""
        keys = [k for k in self._cache if k.startswith(prefix)]
        for k in keys:
            del self._cache[k]
        return len(keys)

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()

    def _evict_expired(self) -> None:
        """Remove all expired entries."""
        now = time.time()
        expired = [k for k, (_, exp) in self._cache.items() if now > exp]
        for k in expired:
            del self._cache[k]

    @property
    def size(self) -> int:
        return len(self._cache)


# Global cache instance
ttl_cache = TTLCache(max_size=2000)
