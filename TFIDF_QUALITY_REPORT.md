# TF-IDF Keyword Quality Analysis Report

## Executive Summary

This report analyzes the presence of non-semantic terms appearing as "distinctive" keywords in the TF-IDF analysis of the music lyrics dashboard. The investigation reveals several categories of problematic terms that are inflating TF-IDF scores without providing meaningful insights about genre characteristics.

## Problem Statement

The TF-IDF (Term Frequency-Inverse Document Frequency) analysis is surfacing terms like "ron", "gimme", "doo", "chh", "um", "ba", "dit", "ay" as highly distinctive keywords for various genres. These terms lack semantic meaning and distort the analysis of what makes each genre linguistically unique.

---

## Categories of Problematic Terms

### 1. Vocal Sounds / Onomatopoeia (Doo-Wop Style)

These are non-lexical vocables commonly found in doo-wop, early rock and roll, and pop music.

| Term | TF-IDF Score | Genre | Example Song |
|------|-------------|-------|--------------|
| doo | 0.2427 (pop), 0.2169 (rock), 0.1809 (dance) | Multiple | "Come Softly To Me" - Fleetwoods (1959) |
| dum | 0.3142 (pop 1950s), 0.0928 (pop) | Pop | "Come Softly To Me" - Fleetwoods |
| ba | 0.1506 (rock), 0.1913 (dance), 0.1162 (pop) | Multiple | "Lonely Teardrops" - Jackie Wilson |
| dooby | 0.1195 (pop 1950s) | Pop | "Come Softly To Me" - Fleetwoods |

**Example Context:**
"Come Softly To Me" by The Fleetwoods (1959) contains extensive doo-wop vocalizations:
- "Doo dooby doo, Dum dum, dum doo dum, dooby doo" repeated throughout

### 2. Percussive/Rhythmic Vocalizations

Sounds used to simulate percussion or rhythm in songs.

| Term | TF-IDF Score | Genre | Example Song |
|------|-------------|-------|--------------|
| chh | 0.2116 | Rock | "In The Summertime" - Mungo Jerry (1970) |
| boaw | 0.1655 | Hip-Hop | "Peaches & Eggplants" - Young Nudy ft. 21 Savage (2023) |

**Example Context:**
"In The Summertime" by Mungo Jerry features extensive rhythmic vocalizations:
- "Chh chh-chh, uh, Chh chh-chh, uh" used as a percussive chorus element

"Peaches & Eggplants" by Young Nudy uses "boaw" as an onomatopoeic sound repeated extensively throughout the track.

### 3. Filler Words / Interjections

Common verbal fillers and emotional interjections.

| Term | TF-IDF Score | Genre | Example Context |
|------|-------------|-------|-----------------|
| um | 0.1895 | Rock | General filler in lyrics |
| uh | 0.1151 (hip-hop 1950s) | Hip-Hop | Common verbal filler |
| eh | 0.1055 | Pop | General interjection |
| oh | 0.1352 (pop 1950s) | Pop | Emotional interjection |
| oo | 0.0866 | Pop | Vocalization |
| aa | 0.0805 | Pop | Vocalization |
| ay | 0.1476 | Rock | Interjection |
| ayy | 0.0834 (pop), 0.1592 (hip-hop) | Multiple | Hip-hop interjection |

### 4. Extended/Stylized Vocalizations

Modern song-specific stylized sounds.

| Term | TF-IDF Score | Genre | Example Song |
|------|-------------|-------|--------------|
| yuuuuuuu | 0.189 | R&B | "Crank That (Soulja Boy)" - Soulja Boy (2007) |
| thoia | 0.3703 | R&B | "Thoia Thoing" - R. Kelly (2003) |
| thoing | 0.1711 | R&B | "Thoia Thoing" - R. Kelly (2003) |
| yaka | 0.1634 | R&B | Various |

**Example Context:**
"Crank That (Soulja Boy)" contains "yuuuuuuu" repeated over 30 times as a signature catchphrase.
"Thoia Thoing" by R. Kelly uses the made-up words "thoia" and "thoing" as the main hook.

### 5. Informal Contractions

Colloquial speech patterns in lyrics.

| Term | TF-IDF Score | Genre | Example Context |
|------|-------------|-------|-----------------|
| gimme | 0.2219 (rock), 0.1034 (dance) | Rock/Dance | "Give me" contracted |
| gonna | Common | Multiple | "Going to" contracted |
| wanna | Common | Multiple | "Want to" contracted |
| gotta | Common | Multiple | "Got to" contracted |

### 6. Name Fragments / Artist Names

Parts of names appearing in lyrics or metadata leakage.

| Term | TF-IDF Score | Genre | Root Cause |
|------|-------------|-------|------------|
| ron | 0.2314 | Rock | Artist name "Ron Holden", "Ron Wilson" appearing in lyrics/metadata |
| braxton | 0.2069 | R&B | Toni Braxton references |
| wallen | 0.1298 | Country | Morgan Wallen references |
| cardi | 0.0679 | Hip-Hop | Cardi B references |
| jones | 0.0934 | Rock | Various "Jones" references |

