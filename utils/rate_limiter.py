"""Simple in-memory rate limiter to prevent bot abuse."""
import time
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Limits users to a max number of messages per time window."""

    def __init__(self, max_requests=5, window_seconds=10):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {user_id: [timestamp, ...]}

    def is_allowed(self, user_id):
        """Returns True if user is within rate limit, False if throttled."""
        now = time.time()
        if user_id not in self.requests:
            self.requests[user_id] = []

        # Remove old timestamps outside the window
        self.requests[user_id] = [
            t for t in self.requests[user_id]
            if now - t < self.window_seconds
        ]

        if len(self.requests[user_id]) >= self.max_requests:
            logger.warning(f"Rate limited user {user_id}: {len(self.requests[user_id])} requests in {self.window_seconds}s")
            return False

        self.requests[user_id].append(now)
        return True


# Singleton instance — 5 messages per 10 seconds
rate_limiter = RateLimiter(max_requests=5, window_seconds=10)
