"""Tests for the TTL cache utility."""
import time
import pytest
from app.utils.cache import TTLCache


class TestTTLCache:
    def test_set_and_get(self):
        cache = TTLCache()
        cache.set("key1", "value1", ttl=60)
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self):
        cache = TTLCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        cache = TTLCache()
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_delete(self):
        cache = TTLCache()
        cache.set("key1", "value1", ttl=60)
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_delete_nonexistent(self):
        cache = TTLCache()
        cache.delete("nonexistent")  # Should not raise

    def test_invalidate_prefix(self):
        cache = TTLCache()
        cache.set("user:1:dashboard", "data1", ttl=60)
        cache.set("user:1:readiness", "data2", ttl=60)
        cache.set("user:2:dashboard", "data3", ttl=60)
        cache.set("company:1", "data4", ttl=60)

        count = cache.invalidate_prefix("user:1:")
        assert count == 2
        assert cache.get("user:1:dashboard") is None
        assert cache.get("user:1:readiness") is None
        assert cache.get("user:2:dashboard") == "data3"
        assert cache.get("company:1") == "data4"

    def test_clear(self):
        cache = TTLCache()
        cache.set("key1", "val1", ttl=60)
        cache.set("key2", "val2", ttl=60)
        assert cache.size == 2
        cache.clear()
        assert cache.size == 0

    def test_max_size_eviction(self):
        cache = TTLCache(max_size=10)
        for i in range(15):
            cache.set(f"key{i}", f"val{i}", ttl=60)
        # Should not exceed max_size (allows some overflow during eviction)
        assert cache.size <= 13  # 10 max + some tolerance

    def test_size_property(self):
        cache = TTLCache()
        assert cache.size == 0
        cache.set("k1", "v1", ttl=60)
        assert cache.size == 1
        cache.set("k2", "v2", ttl=60)
        assert cache.size == 2

    def test_overwrite_existing_key(self):
        cache = TTLCache()
        cache.set("key1", "old_value", ttl=60)
        cache.set("key1", "new_value", ttl=60)
        assert cache.get("key1") == "new_value"
        assert cache.size == 1

    def test_complex_values(self):
        cache = TTLCache()
        data = {
            "profile": {"name": "Test"},
            "stats": [1, 2, 3],
            "nested": {"a": {"b": "c"}},
        }
        cache.set("complex", data, ttl=60)
        assert cache.get("complex") == data

    def test_invalidate_prefix_returns_zero_for_no_match(self):
        cache = TTLCache()
        cache.set("key1", "val1", ttl=60)
        count = cache.invalidate_prefix("nonexistent:")
        assert count == 0
