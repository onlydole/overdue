"""Reading room mood calculation based on aggregate Dewey Scores."""

from src.config.defaults import MOODS


def calculate_mood(average_dewey_score: float) -> dict:
    """Calculate the reading room mood from the average Dewey Score."""
    mood_name = "Closed for renovation"
    for name, threshold in MOODS:
        if average_dewey_score >= threshold:
            mood_name = name
            break

    visuals = {
        "Quiet study": {
            "description": "Warm golden light fills the reading room. Knowledge is well-tended.",
            "color": "#5cdb5c",
            "ambiance": "soft_pages",
        },
        "Gentle hum": {
            "description": "A pleasant bustle of activity. Most volumes are in good shape.",
            "color": "#a0d468",
            "ambiance": "gentle_hum",
        },
        "Getting noisy": {
            "description": "The shelves are getting restless. Several volumes need attention.",
            "color": "#f6bb42",
            "ambiance": "restless",
        },
        "Call for order": {
            "description": "Warning! Many volumes are gathering dust. Review needed urgently.",
            "color": "#e8563e",
            "ambiance": "urgent",
        },
        "Closed for renovation": {
            "description": "The library needs serious attention. Knowledge is at risk.",
            "color": "#9e1b1b",
            "ambiance": "closed",
        },
    }

    mood_data = visuals.get(mood_name, visuals["Closed for renovation"])
    return {
        "mood": mood_name,
        "average_dewey_score": round(average_dewey_score, 1),
        **mood_data,
    }
