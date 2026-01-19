"""
NLP analysis pipeline for processing lyrics and generating insights.

Analyzes sentiment, lexical diversity, word frequencies by genre/decade.
Outputs data.json for the dashboard and lyrics files for interactive display.
"""

import json
from collections import defaultdict, Counter
from datetime import datetime

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

import config
from fetch_pipeline import run_fetch_pipeline
from utils.nlp_helpers import clean_lyrics, tokenize, calculate_ttr
from utils.genre_classifier import classify_genre, get_genre_label


def ensure_nltk_data():
    """Download required NLTK data."""
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        print("Downloading NLTK VADER lexicon...")
        nltk.download('vader_lexicon', quiet=True)


def analyze_sentiment(lyrics: str) -> dict | None:
    """Analyze sentiment using VADER."""
    if not lyrics:
        return None

    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(lyrics)

    return {
        "positive": round(scores["pos"], 3),
        "negative": round(scores["neg"], 3),
        "neutral": round(scores["neu"], 3),
        "compound": round(scores["compound"], 3),
    }


def calculate_lexical_diversity(lyrics: str) -> float | None:
    """Calculate lexical diversity (TTR) for lyrics."""
    if not lyrics:
        return None

    cleaned = clean_lyrics(lyrics)
    tokens = tokenize(cleaned, remove_stopwords=True)

    if len(tokens) < 10:
        return None

    return round(calculate_ttr(tokens), 3)


def compute_word_frequencies(songs: list[dict], group_by: str, top_n: int = 30) -> dict:
    """
    Compute word frequencies for each group.
    Returns dict with word counts for bar chart visualization.
    """
    groups = defaultdict(list)

    for song in songs:
        if not song.get("cleaned_lyrics"):
            continue

        tokens = tokenize(song["cleaned_lyrics"], remove_stopwords=True)

        if group_by == "genre":
            key = song.get("genre", "other")
        elif group_by == "decade":
            key = f"{(song['year'] // 10) * 10}s"
        else:
            key = str(song['year'])

        groups[key].extend(tokens)

    result = {}
    for group_name, all_tokens in groups.items():
        counter = Counter(all_tokens)
        # Get top words with counts
        top_words = counter.most_common(top_n)
        result[group_name] = [{"word": word, "count": count} for word, count in top_words]

    return result


def compute_genre_decade_frequencies(songs: list[dict], top_n: int = 25) -> dict:
    """
    Compute word frequencies by genre AND decade combination.
    """
    groups = defaultdict(list)

    for song in songs:
        if not song.get("cleaned_lyrics"):
            continue

        tokens = tokenize(song["cleaned_lyrics"], remove_stopwords=True)
        genre = song.get("genre", "other")
        decade = f"{(song['year'] // 10) * 10}s"
        key = f"{genre}_{decade}"

        groups[key].extend(tokens)

    result = {}
    for group_name, all_tokens in groups.items():
        if len(all_tokens) < 50:  # Skip small groups
            continue
        counter = Counter(all_tokens)
        top_words = counter.most_common(top_n)
        result[group_name] = [{"word": word, "count": count} for word, count in top_words]

    return result


def is_contaminated_lyrics(lyrics: str) -> bool:
    """
    Check if lyrics appear to be contaminated with non-music text.
    The Kaggle dataset has some entries with Proust, Joyce, Arabian Nights text
    instead of actual song lyrics.

    Detection methods:
    1. Word count - real songs rarely exceed 2000 words; contaminated entries
       average 17,000 words (some have 149,000+ - entire books)
    2. Literary text markers - specific character/place names from known sources
    """
    if not lyrics:
        return False

    # Word count filter - most effective
    # Real songs: avg 229 words, max ~2000 for very long songs
    # Contaminated: avg 17,000 words, some 100,000+
    word_count = len(lyrics.split())
    if word_count > 2500:
        return True

    lyrics_lower = lyrics.lower()

    # Literary text markers for smaller contaminated entries
    contamination_markers = [
        'guermantes', 'villeparisis', 'swann', 'charlus',  # Proust
        'dedalus', 'bloom', 'mulligan', 'conmee',  # Joyce Ulysses
        'sharrkan', 'shahrazad', 'scheherazade', 'al-nu',  # 1001 Nights
        'thou art', 'dost thou', 'hath been', 'wherefore art',  # Archaic
        # TV show scripts
        '[scene', '[enter', '[exit', 'fade in:', 'fade out:',  # Stage directions
        'chandler:', 'rachel:', 'monica:', 'joey:', 'ross:', 'phoebe:',  # Friends
    ]

    return any(marker in lyrics_lower for marker in contamination_markers)


