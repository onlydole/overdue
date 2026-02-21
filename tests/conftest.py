"""Shared test fixtures for Overdue."""

import pytest


@pytest.fixture
def sample_volume_data():
    """Return sample data for creating a volume."""
    return {
        "title": "The Art of Code Review",
        "content": "A comprehensive guide to reviewing code effectively.",
        "shelf_id": 1,
        "bookmarks": ["code-review", "best-practices"],
    }


@pytest.fixture
def sample_shelf_data():
    """Return sample data for creating a shelf."""
    return {
        "name": "Software Engineering",
        "description": "Volumes about software development practices.",
    }
