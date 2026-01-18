"""
Configuration and constants for the Music Sociology Dashboard pipeline.
"""

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SOURCE_DIR = BASE_DIR / "source_data"
PROCESSED_DIR = DATA_DIR / "processed"
LYRICS_DIR = PROCESSED_DIR / "lyrics"
LOGS_DIR = DATA_DIR / "logs"

# Source data files (Kaggle dataset)
KAGGLE_CSV = SOURCE_DIR / "all_songs_data.csv"

# Year range (dataset coverage)
START_YEAR = 1959
END_YEAR = 2023

# Output paths
DATA_JSON = PROCESSED_DIR / "data.json"
EVENTS_JSON = PROCESSED_DIR / "events.json"

# Ensure directories exist
for directory in [PROCESSED_DIR, LYRICS_DIR, LOGS_DIR,
                  LYRICS_DIR / "by_decade", LYRICS_DIR / "by_genre", LYRICS_DIR / "by_year"]:
    directory.mkdir(parents=True, exist_ok=True)


def check_source_data():
    """Verify Kaggle source data exists."""
    if not KAGGLE_CSV.exists():
        print(f"ERROR: Source data not found at {KAGGLE_CSV}")
        print("Please ensure the Kaggle dataset is in the source_data/ folder.")
        return False
    return True