# Custom stopwords for music lyrics TF-IDF
MUSIC_STOPWORDS = {
    # Vocal sounds and onomatopoeia (doo-wop style)
    'doo', 'dooby', 'dum', 'ba', 'la', 'na', 'da', 'sha', 'wa',
    'dee', 'dit', 'buh', 'mow', 'ra', 'ta', 'pa', 'ma', 'fa',

    # Percussive/rhythmic vocalizations
    'chh', 'uh', 'ah', 'eh', 'oh', 'oo', 'aa', 'ee', 'ay', 'ayy',
    'hey', 'ho', 'whoa', 'woah', 'ooh', 'yeah', 'yah', 'ya', 'ye',
    'huh', 'hmm', 'mm', 'mmm', 'um', 'er', 'em',

    # Extended stylized vocalizations
    'yuuuuuuu', 'thoia', 'thoing', 'yaka', 'boaw', 'baow',

    # Informal contractions
    'gimme', 'gonna', 'wanna', 'gotta', 'kinda', 'sorta',
    'lemme', 'coulda', 'woulda', 'shoulda', 'oughta', 'aint',
    'cant', 'dont', 'wont', 'didnt', 'doesnt', 'isnt', 'wasnt',

    # Foreign language stopwords (Spanish/Portuguese/French common)
    'que', 'te', 'mi', 'lo', 'el', 'en', 'la', 'de', 'un', 'una',
    'es', 'por', 'con', 'se', 'tu', 'yo', 'eu', 'di', 'je', 'le',
    'si', 'su', 'nos', 'mas', 'pero', 'como', 'para', 'esta',

    # Metadata leakage
    'feat', 'featuring', 'ft', 'remix', 'version', 'remaster',
    'remastered', 'live', 'acoustic', 'radio', 'edit',

    # Dialect/slang spellings
    'dat', 'wha', 'wid', 'inna', 'gyal', 'dutty', 'fuckin',
    'poppin', 'chasin', 'truckin', 'izz', 'izzle', 'nah',

    # Common filler/nonsense repeated in songs
    'na', 'sha', 'bop', 'shoop', 'dang', 'ding', 'dong',
    'tra', 'laa', 'ooo', 'aah', 'ohh', 'ahh', 'uuh',

    # Very common words that don't distinguish genres
    'got', 'get', 'let', 'come', 'go', 'know', 'see', 'say',
    'make', 'take', 'give', 'tell', 'want', 'need', 'feel',
    'think', 'look', 'way', 'day', 'time', 'life', 'world',
    'man', 'girl', 'boy', 'baby', 'cause', 'cuz', 'cos',
    'like', 'just', 'now', 'back', 'still', 'right', 'good',
}


def compute_tfidf_by_genre(songs: list[dict], top_n: int = 20) -> dict:
    """
    Compute TF-IDF where each genre is treated as a single document.
    This finds words that are distinctive to each genre - common within
    the genre but rare in other genres.

    Returns dict mapping genre to list of distinctive keywords with scores.
    """
    # Build one document per genre (concatenate all lyrics)
    # Filter out contaminated lyrics (literary text from bad scraping)
    genre_documents = defaultdict(list)

    for song in songs:
        if not song.get("cleaned_lyrics"):
            continue
        if is_contaminated_lyrics(song.get("cleaned_lyrics", "")):
            continue  # Skip contaminated entries
        genre = song.get("genre", "other")
        genre_documents[genre].append(song["cleaned_lyrics"])

    if not genre_documents:
        return {}

    # Join all lyrics for each genre into single documents
    genres = list(genre_documents.keys())
    documents = [" ".join(genre_documents[g]) for g in genres]

    # Combine English stopwords with music-specific stopwords
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    combined_stopwords = list(ENGLISH_STOP_WORDS | MUSIC_STOPWORDS)

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words=combined_stopwords,
        ngram_range=(1, 1),
        min_df=1,  # Allow words unique to one genre (that's what we want!)
        max_df=0.90,  # Ignore terms in >90% of documents (too common)
        token_pattern=r'\b[a-zA-Z]{3,}\b'  # Only words with 3+ letters
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
    except ValueError:
        return {}

    result = {}
    for idx, genre in enumerate(genres):
        # Get TF-IDF scores for this genre
        scores = tfidf_matrix[idx].toarray().flatten()

        # Get top words by TF-IDF score, filtering out remaining noise
        top_indices = scores.argsort()[-top_n * 2:][::-1]  # Get extra to filter
        top_words = []
        for i in top_indices:
            if scores[i] > 0 and len(top_words) < top_n:
                word = feature_names[i]
                # Skip words that are all the same letter repeated
                if len(set(word)) > 1:
                    top_words.append({"word": word, "score": round(scores[i], 4)})

        result[genre] = top_words

    return result


