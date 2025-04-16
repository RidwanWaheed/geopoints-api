# app/middleware/rate_limiting.py
from typing import Dict, Tuple
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.core.limiter import rate_limiter

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: FastAPI, 
        default_limit: int = 100,       # Default limit
        default_window: int = 60,       # Default window in seconds
        path_limits: Dict[str, Dict] = None  # Path-specific limits
    ):
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window
        self.path_limits = path_limits or {}
    
    def _get_limit_for_request(self, path: str, method: str) -> Tuple[int, int]:
        """Get the rate limit configuration for a path and method"""
        # Check for exact path+method match (e.g., "/api/points:POST")
        path_method_key = f"{path}:{method}"
        if path_method_key in self.path_limits:
            config = self.path_limits[path_method_key]
            return config.get("limit", self.default_limit), config.get("window", self.default_window)
        
        # Check for exact path match
        if path in self.path_limits:
            config = self.path_limits[path]
            return config.get("limit", self.default_limit), config.get("window", self.default_window)
        
        # If it's a write operation, use write tier if defined
        if method in ("POST", "PUT", "DELETE") and "WRITE" in self.path_limits:
            config = self.path_limits["WRITE"]
            return config.get("limit", self.default_limit), config.get("window", self.default_window)
        
        # If there's a wildcard config, use that
        if "*" in self.path_limits:
            config = self.path_limits["*"]
            return config.get("limit", self.default_limit), config.get("window", self.default_window)
        
        # Otherwise use defaults
        return self.default_limit, self.default_window
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "0.0.0.0"
        
        # Get path
        path = request.url.path
        
        # Get limit for this path
        limit, window = self._get_limit_for_path(path)
        
        # Check if rate limited
        if rate_limiter.is_rate_limited(client_ip, path, limit, window):
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(window)}
            )
            
        # Continue with the request
        response = await call_next(request)
        return response