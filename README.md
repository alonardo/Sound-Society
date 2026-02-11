# Rhymes and Reason

**What 65 Years of Lyrics Reveal**

An interactive dashboard that analyzes 65 years of Billboard Hot 100 lyrics (1959–2023) to uncover how American music reflects culture, emotion, and evolving language.

![Dashboard](https://img.shields.io/badge/status-live-brightgreen) ![Python](https://img.shields.io/badge/python-3.10+-blue) ![License](https://img.shields.io/badge/license-MIT-yellow)

## What It Does

Rhymes and Reason processes ~6,500 hit songs through an NLP pipeline and visualizes the results in a dark-themed, interactive dashboard with four views:

- **Explore** — Filter by genre, decade, or year. See top words, TF-IDF distinctive keywords, sentiment, and vocabulary richness per genre.
- **Trends** — Track sentiment, lexical diversity, and word count over time. Overlay historical events (Civil Rights, Watergate, 9/11, etc.) on the chart.
- **Summary** — Genre report cards with stats, distinctive words, and descriptions.
- **Home** — Project overview with methodology explainers and aggregate stats.

## Analysis Methods

| Method | What It Measures |
|---|---|
| **VADER Sentiment** | Emotional tone of lyrics (-1 negative to +1 positive) |
| **Lexical Diversity (TTR)** | Vocabulary richness — ratio of unique words to total words |
| **TF-IDF** | Words distinctive to each genre — common within, rare elsewhere |
| **Word Frequency** | Most-used words per genre/decade (stopwords removed) |

## Tech Stack

**Pipeline (Python)**
- NLTK (VADER sentiment analysis)
- scikit-learn (TF-IDF vectorization)
- Custom genre classifier based on artist/era heuristics
- Contamination detection (filters non-music text from dataset)

**Dashboard (Vanilla JS)**
- Chart.js with annotation plugin
- Space Grotesk + JetBrains Mono fonts
- Responsive dark theme with mobile hamburger nav
- No framework — pure HTML/CSS/JS

**Deployment**
- Vercel (static hosting)

## Getting Started

### Prerequisites

- Python 3.10+
- The Kaggle Billboard dataset (`source_data/all_songs_data.csv`)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline (fetch + analyze)
python run_pipeline.py

# Or run a quick test with 1990s data only
python run_pipeline.py --test

# Launch the dashboard locally
python run_pipeline.py --serve
```

The pipeline generates `data/processed/data.json` which the dashboard reads at runtime.

### Pipeline Options

```
python run_pipeline.py                     # Full pipeline (all years)
python run_pipeline.py --test              # Test run (1990s only)
python run_pipeline.py --years 1980-1989   # Specific year range
python run_pipeline.py --serve             # Launch local server
```

## Project Structure

```
├── dashboard/              # Frontend
│   ├── index.html          # Single-page app
│   ├── css/style.css       # Dark theme styles
│   ├── js/app.js           # Charts, filters, navigation
│   └── favicon.svg         # Vinyl record icon
├── data/
│   └── processed/          # Pipeline output
│       ├── data.json       # Main dashboard data
│       └── events.json     # Historical events overlay
├── source_data/            # Kaggle dataset (not committed)
├── utils/
│   ├── genre_classifier.py # Artist/era-based genre classification
│   └── nlp_helpers.py      # Tokenization, cleaning, TTR
├── analyze_pipeline.py     # NLP analysis (sentiment, TF-IDF, aggregations)
├── fetch_pipeline.py       # Data loading and preprocessing
├── config.py               # Paths and constants
├── run_pipeline.py         # Main entry point
├── serve.py                # Local dev server
├── requirements.txt        # Python dependencies
└── vercel.json             # Deployment config
```

## Data Source

[Billboard Year-End Hot 100 (1959–2023)](https://www.kaggle.com/) via Kaggle. The dataset includes song title, artist, year, chart rank, and lyrics.
