"""Simple in-memory rate limiter. For production, use Redis-based rate limiting."""
import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException, status

logger = logging.getLogger("pip.ratelimit")

# In-memory store: {key: [timestamp, ...]}
_requests: dict[str, list[float]] = defaultdict(list)

# Config
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # per window for authenticated users
RATE_LIMIT_MAX_PUBLIC = 30  # per window for unauthenticated users

# Cleanup stale keys every N requests to prevent memory leak
_request_counter = 0
_CLEANUP_INTERVAL = 500  # run full cleanup every 500 requests
_MAX_TRACKED_KEYS = 10000  # hard cap on tracked IPs


def _get_client_key(request: Request) -> str:
    """Get a unique key for the client — IP-based for simplicity."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _cleanup_old_entries(key: str, now: float):
    """Remove entries older than the window."""
    cutoff = now - RATE_LIMIT_WINDOW
    _requests[key] = [ts for ts in _requests[key] if ts > cutoff]


def _cleanup_all_stale_keys(now: float):
    """Remove keys with no recent requests to prevent unbounded memory growth."""
    cutoff = now - RATE_LIMIT_WINDOW
    stale_keys = [k for k, timestamps in _requests.items() if not timestamps or timestamps[-1] < cutoff]
    for k in stale_keys:
        del _requests[k]
    if stale_keys:
        logger.debug(f"Rate limiter cleanup: removed {len(stale_keys)} stale keys, {len(_requests)} remaining")


async def rate_limit_check(request: Request):
    """FastAPI dependency for rate limiting."""
    global _request_counter

    # Skip rate limiting for health checks and docs
    if request.url.path in ("/health", "/api/docs", "/api/redoc", "/openapi.json"):
        return

    key = _get_client_key(request)
    now = time.time()

    _cleanup_old_entries(key, now)

    # Periodic full cleanup to prevent memory leak
    _request_counter += 1
    if _request_counter >= _CLEANUP_INTERVAL or len(_requests) > _MAX_TRACKED_KEYS:
        _cleanup_all_stale_keys(now)
        _request_counter = 0

    # Determine limit based on auth
    auth_header = request.headers.get("authorization")
    max_requests = RATE_LIMIT_MAX_REQUESTS if auth_header else RATE_LIMIT_MAX_PUBLIC

    if len(_requests[key]) >= max_requests:
        retry_after = int(RATE_LIMIT_WINDOW - (now - _requests[key][0]))
        logger.warning(f"Rate limit exceeded for {key}: {len(_requests[key])}/{max_requests}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(max(retry_after, 1))},
        )

    _requests[key].append(now)