**Example:**
"Love You So" by Ron Holden - the artist's name appears in search results/metadata.

### 7. Foreign Language Terms (Spanish/Portuguese)

Non-English terms from bilingual or international songs.

| Term | TF-IDF Score | Genre | Meaning |
|------|-------------|-------|---------|
| que | 0.2341 (pop), 0.1654 (dance), 0.1279 (hip-hop) | Multiple | Spanish "what/that" |
| te | 0.16 | Pop | Spanish "you" |
| mi | 0.0784 (pop), 0.1241 (dance) | Multiple | Spanish "my" |
| lo | 0.108 (pop), 0.1285 (rock) | Multiple | Spanish "the/it" |
| el | 0.0788 | Pop | Spanish "the" |
| en | 0.0837 | Pop | Spanish "in" |
| eu | 0.1146 | Hip-Hop | Portuguese "I" |
| di | 0.1422 | Dance | Italian/Spanish |
| je | 0.1078 | Dance | French "I" |

### 8. Repetitive Song Elements

Terms from songs with heavy repetition that dominate TF-IDF.

| Term | TF-IDF Score | Genre | Example Song |
|------|-------------|-------|--------------|
| hurdy | 0.0941 | Rock | "Hurdy Gurdy Man" - Donovan (1968) |
| gurdy | 0.1176 | Rock | "Hurdy Gurdy Man" - Donovan (1968) |
| mow | 0.1018 | Rock | "Surfin' Bird" - The Trashmen (likely) |
| hump | 0.3947 | Dance | "The Humpty Dance" - Digital Underground |
| choo | 0.0809 (pop), 0.1486 (pop 1990s) | Pop | Train-themed songs |

### 9. Metadata Contamination / Non-Lyrics Content

Terms from non-lyric content that leaked into the dataset.

| Term | TF-IDF Score | Genre | Source |
|------|-------------|-------|--------|
| chandler | 0.1124 | R&B | Friends TV show script contamination |
| rachel | 0.1167 | R&B | Friends TV show script contamination |
| monica | 0.09 | R&B | Friends TV show script contamination |
| feat | 0.1452 (R&B), 0.22 (country) | Multiple | "featuring" abbreviation from song titles |

**Critical Finding:**
A Friends TV show episode script ("The One With The Evil Orthodontist") appears in the dataset, misattributed as a song. This explains why TV character names appear as R&B keywords.

### 10. Slang Spellings / Phonetic Transcriptions

| Term | TF-IDF Score | Genre | Standard Form |
|------|-------------|-------|---------------|
| dat | 0.3783 (R&B 1950s) | R&B | "that" |
| wha | 0.1153 | Dance | "what" |
| wid | 0.1117 | Dance | "with" |
| inna | 0.1048 | Dance | "in the/in a" |
| gyal | 0.1467 | Dance | "girl" (Caribbean) |
| dutty | 0.0993 | Dance | "dirty" (Caribbean) |

### 11. Hip-Hop Slang/Variations

| Term | TF-IDF Score | Genre | Meaning |
|------|-------------|-------|---------|
| izz | 0.0668 | Hip-Hop | Snoop Dogg "-izz" language pattern |
| fuckin | 0.0989 | Hip-Hop | Informal spelling |
| poppin | 0.0684 | Hip-Hop | "popping" |
| chasin | 0.1484 | Country | "chasing" |
| truckin | 0.1474 | Country | "trucking" |

---

## Root Cause Analysis

### Why These Terms Score High in TF-IDF

1. **High Frequency in Specific Songs**: Terms like "doo", "chh", "thoia" appear dozens or hundreds of times in single songs, dramatically inflating their term frequency.

2. **Low Document Frequency**: These nonsense terms appear in relatively few songs across the corpus, giving them high inverse document frequency scores.

3. **Genre Clustering**: Certain genres (doo-wop, hip-hop) have stylistic conventions that use these vocalizations extensively.

4. **Data Contamination**: Non-music content (TV scripts, metadata) has leaked into the lyrics field.

5. **No Preprocessing Filter**: The TF-IDF calculation doesn't filter out:
   - Single/double letter "words"
   - Repeated syllables
   - Common vocal sounds
   - Non-English stopwords

---

## Recommended Solutions

### 1. Expanded Stopwords List

Add the following terms to the TF-IDF stopwords filter:

