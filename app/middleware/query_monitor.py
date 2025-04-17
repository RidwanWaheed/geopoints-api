import time
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class QueryMonitorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, log_slow_queries: bool = True, threshold_ms: int = 500):
        super().__init__(app)
        self.log_slow_queries = log_slow_queries
        self.threshold_ms = threshold_ms
    
    async def dispatch(self, request: Request, call_next):
        # Only monitor spatial API endpoints
        path = request.url.path
        if "/api/v1/points/nearby" in path or "/api/v1/points/within" in path or "/api/v1/points/nearest" in path:
            start_time = time.time()
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Add timing header
            response.headers["X-Process-Time-Ms"] = str(int(process_time))
            
            # Log slow queries
            if self.log_slow_queries and process_time > self.threshold_ms:
                logger.warning(
                    f"Slow spatial query detected: {path} took {process_time:.2f}ms "
                    f"(threshold: {self.threshold_ms}ms)"
                )
            
            return response
        
        return await call_next(request)