def compute_tfidf_by_genre_decade(songs: list[dict], top_n: int = 15) -> dict:
    """
    Compute TF-IDF for each genre within each decade.
    Returns dict mapping "genre_decade" keys to list of distinctive keywords.
    """
    # Build documents per genre+decade combination
    genre_decade_documents = defaultdict(list)

    for song in songs:
        if not song.get("cleaned_lyrics"):
            continue
        if is_contaminated_lyrics(song.get("cleaned_lyrics", "")):
            continue
        genre = song.get("genre", "other")
        year = song.get("year", 0)
        decade = f"{(year // 10) * 10}s"
        key = f"{genre}_{decade}"
        genre_decade_documents[key].append(song["cleaned_lyrics"])

    if not genre_decade_documents:
        return {}

    # For each decade, compute TF-IDF across genres within that decade
    # Group by decade
    decades = set()
    for key in genre_decade_documents.keys():
        decade = key.split("_")[1]
        decades.add(decade)

    result = {}

    for decade in decades:
        # Get all genre+decade keys for this decade
        decade_keys = [k for k in genre_decade_documents.keys() if k.endswith(f"_{decade}")]

        if len(decade_keys) < 2:
            # Need at least 2 genres to compute meaningful TF-IDF
            continue

        genres_in_decade = [k.split("_")[0] for k in decade_keys]
        documents = [" ".join(genre_decade_documents[k]) for k in decade_keys]

        # Combine English stopwords with music-specific stopwords
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        combined_stopwords = list(ENGLISH_STOP_WORDS | MUSIC_STOPWORDS)

        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=3000,
            stop_words=combined_stopwords,
            ngram_range=(1, 1),
            min_df=1,
            max_df=0.90,
            token_pattern=r'\b[a-zA-Z]{3,}\b'  # Only words with 3+ letters
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
            feature_names = vectorizer.get_feature_names_out()
        except ValueError:
            continue

        for idx, genre in enumerate(genres_in_decade):
            scores = tfidf_matrix[idx].toarray().flatten()
            top_indices = scores.argsort()[-top_n * 2:][::-1]
            top_words = []
            for i in top_indices:
                if scores[i] > 0 and len(top_words) < top_n:
                    word = feature_names[i]
                    # Skip words that are all the same letter repeated
                    if len(set(word)) > 1:
                        top_words.append({"word": word, "score": round(scores[i], 4)})
            key = f"{genre}_{decade}"
            result[key] = top_words

    return result


