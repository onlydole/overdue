"""Tests for mood calculation and middleware."""

from src.game.mood import calculate_mood


def test_quiet_study_mood():
    """Average score >= 80 should produce soft_pages ambiance."""
    mood = calculate_mood(85.0)
    assert mood["ambiance"] == "soft_pages"
    assert mood["mood"] == "Quiet study"


def test_gentle_hum_mood():
    """Average score 60-79 should produce gentle_hum ambiance."""
    mood = calculate_mood(70.0)
    assert mood["ambiance"] == "gentle_hum"
    assert mood["mood"] == "Gentle hum"


def test_restless_mood():
    """Average score 40-59 should produce restless ambiance."""
    mood = calculate_mood(45.0)
    assert mood["ambiance"] == "restless"
    assert mood["mood"] == "Getting noisy"


def test_urgent_mood():
    """Average score 20-39 should produce urgent ambiance."""
    mood = calculate_mood(25.0)
    assert mood["ambiance"] == "urgent"
    assert mood["mood"] == "Call for order"


def test_closed_mood():
    """Average score < 20 should produce closed ambiance."""
    mood = calculate_mood(10.0)
    assert mood["ambiance"] == "closed"
    assert mood["mood"] == "Closed for renovation"


def test_empty_library_defaults_pristine():
    """An empty library (score 100) should be quiet study."""
    mood = calculate_mood(100.0)
    assert mood["ambiance"] == "soft_pages"
