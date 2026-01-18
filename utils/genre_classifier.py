"""
Simple genre classifier based on artist names and era.
Uses known artists and heuristics to assign approximate genres.
"""

# Known artists by genre (sampling of major artists)
ARTIST_GENRES = {
    # Rock
    "rock": [
        "beatles", "rolling stones", "led zeppelin", "queen", "pink floyd",
        "eagles", "fleetwood mac", "aerosmith", "van halen", "bon jovi",
        "guns n' roses", "nirvana", "pearl jam", "green day", "foo fighters",
        "red hot chili peppers", "u2", "the who", "ac/dc", "def leppard",
        "journey", "foreigner", "heart", "pat benatar", "joan jett",
        "tom petty", "bruce springsteen", "john mellencamp", "bryan adams",
        "creedence clearwater", "santana", "chicago", "boston", "kansas",
        "styx", "reo speedwagon", "38 special", "poison", "whitesnake",
        "motley crue", "kiss", "alice cooper", "ozzy", "black sabbath"
    ],
    # Pop
    "pop": [
        "michael jackson", "madonna", "prince", "whitney houston", "mariah carey",
        "celine dion", "britney spears", "christina aguilera", "backstreet boys",
        "nsync", "spice girls", "taylor swift", "katy perry", "lady gaga",
        "ariana grande", "justin bieber", "bruno mars", "ed sheeran", "adele",
        "rihanna", "beyonce", "shakira", "jennifer lopez", "pink", "kelly clarkson",
        "dua lipa", "billie eilish", "olivia rodrigo", "the weeknd", "post malone",
        "elton john", "billy joel", "phil collins", "lionel richie", "george michael",
        "wham", "hall & oates", "duran duran", "culture club", "cyndi lauper",
        "paula abdul", "janet jackson", "new kids on the block", "debbie gibson"
    ],
    # R&B/Soul
    "rnb": [
        "stevie wonder", "aretha franklin", "marvin gaye", "al green", "james brown",
        "otis redding", "sam cooke", "ray charles", "diana ross", "supremes",
        "temptations", "four tops", "smokey robinson", "gladys knight", "earth wind",
        "kool & the gang", "commodores", "boyz ii men", "r. kelly", "usher",
        "alicia keys", "john legend", "chris brown", "ne-yo", "trey songz",
        "the weeknd", "frank ocean", "sza", "h.e.r.", "daniel caesar",
        "toni braxton", "brandy", "monica", "tlc", "destiny's child",
        "mary j. blige", "lauryn hill", "erykah badu", "d'angelo", "maxwell"
    ],
    # Hip-Hop/Rap
    "hiphop": [
        "eminem", "jay-z", "kanye west", "drake", "kendrick lamar", "j. cole",
        "lil wayne", "nicki minaj", "cardi b", "megan thee stallion", "travis scott",
        "post malone", "21 savage", "future", "migos", "lil baby", "dababy",
        "tupac", "notorious b.i.g.", "nas", "snoop dogg", "dr. dre", "ice cube",
        "ll cool j", "run dmc", "beastie boys", "public enemy", "n.w.a",
        "outkast", "ludacris", "t.i.", "50 cent", "ja rule", "nelly",
        "missy elliott", "lil kim", "foxy brown", "eve", "lauryn hill",
        "chance the rapper", "childish gambino", "tyler the creator", "a$ap rocky"
    ],
    # Country
    "country": [
        "johnny cash", "dolly parton", "willie nelson", "kenny rogers", "glen campbell",
        "john denver", "alabama", "garth brooks", "george strait", "reba mcentire",
        "shania twain", "tim mcgraw", "faith hill", "keith urban", "carrie underwood",
        "taylor swift", "luke bryan", "blake shelton", "jason aldean", "florida georgia line",
        "zac brown band", "lady antebellum", "little big town", "dan + shay",
        "conway twitty", "loretta lynn", "tammy wynette", "randy travis", "alan jackson",
        "brooks & dunn", "toby keith", "kenny chesney", "brad paisley", "dierks bentley",
        "eric church", "chris stapleton", "kane brown", "luke combs", "morgan wallen"
    ],
    # Dance/Electronic
    "dance": [
        "donna summer", "bee gees", "chic", "gloria gaynor", "village people",
        "depeche mode", "new order", "pet shop boys", "erasure", "technotronic",
        "c+c music factory", "snap", "la bouche", "real mccoy", "ace of base",
        "daft punk", "david guetta", "calvin harris", "deadmau5", "skrillex",
        "marshmello", "chainsmokers", "avicii", "tiesto", "zedd",
        "black eyed peas", "flo rida", "pitbull", "sean paul", "jason derulo",
        "usher", "chris brown", "ne-yo"
    ]
}

# Keywords in song titles that suggest genres
TITLE_KEYWORDS = {
    "rock": ["rock", "guitar", "metal", "punk"],
    "country": ["country", "cowboy", "truck", "beer", "whiskey", "farm", "texas", "nashville"],
    "hiphop": ["feat.", "featuring", "ft."],
    "dance": ["dance", "disco", "party", "club", "dj"],
    "rnb": ["love", "baby", "heart", "soul"]
}

# Era-based genre tendencies
ERA_GENRES = {
    (1959, 1963): ["pop", "rock", "rnb"],
    (1964, 1969): ["rock", "pop", "rnb"],
    (1970, 1979): ["rock", "disco", "rnb", "pop"],
    (1980, 1989): ["pop", "rock", "dance", "rnb"],
    (1990, 1999): ["pop", "hiphop", "rnb", "rock", "country"],
    (2000, 2009): ["pop", "hiphop", "rnb", "rock", "country"],
    (2010, 2019): ["pop", "hiphop", "dance", "country", "rnb"],
    (2020, 2029): ["pop", "hiphop", "rnb"]
}


def classify_genre(artist: str, title: str, year: int) -> str:
    """
    Classify a song's genre based on artist, title, and year.
    Returns one of: rock, pop, rnb, hiphop, country, dance, other
    """
    artist_lower = artist.lower() if artist else ""
    title_lower = title.lower() if title else ""

    # Check known artists first
    for genre, artists in ARTIST_GENRES.items():
        for known_artist in artists:
            if known_artist in artist_lower:
                return genre

    # Check title keywords
    for genre, keywords in TITLE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return genre

    # Default based on era
    for (start, end), genres in ERA_GENRES.items():
        if start <= year <= end:
            # Return most common genre for era
            return genres[0]

    return "pop"  # Default fallback


GENRE_LABELS = {
    "rock": "Rock",
    "pop": "Pop",
    "rnb": "R&B / Soul",
    "hiphop": "Hip-Hop / Rap",
    "country": "Country",
    "dance": "Dance / Electronic",
    "other": "Other"
}


def get_genre_label(genre_code: str) -> str:
    """Get display label for genre code."""
    return GENRE_LABELS.get(genre_code, "Other")
