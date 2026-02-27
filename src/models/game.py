"""Pydantic models for game mechanics."""

from datetime import datetime

from pydantic import BaseModel


class XPAward(BaseModel):
    """A single XP award entry."""

    amount: int
    reason: str
    created_at: datetime


class XPSummary(BaseModel):
    """Summary of a librarian's XP and rank."""

    total_xp: int
    rank: str
    next_rank: str | None
    xp_to_next_rank: int | None
    recent_awards: list[XPAward]


class BadgeDefinition(BaseModel):
    """Definition of an achievable badge."""

    name: str
    description: str
    icon: str


class BadgeEarned(BaseModel):
    """A badge earned by a librarian."""

    name: str
    description: str
    icon: str
    tier: str = "Common"
    earned_at: datetime


class StreakInfo(BaseModel):
    """Streak information for a librarian."""

    current_streak: int
    longest_streak: int
    last_review_date: datetime | None


class LeaderboardEntry(BaseModel):
    """A single entry on the leaderboard."""

    rank_position: int
    username: str
    total_xp: int
    librarian_rank: str
    badge_count: int
    current_streak: int


class LeaderboardResponse(BaseModel):
    """Full leaderboard response."""

    entries: list[LeaderboardEntry]
    total_librarians: int


class ReadingRoomMood(BaseModel):
    """Current mood of the reading room."""

    mood: str
    average_dewey_score: float
    total_volumes: int
    overdue_volumes: int
    description: str


class GameResult(BaseModel):
    """Structured feedback from a game action (shelve/review)."""

    xp_awarded: int = 0
    xp_breakdown: list[dict[str, str | int]] = []
    total_xp: int = 0
    rank: str = "Page"
    rank_changed: bool = False
    new_rank: str | None = None
    badges_earned: list[str] = []
    streak: int = 0
    streak_bonus_awarded: bool = False
