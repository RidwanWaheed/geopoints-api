from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import settings
from app.dependencies import init_db
from app.api.deps import cleanup_uow
from app.core.error_handlers import add_exception_handlers
from app.middleware.rate_limiting import RateLimitMiddleware
from app.middleware.query_monitor import QueryMonitorMiddleware


# Define rate limit tiers
STANDARD_TIER = {"limit": 100, "window": 60}  # 100 requests per minute
INTENSIVE_TIER = {"limit": 20, "window": 60}  # 20 requests per minute
WRITE_TIER = {"limit": 30, "window": 60}      # 30 requests per minute
AUTH_TIER = {"limit": 5, "window": 60}        # 5 requests per minute

# Initialize the database
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    cleanup_uow()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    contact={
        "name": "Ridwan Waheed",
        "email": "waheedridwan96@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Add query monitoring middleware
app.add_middleware(QueryMonitorMiddleware)

# Add rate limiting middleware with path-specific limits
app.add_middleware(
    RateLimitMiddleware,
    default_limit=100,      # Default: 100 requests per minute
    default_window=60,
    path_limits={
        # Intensive operations
        f"{settings.API_V1_STR}/points/nearby": INTENSIVE_TIER,
        f"{settings.API_V1_STR}/points/within": INTENSIVE_TIER,
        f"{settings.API_V1_STR}/points/nearest": INTENSIVE_TIER,
        
        # Write operations (POST, PUT, DELETE handled in middleware)
        f"{settings.API_V1_STR}/points": WRITE_TIER, 
        f"{settings.API_V1_STR}/categories": WRITE_TIER,
        
        # Default for everything else
        "*": STANDARD_TIER
    },
    authenticated_limits={
        # Higher limits for authenticated users
        f"{settings.API_V1_STR}/points/nearby": {"limit": 200, "window": 60},
        f"{settings.API_V1_STR}/points/within": {"limit": 100, "window": 60},
        f"{settings.API_V1_STR}/points": {"limit": 100, "window": 60},
    }
)

# Set up CORS middleware
if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["X-Total-Count"],
        max_age=600,  # 10 minutes cache for preflight requests
    )

    print(
        settings.BACKEND_CORS_ORIGINS
    )  # Should print a comma-separated string from the .env file
    print(settings.backend_cors_origins)  # Should print a list


# Add a simple test endpoint
@app.get("/")
def root():
    return {"message": "Welcome to GeoPoints API"}


# Add exception handlers
add_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Add health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
