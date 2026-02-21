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
            "color": "#F5E6C8",
            "ambiance": "soft_pages",
        },
        "Gentle hum": {
            "description": "A pleasant bustle of activity. Most volumes are in good shape.",
            "color": "#E8D5B7",
            "ambiance": "gentle_hum",
        },
        "Getting noisy": {
            "description": "The stacks are getting restless. Several volumes need attention.",
            "color": "#D4A574",
            "ambiance": "restless",
        },
        "Call for order": {
            "description": "Warning! Many volumes are gathering dust. Review needed urgently.",
            "color": "#C45D3E",
            "ambiance": "urgent",
        },
        "Closed for renovation": {
            "description": "The library needs serious attention. Knowledge is at risk.",
            "color": "#8B2500",
            "ambiance": "closed",
        },
    }

    mood_data = visuals.get(mood_name, visuals["Closed for renovation"])
    return {
        "mood": mood_name,
        "average_dewey_score": round(average_dewey_score, 1),
        **mood_data,
    }
