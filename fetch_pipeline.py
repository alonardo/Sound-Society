"""
Data pipeline for loading Kaggle Billboard dataset.

Source: Kaggle Billboard Year-End Hot 100 (1959-2023) with lyrics
"""

import ast
import csv
import re
import sys
from datetime import datetime

from tqdm import tqdm

import config

# Increase CSV field size limit for large lyrics fields
csv.field_size_limit(sys.maxsize)


def extract_spotify_id(media_str: str) -> str | None:
    """
    Extract Spotify track ID from the Media column (for reference/linking).
    """
    if not media_str or media_str == "[]":
        return None

    try:
        media_list = ast.literal_eval(media_str)
        for item in media_list:
            if item.get("provider") == "spotify":
                uri = item.get("native_uri", "")
                if uri.startswith("spotify:track:"):
                    return uri.split(":")[-1]
                url = item.get("url", "")
                match = re.search(r"track/([a-zA-Z0-9]+)", url)
                if match:
                    return match.group(1)
    except (ValueError, SyntaxError):
        pass

    return None


def load_kaggle_data() -> list[dict]:
    """
    Load songs from Kaggle CSV.

    Returns:
        List of song dicts with basic info and lyrics
    """
    songs = []

    with open(config.KAGGLE_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            year = row.get("Year", "")
            try:
                year = int(float(year)) if year else None
            except ValueError:
                year = None

            if not year:
                continue

            rank = row.get("Rank", "")
            try:
                rank = int(rank) if rank else None
            except ValueError:
                rank = None

            song = {
                "id": f"{year}_{rank:03d}" if rank else f"{year}_000",
                "year": year,
                "rank": rank,
                "title": row.get("Song Title", "").strip(),
                "artist": row.get("Artist", "").strip(),
                "album": row.get("Album", "").strip(),
                "release_date": row.get("Release Date", "").strip(),
                "lyrics": row.get("Lyrics", "").strip(),
                "spotify_id": extract_spotify_id(row.get("Media", "")),
                "song_url": row.get("Song URL", "").strip(),
            }

            songs.append(song)

    return songs


def run_fetch_pipeline(start_year: int = None, end_year: int = None) -> list[dict]:
    """
    Run the data loading pipeline.

    Args:
        start_year: Filter start year (default: all)
        end_year: Filter end year (default: all)

    Returns:
        List of song dicts
    """
    print("Loading data pipeline")
    print("=" * 50)

    if not config.check_source_data():
        return []

    print(f"Loading data from {config.KAGGLE_CSV.name}...")
    songs = load_kaggle_data()
    print(f"Loaded {len(songs)} songs")

    # Filter by year
    start_year = start_year or config.START_YEAR
    end_year = end_year or config.END_YEAR

    songs = [s for s in songs if start_year <= s["year"] <= end_year]
    print(f"Filtered to {len(songs)} songs ({start_year}-{end_year})")

    songs_with_lyrics = sum(1 for s in songs if s.get("lyrics"))
    print(f"Songs with lyrics: {songs_with_lyrics}")

    songs_with_spotify = sum(1 for s in songs if s.get("spotify_id"))
    print(f"Songs with Spotify IDs: {songs_with_spotify} (for linking)")

    print("\n" + "=" * 50)
    print("Data loaded!")

    return songs


if __name__ == "__main__":
    songs = run_fetch_pipeline()
    if songs:
        print(f"\nSample: '{songs[0]['title']}' by {songs[0]['artist']} ({songs[0]['year']})")
