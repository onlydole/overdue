"""SQLAlchemy table definitions for the Overdue knowledge library."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# Association table for volume bookmarks (tags)
volume_bookmarks = Table(
    "volume_bookmarks",
    Base.metadata,
    Column("volume_id", Integer, ForeignKey("volumes.id"), primary_key=True),
    Column("bookmark", String(100), primary_key=True),
)


class VolumeRow(Base):
    """A volume of knowledge on a shelf."""

    __tablename__ = "volumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(60), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    shelf_id: Mapped[int] = mapped_column(Integer, ForeignKey("shelves.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("librarians.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_reviewed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    spine_seed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    shelf: Mapped["ShelfRow"] = relationship("ShelfRow", back_populates="volumes")
    author: Mapped["LibrarianRow"] = relationship("LibrarianRow", back_populates="volumes")
    reviews: Mapped[list["ReviewRow"]] = relationship(
        "ReviewRow", back_populates="volume", cascade="all, delete-orphan"
    )


class ShelfRow(Base):
    """A categorized shelf holding volumes."""

    __tablename__ = "shelves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("librarians.id"), nullable=False)

    volumes: Mapped[list["VolumeRow"]] = relationship(
        "VolumeRow", back_populates="shelf", cascade="all, delete-orphan"
    )
    creator: Mapped["LibrarianRow"] = relationship(
        "LibrarianRow", back_populates="shelves_created"
    )


class LibrarianRow(Base):
    """An authenticated user of the library."""

    __tablename__ = "librarians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="Page", nullable=False)
    total_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bot_difficulty: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar_id: Mapped[str] = mapped_column(String(20), default="avatar_01", nullable=False)

    volumes: Mapped[list["VolumeRow"]] = relationship("VolumeRow", back_populates="author")
    shelves_created: Mapped[list["ShelfRow"]] = relationship(
        "ShelfRow", back_populates="creator"
    )
    xp_ledger: Mapped[list["XPLedgerRow"]] = relationship(
        "XPLedgerRow", back_populates="librarian", cascade="all, delete-orphan"
    )
    badges: Mapped[list["BadgeRow"]] = relationship(
        "BadgeRow", back_populates="librarian", cascade="all, delete-orphan"
    )
    streak: Mapped["StreakRow | None"] = relationship(
        "StreakRow", back_populates="librarian", uselist=False, cascade="all, delete-orphan"
    )
    reviews: Mapped[list["ReviewRow"]] = relationship(
        "ReviewRow", back_populates="librarian", cascade="all, delete-orphan"
    )


class ReviewRow(Base):
    """A record of a librarian reviewing a volume."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    volume_id: Mapped[int] = mapped_column(Integer, ForeignKey("volumes.id"), nullable=False)
    librarian_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("librarians.id"), nullable=False
    )
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    dewey_score_before: Mapped[float] = mapped_column(Float, nullable=False)

    volume: Mapped["VolumeRow"] = relationship("VolumeRow", back_populates="reviews")
    librarian: Mapped["LibrarianRow"] = relationship("LibrarianRow", back_populates="reviews")


class XPLedgerRow(Base):
    """Tracks XP (pages read) awards."""

    __tablename__ = "xp_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    librarian_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("librarians.id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    librarian: Mapped["LibrarianRow"] = relationship("LibrarianRow", back_populates="xp_ledger")


class BadgeRow(Base):
    """Achievement badges earned by librarians."""

    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    librarian_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("librarians.id"), nullable=False
    )
    badge_name: Mapped[str] = mapped_column(String(100), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    librarian: Mapped["LibrarianRow"] = relationship("LibrarianRow", back_populates="badges")


class StreakRow(Base):
    """Daily review streak tracking."""

    __tablename__ = "streaks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    librarian_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("librarians.id"), nullable=False, unique=True
    )
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_review_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    librarian: Mapped["LibrarianRow"] = relationship("LibrarianRow", back_populates="streak")


class BulletinRow(Base):
    """Webhook subscription (bulletin board posting)."""

    __tablename__ = "bulletins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    events: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    librarian_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("librarians.id"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
