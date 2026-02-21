"""API router aggregation."""

from fastapi import APIRouter

from src.api.bulletins import router as bulletins_router
from src.api.catalog import router as catalog_router
from src.api.reading_room import router as reading_room_router
from src.api.shelves import router as shelves_router
from src.api.volumes import router as volumes_router
from src.auth.librarian import router as librarian_router

api_router = APIRouter()
api_router.include_router(librarian_router, prefix="/librarians", tags=["Librarians"])
api_router.include_router(volumes_router, prefix="/volumes", tags=["Volumes"])
api_router.include_router(shelves_router, prefix="/shelves", tags=["Shelves"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["Catalog"])
api_router.include_router(reading_room_router, prefix="/reading-room", tags=["Reading Room"])
api_router.include_router(bulletins_router, prefix="/bulletins", tags=["Bulletins"])