def compute_aggregations(songs: list[dict]) -> dict:
    """Compute aggregated statistics by year, decade, and genre."""
    by_year = defaultdict(lambda: {
        "count": 0, "lyrics_available": 0,
        "avg_sentiment": [], "avg_lexical_diversity": [],
        "avg_word_count": [], "genres": defaultdict(int)
    })

    by_decade = defaultdict(lambda: {
        "count": 0, "lyrics_available": 0,
        "avg_sentiment": [], "avg_lexical_diversity": [],
        "avg_word_count": [], "genres": defaultdict(int)
    })

    by_genre = defaultdict(lambda: {
        "count": 0, "lyrics_available": 0,
        "avg_sentiment": [], "avg_lexical_diversity": [],
        "avg_word_count": [], "years": [], "decades": defaultdict(int)
    })

    for song in songs:
        year = song["year"]
        decade = f"{(year // 10) * 10}s"
        genre = song.get("genre", "other")

        # By year
        by_year[year]["count"] += 1
        by_year[year]["genres"][genre] += 1
        if song.get("lyrics"):
            by_year[year]["lyrics_available"] += 1
        if song.get("sentiment"):
            by_year[year]["avg_sentiment"].append(song["sentiment"]["compound"])
        if song.get("lexical_diversity"):
            by_year[year]["avg_lexical_diversity"].append(song["lexical_diversity"])
        if song.get("word_count"):
            by_year[year]["avg_word_count"].append(song["word_count"])

        # By decade
        by_decade[decade]["count"] += 1
        by_decade[decade]["genres"][genre] += 1
        if song.get("lyrics"):
            by_decade[decade]["lyrics_available"] += 1
        if song.get("sentiment"):
            by_decade[decade]["avg_sentiment"].append(song["sentiment"]["compound"])
        if song.get("lexical_diversity"):
            by_decade[decade]["avg_lexical_diversity"].append(song["lexical_diversity"])
        if song.get("word_count"):
            by_decade[decade]["avg_word_count"].append(song["word_count"])

        # By genre
        by_genre[genre]["count"] += 1
        by_genre[genre]["decades"][decade] += 1
        by_genre[genre]["years"].append(year)
        if song.get("lyrics"):
            by_genre[genre]["lyrics_available"] += 1
        if song.get("sentiment"):
            by_genre[genre]["avg_sentiment"].append(song["sentiment"]["compound"])
        if song.get("lexical_diversity"):
            by_genre[genre]["avg_lexical_diversity"].append(song["lexical_diversity"])
        if song.get("word_count"):
            by_genre[genre]["avg_word_count"].append(song["word_count"])

    def avg(lst):
        return round(sum(lst) / len(lst), 3) if lst else None

    result_by_year = {}
    for year, data in sorted(by_year.items()):
        result_by_year[year] = {
            "count": data["count"],
            "lyrics_available": data["lyrics_available"],
            "avg_sentiment": avg(data["avg_sentiment"]),
            "avg_lexical_diversity": avg(data["avg_lexical_diversity"]),
            "avg_word_count": avg(data["avg_word_count"]),
            "genres": dict(data["genres"])
        }

    result_by_decade = {}
    for decade, data in sorted(by_decade.items()):
        result_by_decade[decade] = {
            "count": data["count"],
            "lyrics_available": data["lyrics_available"],
            "avg_sentiment": avg(data["avg_sentiment"]),
            "avg_lexical_diversity": avg(data["avg_lexical_diversity"]),
            "avg_word_count": avg(data["avg_word_count"]),
            "genres": dict(data["genres"])
        }

    result_by_genre = {}
    for genre, data in by_genre.items():
        result_by_genre[genre] = {
            "label": get_genre_label(genre),
            "count": data["count"],
            "lyrics_available": data["lyrics_available"],
            "avg_sentiment": avg(data["avg_sentiment"]),
            "avg_lexical_diversity": avg(data["avg_lexical_diversity"]),
            "avg_word_count": avg(data["avg_word_count"]),
            "decades": dict(data["decades"]),
            "year_range": [min(data["years"]), max(data["years"])] if data["years"] else None
        }

    return {
        "by_year": result_by_year,
        "by_decade": result_by_decade,
        "by_genre": result_by_genre
    }


