import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self):
        # Store request counts and timestamps per IP and path: {(ip_address, path): [(timestamp, count)]}
        self.requests: Dict[Tuple[str, str], list] = defaultdict(list)
    
    def is_rate_limited(self, ip_address: str, path: str, limit: int, window: int) -> bool:
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
        key = (ip_address, path)
        
        # Remove expired timestamps
        self.requests[key] = [
            (ts, count) for ts, count in self.requests[key]
            if now - ts < window
        ]
        
        # Count total requests in the window
        total_requests = sum(count for _, count in self.requests[key])
        
        # Check if limit is exceeded
        if total_requests >= limit:
            return True
            
        # Record this request
        self.requests[key].append((now, 1))
        return False

# Create a global instance
rate_limiter = RateLimiter()