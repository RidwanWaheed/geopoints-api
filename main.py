from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import settings
from app.dependencies import init_db
from app.api.deps import cleanup_uow
from app.core.error_handlers import add_exception_handlers

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
)

# Set up CORS middleware
if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