def save_lyrics_files(songs: list[dict]) -> None:
    """Save lyrics to lazy-loaded files by decade, year, and genre."""
    by_decade = defaultdict(dict)
    by_year = defaultdict(dict)
    by_genre = defaultdict(dict)

    for song in songs:
        if not song.get("lyrics") or song.get("contaminated"):
            continue

        song_id = song["id"]
        lyrics_entry = {
            "title": song["title"],
            "artist": song["artist"],
            "year": song["year"],
            "rank": song["rank"],
            "genre": song.get("genre", "other"),
            "genre_label": get_genre_label(song.get("genre", "other")),
            "lyrics": song["lyrics"],
        }

        decade = f"{(song['year'] // 10) * 10}s"
        genre = song.get("genre", "other")

        by_decade[decade][song_id] = lyrics_entry
        by_year[song["year"]][song_id] = lyrics_entry
        by_genre[genre][song_id] = lyrics_entry

    lyrics_dir = config.LYRICS_DIR

    # Ensure genre directory exists
    (lyrics_dir / "by_genre").mkdir(parents=True, exist_ok=True)

    print(f"  Saving lyrics by decade ({len(by_decade)} files)...")
    for decade, data in by_decade.items():
        filepath = lyrics_dir / "by_decade" / f"{decade}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Saving lyrics by year ({len(by_year)} files)...")
    for year, data in by_year.items():
        filepath = lyrics_dir / "by_year" / f"{year}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Saving lyrics by genre ({len(by_genre)} files)...")
    for genre, data in by_genre.items():
        filepath = lyrics_dir / "by_genre" / f"{genre}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def run_analysis_pipeline(songs: list[dict] = None) -> None:
    """Run the full analysis pipeline."""
    print("Starting analysis pipeline")
    print("=" * 50)

    ensure_nltk_data()

    if songs is None:
        songs = run_fetch_pipeline()

    if not songs:
        print("No songs to analyze.")
        return

    print(f"\nClassifying genres and analyzing {len(songs)} songs...")

    songs_with_lyrics = 0
    genre_counts = defaultdict(int)

    contaminated_count = 0
    for song in tqdm(songs, desc="Processing", unit="song"):
        # Classify genre
        song["genre"] = classify_genre(song["artist"], song["title"], song["year"])
        genre_counts[song["genre"]] += 1

        if song.get("lyrics"):
            # Check for contaminated lyrics (non-music content)
            if is_contaminated_lyrics(song["lyrics"]):
                song["contaminated"] = True
                song["cleaned_lyrics"] = None
                song["sentiment"] = None
                song["lexical_diversity"] = None
                song["word_count"] = 0
                contaminated_count += 1
                continue

            songs_with_lyrics += 1

            cleaned = clean_lyrics(song["lyrics"])
            song["cleaned_lyrics"] = cleaned
            song["contaminated"] = False

            song["sentiment"] = analyze_sentiment(cleaned)
            song["lexical_diversity"] = calculate_lexical_diversity(song["lyrics"])

            tokens = tokenize(cleaned, remove_stopwords=False)
            song["word_count"] = len(tokens)
        else:
            song["cleaned_lyrics"] = None
            song["sentiment"] = None
            song["lexical_diversity"] = None
            song["word_count"] = 0
            song["contaminated"] = False

    print(f"\nFiltered {contaminated_count} songs with contaminated lyrics (non-music content)")

    print("\nGenre distribution:")
    for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
        print(f"  {get_genre_label(genre)}: {count}")

    # Compute word frequencies
    print("\nComputing word frequencies...")
    word_freq_by_genre = compute_word_frequencies(songs, "genre")
    word_freq_by_decade = compute_word_frequencies(songs, "decade")
    word_freq_by_genre_decade = compute_genre_decade_frequencies(songs)

    # Compute TF-IDF (genre-level)
    print("Computing TF-IDF keywords by genre...")
    tfidf_by_genre = compute_tfidf_by_genre(songs)

    print("Computing TF-IDF keywords by genre+decade...")
    tfidf_by_genre_decade = compute_tfidf_by_genre_decade(songs)

    # Compute aggregations
    print("Computing aggregations...")
    aggregations = compute_aggregations(songs)

    # Prepare songs for output (exclude full lyrics)
    output_songs = []
    for song in songs:
        output_song = {k: v for k, v in song.items()
                       if k not in ["lyrics", "cleaned_lyrics"]}
        output_song["lyrics_available"] = bool(song.get("lyrics"))
        output_song["genre_label"] = get_genre_label(song.get("genre", "other"))
        output_songs.append(output_song)

    # Build final data.json
    years = [s["year"] for s in songs]
    output_data = {
        "songs": output_songs,
        "aggregations": aggregations,
        "word_frequencies": {
            "by_genre": word_freq_by_genre,
            "by_decade": word_freq_by_decade,
            "by_genre_decade": word_freq_by_genre_decade
        },
        "tfidf": {
            "by_genre": tfidf_by_genre,
            "by_genre_decade": tfidf_by_genre_decade
        },
        "metadata": {
            "total_songs": len(songs),
            "songs_with_lyrics": songs_with_lyrics,
            "years_covered": [min(years), max(years)] if years else [],
            "genres": list(genre_counts.keys()),
            "generated_at": datetime.now().isoformat(),
            "source": "Kaggle Billboard Year-End Hot 100 (1959-2023)",
        }
    }

    # Save outputs
    print(f"\nSaving {config.DATA_JSON}...")
    with open(config.DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("Saving lyrics files...")
    save_lyrics_files(songs)

    print("\n" + "=" * 50)
    print("Analysis complete!")
    print(f"  Total songs: {len(songs)}")
    print(f"  Songs with lyrics: {songs_with_lyrics}")
    print(f"  Genres: {len(genre_counts)}")
    print(f"  Output: {config.DATA_JSON}")
    print(f"  Lyrics: {config.LYRICS_DIR}")


if __name__ == "__main__":
    run_analysis_pipeline()
