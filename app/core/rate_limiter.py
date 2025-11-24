# This can be made better. For now it is a simple in-memory rate limiter

from fastapi import HTTPException, status
from time import time

requests_log = {}

def rate_limit(ip: str, max_requests=10, window_seconds=60):
    now = time()
    history = requests_log.get(ip, [])

    # keep only recent requests
    history = [t for t in history if now - t < window_seconds]
    requests_log[ip] = history

    if len(history) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests"
        )

    history.append(now)
