"""
API v1 router aggregation
"""
from fastapi import APIRouter

from app.api.v1.endpoints import files, calculations, summaries

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    files.router, 
    prefix="/files", 
    tags=["files"]
)

api_router.include_router(
    calculations.router, 
    prefix="/calculations", 
    tags=["calculations"]
)

api_router.include_router(
    summaries.router, 
    prefix="/summaries", 
    tags=["summaries"]
)
