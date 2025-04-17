import time
from collections import defaultdict
from typing import Dict, Tuple


class RateLimiter:
    def __init__(self):
        # Store request counts and timestamps per user/IP and path: {(ip_address, path): [(timestamp, count)]}
        self.requests: Dict[Tuple[str, str], list] = defaultdict(list)

    def is_rate_limited(self, key: str, path: str, limit: int, window: int) -> bool:
        """
        Check if the IP address is rate limited for a specific path

        Args:
            ip_address: Client IP address
            path: Request path
            limit: Maximum number of requests
            window: Time window in seconds

        Returns:
            True if rate limited, False otherwise
        """
        now = time.time()
        request_key = (key, path)

        # Remove expired timestamps
        self.requests[request_key] = [
            (ts, count) for ts, count in self.requests[request_key] if now - ts < window
        ]

        # Count total requests in the window
        total_requests = sum(count for _, count in self.requests[request_key])

        # Check if limit is exceeded
        if total_requests >= limit:
            return True

        # Record this request
        self.requests[request_key].append((now, 1))
        return False

    def get_remaining(self, key: str, path: str, limit: int, window: int) -> int:
        """Get remaining requests allowed in the current window"""
        now = time.time()
        request_key = (key, path)

        # Count total requests in the window
        total_requests = sum(
            count for ts, count in self.requests[request_key] if now - ts < window
        )

        return max(0, limit - total_requests)

    def get_reset_time(self, key: str, path: str, window: int) -> int:
        """Get seconds until the rate limit window resets"""
        now = time.time()
        request_key = (key, path)

        if not self.requests[request_key]:
            return 0

        # Find the oldest timestamp in current window
        oldest = min(ts for ts, _ in self.requests[request_key])

        return max(0, int(oldest + window - now))


# Create a global instance
rate_limiter = RateLimiter()
