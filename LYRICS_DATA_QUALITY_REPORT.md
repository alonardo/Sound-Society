# Lyrics Data Quality Analysis Report

## Summary

Investigation into anomalous TF-IDF keywords ("mme", "guermantes", "villeparisis") revealed **data contamination** in the Kaggle Billboard dataset. Approximately **1.3% of songs** (80 out of 6,384) have lyrics that are not actual song lyrics but excerpts from literary works.

## The Problem

When analyzing TF-IDF keywords for the "Pop" genre, unusual words appeared:
- **mme** - French for "Madame"
- **guermantes** - A character/location from Marcel Proust's novels
- **villeparisis** - Another Proust character (Marquise de Villeparisis)

These words have nothing to do with pop music.

## Root Cause

The Kaggle dataset contains **mismatched or corrupted lyrics data**. Instead of actual song lyrics, some entries contain:

### 1. Marcel Proust's "In Search of Lost Time"
- Characters: Swann, Guermantes, Villeparisis
- French honorifics: Mme., M.

### 2. James Joyce's "Ulysses"
- Characters: Bloom, Dedalus, Mulligan, Conmee, Molly
- Dublin locations and Irish references

### 3. "One Thousand and One Nights" (Arabian Nights)
- Characters: Sharrkan, Shahrazad, King Omar bin al-Nu'uman
- Arabic/Middle Eastern narrative style

### 4. Other Mismatched Content
- Modern rap lyrics appearing in 1950s songs
- Archaic English text

## Examples of Contaminated Entries

| Song Title | Artist | Year | Actual Content |
|------------|--------|------|----------------|
| 16 Candles | Crests | 1959 | Arabian Nights text |
| Lavender Blue | Sammy Turner | 1959 | Joyce's Ulysses |
| The All American Boy | Bill Parsons | 1959 | Joyce's Ulysses |
| Tell Him No | Travis and Bob | 1959 | Modern rap lyrics |

## Contamination Statistics

**Overall:** 80 contaminated songs out of 6,384 (1.3%)

### By Decade
| Decade | Contaminated Songs |
|--------|-------------------|
| 1950s  | 5 |
| 1960s  | 18 |
| 1970s  | 11 |
| 1980s  | 7 |
| 1990s  | 11 |
| 2000s  | 3 |
| 2010s  | 20 |
| 2020s  | 5 |

### By Genre
| Genre | Contaminated Songs |
|-------|-------------------|
| Pop | 36 |
| Rock | 19 |
| Hip-Hop | 14 |
| R&B | 9 |
| Country | 1 |
| Dance | 1 |

## Impact on Analysis

1. **TF-IDF Results**: Literary vocabulary incorrectly identified as "distinctive" to certain genres
2. **Sentiment Analysis**: Literary passages have different emotional profiles than song lyrics
3. **Word Frequencies**: Contaminated words inflate frequency counts
4. **Lexical Diversity**: Literary text typically has higher vocabulary diversity than song lyrics

## Likely Source of Contamination

This appears to be a **web scraping error** in the original dataset creation:
- Lyrics websites sometimes display placeholder or error content
- OCR errors from scanned sources
- Database join errors matching wrong content to songs
- Possible A/B testing content from lyrics websites

The presence of classic public domain literature (Proust, Joyce, Arabian Nights) suggests these texts may have been used as placeholder content on some lyrics websites, which was then scraped without validation.

## Detection Method

The most effective detection method is **word count**:

| Metric | Real Songs | Contaminated |
|--------|-----------|--------------|
| Average word count | 229 | 16,963 |
| Max word count | ~4,000 | 149,170 |
| Words per line | 5-10 | 17,000+ (single line) |

**Filter implemented:** Songs with >5,000 words are automatically flagged as contaminated.

Secondary detection uses literary character/place name markers:
- Proust: guermantes, villeparisis, swann, charlus
- Joyce: dedalus, bloom, mulligan, conmee
- Arabian Nights: sharrkan, shahrazad, scheherazade

## Implementation

The `analyze_pipeline.py` now:
1. Checks each song with `is_contaminated_lyrics()`
2. Marks contaminated songs with `"contaminated": true`
3. Excludes them from:
   - Sentiment analysis
   - Lexical diversity calculations
   - Word frequency counts
   - TF-IDF computation
   - Lyrics file output

## Conclusion

While the contamination rate is relatively low (1.3%), it has an outsized impact on TF-IDF analysis because the literary vocabulary is highly distinctive. The analysis methodology is sound; the issue lies in the source data quality from the Kaggle dataset.

For the most accurate results, consider filtering out songs from decades with higher contamination rates (1960s, 2010s) or implementing a contamination detection filter before analysis.

---
*Report generated during dashboard development*
*Investigation triggered by anomalous TF-IDF keywords in Pop genre*
