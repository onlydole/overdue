"""Constants and default values for the Overdue knowledge library."""

# ---------------------------------------------------------------------------
# Dewey Score thresholds
# ---------------------------------------------------------------------------
DEWEY_PRISTINE = 100
DEWEY_GOOD_SHAPE = 75
DEWEY_NEEDS_ATTENTION = 50
DEWEY_OVERDUE = 25
DEWEY_LOST = 0

# Decay rate: points lost per unit time since last review
# Unit is seconds (default: 10 seconds = fast demo mode)
# For realistic mode, set OVERDUE_DEWEY_DECAY_SECONDS to 86400 (1 day)
DEWEY_DECAY_RATE = 3
DEWEY_DECAY_SECONDS = 10  # how many seconds = one decay unit

# ---------------------------------------------------------------------------
# XP awards ("pages read")
# ---------------------------------------------------------------------------
XP_SHELVE_VOLUME = 10
XP_REVIEW_CURRENT = 5
XP_REVIEW_OVERDUE_MULTIPLIER = 2  # overdue reviews earn base * multiplier
XP_DAILY_STREAK_BONUS = 15
XP_SHELF_BONUS = 50  # all volumes on a shelf above DEWEY_GOOD_SHAPE

# ---------------------------------------------------------------------------
# Rank thresholds
# ---------------------------------------------------------------------------
RANKS: list[tuple[str, int]] = [
    ("Page", 0),
    ("Shelver", 100),
    ("Librarian", 500),
    ("Archivist", 2000),
    ("Head Librarian", 5000),
]

# ---------------------------------------------------------------------------
# Reading Room mood thresholds (average Dewey score)
# ---------------------------------------------------------------------------
MOODS: list[tuple[str, int]] = [
    ("Quiet study", 80),
    ("Gentle hum", 60),
    ("Getting noisy", 40),
    ("Call for order", 20),
    ("Closed for renovation", 0),
]

# ---------------------------------------------------------------------------
# Rate limiting (quiet hours)
# ---------------------------------------------------------------------------
QUIET_HOURS_REQUESTS_PER_MINUTE = 60
QUIET_HOURS_BURST = 10
