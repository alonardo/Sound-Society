"""
NLP helper utilities for text cleaning, tokenization, and analysis.
"""

import re
import string
from collections import Counter


# Common English stopwords (extended list for lyrics analysis)
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
    "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from",
    "up", "down", "in", "out", "on", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "where", "why", "how",
    "all", "each", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "can", "will", "just", "should", "now", "i", "me", "my", "myself",
    "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
    "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
    "herself", "it", "its", "itself", "they", "them", "their", "theirs",
    "themselves", "what", "which", "who", "whom", "this", "that", "these",
    "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "would",
    "could", "ought", "im", "youre", "hes", "shes", "its", "were", "theyre",
    "ive", "youve", "weve", "theyve", "id", "youd", "hed", "shed", "wed",
    "theyd", "ill", "youll", "hell", "shell", "well", "theyll", "isnt",
    "arent", "wasnt", "werent", "hasnt", "havent", "hadnt", "doesnt",
    "dont", "didnt", "wont", "wouldnt", "shant", "shouldnt", "cant",
    "cannot", "couldnt", "mustnt", "lets", "thats", "whos", "whats",
    "heres", "theres", "whens", "wheres", "whys", "hows", "because",
    "as", "until", "while", "of", "both", "any", "ever",
    # Common lyrics fillers
    "oh", "yeah", "ooh", "ah", "uh", "hey", "la", "na", "da", "whoa",
    "yo", "mmm", "hmm", "ayy", "aye",
}


def clean_lyrics(text: str) -> str:
    """
    Clean lyrics text by removing annotations and normalizing.

    Args:
        text: Raw lyrics text

    Returns:
        Cleaned lyrics string
    """
    if not text:
        return ""

    # Remove Genius annotations like [Verse 1], [Chorus], etc.
    text = re.sub(r'\[.*?\]', '', text)

    # Remove parenthetical notes like (x2), (Repeat)
    text = re.sub(r'\(.*?\)', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove "Embed" and contributor notes often at end of Genius lyrics
    text = re.sub(r'\d*Embed$', '', text)
    text = re.sub(r'EmbedShare URLCopyEmbedCopy', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def tokenize(text: str, remove_stopwords: bool = True, lowercase: bool = True) -> list[str]:
    """
    Tokenize text into words.

    Args:
        text: Input text
        remove_stopwords: Whether to remove common stopwords
        lowercase: Whether to convert to lowercase

    Returns:
        List of word tokens
    """
    if not text:
        return []

    # Convert to lowercase if requested
    if lowercase:
        text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Split into words
    tokens = text.split()

    # Remove stopwords if requested
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]

    # Remove single characters and numbers
    tokens = [t for t in tokens if len(t) > 1 and not t.isdigit()]

    return tokens


def calculate_ttr(tokens: list[str]) -> float:
    """
    Calculate Type-Token Ratio (lexical diversity).

    TTR = number of unique words / total words

    Args:
        tokens: List of word tokens

    Returns:
        TTR value between 0 and 1, or 0 if no tokens
    """
    if not tokens:
        return 0.0

    unique_tokens = set(tokens)
    return len(unique_tokens) / len(tokens)


def get_word_frequencies(tokens: list[str], top_n: int = 50) -> list[tuple[str, int]]:
    """
    Get word frequencies from tokens.

    Args:
        tokens: List of word tokens
        top_n: Number of top words to return

    Returns:
        List of (word, count) tuples sorted by frequency
    """
    if not tokens:
        return []

    counter = Counter(tokens)
    return counter.most_common(top_n)


def normalize_for_comparison(text: str) -> str:
    """
    Normalize text for comparison purposes (e.g., title matching).

    Args:
        text: Input text

    Returns:
        Normalized string
    """
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove common prefixes/suffixes
    text = re.sub(r'^the\s+', '', text)
    text = re.sub(r'\s+remix$', '', text)
    text = re.sub(r'\s+remaster(ed)?$', '', text)
    text = re.sub(r'\s+version$', '', text)
    text = re.sub(r'\s+edit$', '', text)

    return text
