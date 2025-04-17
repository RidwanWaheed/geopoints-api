from typing import Dict, Optional, Tuple

from fastapi import FastAPI, Request, Response
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.config import settings
from app.core.limiter import rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        default_limit: int = 100,
        default_window: int = 60,
        path_limits: Dict[str, Dict] = None,
        authenticated_limits: Dict[str, Dict] = None,
    ):
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window
        self.path_limits = path_limits or {}
        self.authenticated_limits = authenticated_limits or {}

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token if present"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "")
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload.get("sub")
        except JWTError:
            return None

    def _get_limit_for_request(
        self, path: str, method: str, is_authenticated: bool
    ) -> Tuple[int, int]:
        """Get rate limits based on path, method and authentication status"""
        # Check for authenticated user specific limits
        if is_authenticated and path in self.authenticated_limits:
            config = self.authenticated_limits[path]
            return config.get("limit", self.default_limit * 2), config.get(
                "window", self.default_window
            )

        # Check for exact path+method match (e.g., "/api/points:POST")
        path_method_key = f"{path}:{method}"
        if path_method_key in self.path_limits:
            config = self.path_limits[path_method_key]
            return config.get("limit", self.default_limit), config.get(
                "window", self.default_window
            )

        # Check for exact path match
        if path in self.path_limits:
            config = self.path_limits[path]
            return config.get("limit", self.default_limit), config.get(
                "window", self.default_window
            )

        # If it's a write operation, use write tier if defined
        if method in ("POST", "PUT", "DELETE") and "WRITE" in self.path_limits:
            config = self.path_limits["WRITE"]
            return config.get("limit", self.default_limit), config.get(
                "window", self.default_window
            )

        # If there's a wildcard config, use that
        if "*" in self.path_limits:
            config = self.path_limits["*"]
            return config.get("limit", self.default_limit), config.get(
                "window", self.default_window
            )

        # Otherwise use defaults
        return self.default_limit, self.default_window

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "0.0.0.0"

        # Get path and method
        path = request.url.path
        method = request.method

        # Extract user ID if authenticated
        user_id = self._extract_user_id(request)
        is_authenticated = user_id is not None

        # Get limit for this request
        limit, window = self._get_limit_for_request(path, method, is_authenticated)

        # Use user_id for rate limiting if authenticated, otherwise use IP
        key = user_id if is_authenticated else client_ip

        # Check if rate limited
        if rate_limiter.is_rate_limited(key, path, limit, window):
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(window)},
            )

        # Continue with the request
        response = await call_next(request)

        # Add rate limit headers
        remaining = rate_limiter.get_remaining(key, path, limit, window)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            rate_limiter.get_reset_time(key, path, window)
        )

        return response
