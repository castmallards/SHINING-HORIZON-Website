"""Simple in-memory TTL cache for hot read paths.

Per ARCHITECTURE.md §7: 60-second TTL on category lists, brand lists, sitemap.
Invalidated on any write through service-layer hooks.

Single-process safe (uses a threading lock). For multi-process deployments,
swap the implementation for Redis — keep the same interface.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Callable, Optional


class TTLCache:
    def __init__(self, default_ttl: float = 60.0):
        self._default_ttl = default_ttl
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                self._store.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        ttl = self._default_ttl if ttl is None else ttl
        with self._lock:
            self._store[key] = (time.monotonic() + ttl, value)

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: Optional[float] = None) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = factory()
        self.set(key, value, ttl=ttl)
        return value

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> None:
        with self._lock:
            for k in [k for k in self._store if k.startswith(prefix)]:
                self._store.pop(k, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


cache = TTLCache(default_ttl=60.0)


def invalidate_public() -> None:
    """Invalidate every cached public read. Call from service-layer write hooks."""
    cache.invalidate_prefix("public:")
