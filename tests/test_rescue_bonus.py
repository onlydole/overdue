"""Tests for the Rescue Bonus XP mechanic."""

from src.config.defaults import XP_RESCUE_BONUS, XP_REVIEW_CURRENT, XP_REVIEW_OVERDUE_MULTIPLIER


def test_rescue_bonus_constant():
    assert XP_RESCUE_BONUS == 20


def test_overdue_review_total_with_rescue():
    """Overdue review should yield base*multiplier + rescue = 30."""
    base = XP_REVIEW_CURRENT * XP_REVIEW_OVERDUE_MULTIPLIER
    assert base + XP_RESCUE_BONUS == 30


def test_current_review_no_rescue():
    """Current volume review earns only base 5 XP."""
    assert XP_REVIEW_CURRENT == 5
