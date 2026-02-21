"""API router aggregation."""

from fastapi import APIRouter

from src.api.reading_room import router as reading_room_router
from src.api.shelves import router as shelves_router
from src.api.volumes import router as volumes_router

api_router = APIRouter()
api_router.include_router(volumes_router, prefix="/volumes", tags=["Volumes"])
api_router.include_router(shelves_router, prefix="/shelves", tags=["Shelves"])
api_router.include_router(reading_room_router, prefix="/reading-room", tags=["Reading Room"])
