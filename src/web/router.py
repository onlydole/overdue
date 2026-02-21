"""Web page routes (HTML responses)."""

from fastapi import APIRouter

from src.web.actions import router as actions_router
from src.web.auth import router as auth_router
from src.web.dashboard import router as dashboard_router
from src.web.how_to_play import router as how_to_play_router
from src.web.leaderboard import router as leaderboard_router
from src.web.my_library import router as my_library_router
from src.web.profile import router as profile_router
from src.web.shelves import router as shelves_router
from src.web.volumes import router as volumes_router

web_router = APIRouter()
web_router.include_router(auth_router)
web_router.include_router(actions_router)
web_router.include_router(my_library_router)
web_router.include_router(dashboard_router)
web_router.include_router(shelves_router)
web_router.include_router(volumes_router)
web_router.include_router(profile_router)
web_router.include_router(leaderboard_router)
web_router.include_router(how_to_play_router)