```python
# Vocal sounds and onomatopoeia
vocal_sounds = [
    'doo', 'dooby', 'dum', 'ba', 'la', 'na', 'da', 'sha', 'wa',
    'dee', 'dit', 'buh', 'mow', 'chh', 'uh', 'ah', 'eh', 'oh',
    'oo', 'aa', 'ee', 'ay', 'ayy', 'hey', 'ho', 'whoa', 'woah',
    'ooh', 'yeah', 'yah', 'ya', 'ye'
]

# Extended vocalizations (song-specific)
extended_vocals = [
    'yuuuuuuu', 'thoia', 'thoing', 'yaka', 'boaw', 'baow'
]

# Informal contractions
contractions = [
    'gimme', 'gonna', 'wanna', 'gotta', 'kinda', 'sorta',
    'lemme', 'coulda', 'woulda', 'shoulda', 'oughta'
]

# Filler words
fillers = [
    'um', 'uh', 'er', 'em', 'hmm', 'mm', 'mmm', 'huh'
]

# Foreign language stopwords (Spanish/Portuguese/French common)
foreign_stopwords = [
    'que', 'te', 'mi', 'lo', 'el', 'en', 'la', 'de', 'un', 'una',
    'es', 'por', 'con', 'se', 'tu', 'yo', 'eu', 'di', 'je', 'le'
]

# Metadata leakage
metadata_terms = [
    'feat', 'featuring', 'ft', 'remix', 'version', 'remaster',
    'live', 'acoustic', 'radio', 'edit'
]

# Dialect/slang spellings
slang_spellings = [
    'dat', 'wha', 'wid', 'inna', 'gyal', 'dutty', 'fuckin',
    'poppin', 'chasin', 'truckin', 'izz', 'izzle'
]
```

### 2. Minimum Word Length Filter

Implement a minimum word length of 3 characters to eliminate single/double letter "words" like:
- aa, ee, oo, oh, ah, uh, eh, ay, ba, da, la, na, wa, lo, mi, te, di, je

### 3. Data Cleaning - Remove Contaminated Entries

Identify and remove non-lyrics content:
- Friends TV show script (Song ID likely around line 3739)
- Any entries where lyrics contain scene directions like "[SCENE", "EXIT", "ENTER"

### 4. Repetition Dampening

Implement a maximum term frequency cap or logarithmic scaling to prevent single songs with excessive repetition from dominating the TF-IDF scores.

### 5. Name/Proper Noun Filter

Consider filtering or down-weighting proper nouns that appear to be:
- Artist names (braxton, wallen, cardi)
- Character names from contaminated data (chandler, rachel, monica)

---

## Complete List of Terms to Filter

### Priority 1: Immediate Removal (High Impact)

```
doo, dum, ba, la, na, da, chh, um, uh, ah, oh, ay, ayy,
gimme, gonna, wanna, gotta, que, te, mi, lo, el, en,
feat, thoia, thoing, yuuuuuuu, boaw, dooby
```

### Priority 2: Recommended Removal (Medium Impact)

```
sha, wa, dee, dit, buh, mow, eh, oo, aa, ee, ho, whoa,
woah, ooh, yeah, yah, ya, ye, wha, wid, inna, gyal,
dutty, izz, poppin, chasin, truckin, dat, fuckin,
lemme, kinda, sorta, di, je, eu, hurdy, gurdy
```

### Priority 3: Review for Removal (Low Impact / Context-Dependent)

```
choo, hump, mma, rockabye, ayer, yaka
```

---

## Data Quality Issues Identified

### 1. TV Show Script Contamination
- **File**: all_songs_data.csv, approximately line 3739
- **Content**: Friends Season 1 episode "The One With The Evil Orthodontist"
- **Impact**: Introduces "chandler", "rachel", "monica", "joey", "ross", "phoebe" as R&B keywords
- **Action**: Remove this entry entirely

### 2. Mashup/Cover Song Issues
- Some entries are mashups or covers that reference multiple songs
- Example: "Young Dumb & Broke / Bank Account / Bodak Yellow Mashup"
- **Impact**: Cross-contaminates genre characteristics

### 3. Metadata in Lyrics Field
- "feat" appearing with high TF-IDF suggests featuring artist info is in lyrics
- **Action**: Preprocess to remove "feat.", "featuring", "ft." patterns

---

## Conclusion

The TF-IDF analysis is being distorted by several categories of non-semantic content:

1. **Vocal sounds and onomatopoeia** (especially prevalent in 1950s-60s doo-wop)
2. **Extended stylized vocalizations** (modern hip-hop/R&B hooks)
3. **Foreign language stopwords** (Spanish terms from Latin music crossovers)
4. **Data contamination** (TV scripts, metadata leakage)
5. **Single/double letter fragments**

Implementing the recommended stopwords list and data cleaning procedures should significantly improve the quality of TF-IDF keyword extraction, surfacing genuinely distinctive thematic and linguistic characteristics of each genre rather than stylistic vocal artifacts.

---

*Report generated: 2026-01-18*
*Data source: C:\Users\aalon\Documents\Code\AntiGravity\Music\data\processed\data.json*
*Raw data: C:\Users\aalon\Documents\Code\AntiGravity\Music\source_data\all_songs_data.csv*
