# app/api/__init__.py
from fastapi import APIRouter

from app.api.endpoints import auth, categories, points

# Create API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(points.router, prefix="/points", tags=["points"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
