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
from sqlalchemy.orm import DeclarativeBase, relationship


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

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    shelf_id = Column(Integer, ForeignKey("shelves.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("librarians.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)

    shelf = relationship("ShelfRow", back_populates="volumes")
    author = relationship("LibrarianRow", back_populates="volumes")
    reviews = relationship("ReviewRow", back_populates="volume", cascade="all, delete-orphan")


class ShelfRow(Base):
    """A categorized shelf holding volumes."""

    __tablename__ = "shelves"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("librarians.id"), nullable=False)

    volumes = relationship("VolumeRow", back_populates="shelf", cascade="all, delete-orphan")
    creator = relationship("LibrarianRow", back_populates="shelves_created")


class LibrarianRow(Base):
    """An authenticated user of the library."""

    __tablename__ = "librarians"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="Page", nullable=False)
    total_xp = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    volumes = relationship("VolumeRow", back_populates="author")
    shelves_created = relationship("ShelfRow", back_populates="creator")
    xp_ledger = relationship("XPLedgerRow", back_populates="librarian", cascade="all, delete-orphan")
    badges = relationship("BadgeRow", back_populates="librarian", cascade="all, delete-orphan")
    streak = relationship("StreakRow", back_populates="librarian", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("ReviewRow", back_populates="librarian", cascade="all, delete-orphan")


class ReviewRow(Base):
    """A record of a librarian reviewing a volume."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    volume_id = Column(Integer, ForeignKey("volumes.id"), nullable=False)
    librarian_id = Column(Integer, ForeignKey("librarians.id"), nullable=False)
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    dewey_score_before = Column(Float, nullable=False)

    volume = relationship("VolumeRow", back_populates="reviews")
    librarian = relationship("LibrarianRow", back_populates="reviews")


class XPLedgerRow(Base):
    """Tracks XP (pages read) awards."""

    __tablename__ = "xp_ledger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    librarian_id = Column(Integer, ForeignKey("librarians.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    librarian = relationship("LibrarianRow", back_populates="xp_ledger")


class BadgeRow(Base):
    """Achievement badges earned by librarians."""

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    librarian_id = Column(Integer, ForeignKey("librarians.id"), nullable=False)
    badge_name = Column(String(100), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    librarian = relationship("LibrarianRow", back_populates="badges")


class StreakRow(Base):
    """Daily review streak tracking."""

    __tablename__ = "streaks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    librarian_id = Column(Integer, ForeignKey("librarians.id"), nullable=False, unique=True)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_review_date = Column(DateTime, nullable=True)

    librarian = relationship("LibrarianRow", back_populates="streak")


class BulletinRow(Base):
    """Webhook subscription (bulletin board posting)."""

    __tablename__ = "bulletins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False)
    events = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False, default="")
    librarian_id = Column(Integer, ForeignKey("librarians.id"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
