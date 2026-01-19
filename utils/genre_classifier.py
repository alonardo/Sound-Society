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
        "tupac", "2pac", "notorious b.i.g.", "biggie", "nas", "snoop dogg", "dr. dre", "ice cube",
        "ll cool j", "run dmc", "beastie boys", "public enemy", "n.w.a",
        "outkast", "ludacris", "t.i.", "50 cent", "ja rule", "nelly",
        "missy elliott", "missy misdemeanor elliott", "lil kim", "foxy brown", "eve", "lauryn hill",
        "chance the rapper", "childish gambino", "tyler the creator", "a$ap rocky",
        # Additional hip-hop artists
        "tag team", "paperboy", "kriss kross", "kris kross", "mc hammer", "vanilla ice",
        "coolio", "warren g", "bone thugs", "wu-tang", "method man", "redman",
        "dmx", "juvenile", "master p", "no limit", "cash money", "hot boys",
        "ying yang twins", "lil jon", "young jeezy", "gucci mane", "waka flocka",
        "rick ross", "meek mill", "french montana", "2 chainz", "big sean",
        "kid cudi", "mac miller", "wiz khalifa", "juicy j", "three 6 mafia",
        "soulja boy", "young thug", "lil uzi", "playboi carti", "roddy ricch",
        "pop smoke", "juice wrld", "xxxtentacion", "lil peep", "6ix9ine",
        "doja cat", "saweetie", "city girls", "glorilla", "ice spice",
        "digital underground", "de la soul", "a tribe called quest", "jungle brothers",
        "salt-n-pepa", "queen latifah", "mc lyte", "yo-yo",
        "cypress hill", "house of pain", "arrested development", "fugees",
        # Additional artists from misclassified songs
        "busta rhymes", "p. diddy", "puff daddy", "diddy", "pharrell",
        "jt money", "terror squad", "fat joe", "mystikal", "nivea",
        "lord tariq", "peter gunz", "n.o.r.e.", "nore", "rich homie quan",
        "sheck wes", "trick daddy", "mr. cheeks", "dem franchize boyz",
        "nle choppa", "moneybagg yo", "yfn lucci", "pnb rock",
        "kodak black", "desiigner", "offset", "metro boomin", "rae sremmurd",
        "junior mafia", "junior m.a.f.i.a.", "xscape", "tara kemp",
        "shalamar", "naughty by nature", "bell biv devoe", "bbd",
        "mo thugs", "bone thugs-n-harmony", "cash money millionaires",
        "lil scrappy", "lil flip", "lil boosie", "boosie", "webbie",
        "plies", "ace hood", "dj khaled", "pitbull", "flo rida",
        "sean kingston", "akon", "t-pain", "kevin gates", "yo gotti",
        "young dolph", "key glock", "pooh shiesty", "lil durk", "king von",
        "polo g", "lil tjay", "fivio foreign", "a boogie wit da hoodie",
        "gunna", "don toliver", "jack harlow", "central cee", "lil nas x",
        "megan", "meg thee stallion", "mulatto", "latto", "flo milli",
        # More missing artists from data
        "jadakiss", "d.r.a.m.", "dram", "lil yachty", "big pun", "big punisher",
        "trillville", "yung joc", "ray j", "yung berg", "da brat",
        "mims", "rich boy", "the-dream", "the dream", "fabolous",
        "ynw melly", "brs kash", "rod wave", "calboy",
        "jermaine dupri", "bow wow", "lil bow wow", "da brat",
        "e-40", "too short", "too $hort", "mac dre", "mistah fab",
        "g-eazy", "tyga", "yg", "dj mustard", "problem",
        "iggy azalea", "rae sremmurd", "slim jxmmi", "swae lee",
        "quavo", "takeoff", "huncho", "quality control",
        "lil mosey", "blueface", "comethazine", "smokepurpp",
        "ski mask", "denzel curry", "joey badass", "capital steez",
        "flatbush zombies", "beast coast", "pro era",
        "action bronson", "riff raff", "lil dicky", "logic", "joyner lucas",
        "hopsin", "tech n9ne", "strange music", "twista", "do or die",
        "crucial conflict", "psychodrama", "bump j", "common",
        "lupe fiasco", "rhymefest", "kanye", "jeremih", "r kelly",
        "king louie", "chief keef", "lil reese", "fredo santana",
        "sd", "ballout", "tadoe", "capo", "glo gang",
        "g herbo", "lil bibby", "young pappy", "fbg duck",
        # More missing from pop misclassification
        "tq", "kaliii", "scarface", "lloyd banks", "o.t. genasis", "ot genasis",
        "tory lanez", "rich the kid", "david banner", "cali swag district",
        "bryson tiller", "amine", "ahmad", "case", "mase", "lox", "the lox",
        "sheek louch", "styles p", "jadakiss", "g-unit", "lloyd banks", "tony yayo",
        "young buck", "obie trice", "stat quo", "cashis", "bobby creekwater",
        "sisqo", "dru hill", "ginuwine", "tank", "tyrese", "johnny gill",
        "keith sweat", "joe", "carl thomas", "donell jones", "montel jordan",
        "montell jordan", "blackstreet", "next", "112", "jagged edge", "silk",
        "h-town", "intro", "shai", "az yet", "all-4-one", "color me badd",
        "jodeci", "k-ci", "jojo", "devante swing", "mr dalvin",
        # Southern hip-hop
        "scarface", "geto boys", "ugk", "bun b", "pimp c", "chamillionaire",
        "paul wall", "slim thug", "mike jones", "lil keke", "z-ro", "trae",
        "trae tha truth", "devin the dude", "big moe", "dj screw", "swishahouse",
        "8ball", "mjg", "8ball & mjg", "project pat", "la chat", "gangsta boo",
        "tear da club up thugs", "hypnotize minds", "pastor troy", "lil scrappy",
        # More missing artists
        "fetty wap", "monty", "young gunz", "jidenna", "roman gianarthur",
        "adina howard", "total", "blackstreet", "guy", "teddy riley",
        "tony toni tone", "babyface", "bobby brown", "new edition", "bel biv devoe"
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
    "rock": ["rock", "guitar", "metal", "punk", "grunge"],
    "country": ["country", "cowboy", "truck", "beer", "whiskey", "farm", "texas", "nashville"],
    "hiphop": [],  # Removed - "feat." is too common in all genres now
    "dance": ["dance", "disco", "club", "dj", "remix"],
    "rnb": []  # Removed - "love", "baby", "heart" are too common across all genres
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


def normalize_name(name: str) -> str:
    """
    Normalize artist name for matching.
    Removes special characters and normalizes spacing.
    """
    import re
    if not name:
        return ""
    # Convert to lowercase
    name = name.lower()
    # Remove quotes
    name = name.replace('"', '').replace("'", "")
    # Replace hyphens with spaces
    name = name.replace('-', ' ')
    # Remove periods but keep spaces (for "T.I." -> "ti")
    name = re.sub(r'\.', '', name)
    # Normalize multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def classify_genre(artist: str, title: str, year: int) -> str:
    """
    Classify a song's genre based on artist, title, and year.
    Returns one of: rock, pop, rnb, hiphop, country, dance, other
    """
    import re

    artist_lower = artist.lower() if artist else ""
    artist_normalized = normalize_name(artist)
    title_lower = title.lower() if title else ""

    # Extract primary artist (before "feat", "featuring", "ft", "&", "and", "with")
    # to prioritize matching the main artist over featured artists
    primary_artist = artist_normalized
    for sep in [' feat ', ' featuring ', ' ft ', ' & ', ' and ', ' with ', ' x ']:
        if sep in artist_normalized:
            primary_artist = artist_normalized.split(sep)[0].strip()
            break

    # Check known artists - prioritize hip-hop to avoid false pop matches
    # Genre priority: hiphop > rnb > rock > country > dance > pop
    genre_priority = ['hiphop', 'rnb', 'rock', 'country', 'dance', 'pop']

    def check_artist_match(artist_str: str, genre: str) -> bool:
        """Check if artist string matches any known artist in genre."""
        for known_artist in ARTIST_GENRES.get(genre, []):
            known_normalized = normalize_name(known_artist)

            # Use word boundary matching for short names, substring for longer ones
            if len(known_normalized) <= 4:
                # Short names need word boundaries (e.g., "eve", "pink", "u2", "ti")
                pattern = r'\b' + re.escape(known_normalized) + r'\b'
                if re.search(pattern, artist_str):
                    return True
            else:
                # Longer names can use substring matching on normalized version
                if known_normalized in artist_str:
                    return True
        return False

    # First check the PRIMARY artist against prioritized genres
    for genre in genre_priority:
        if check_artist_match(primary_artist, genre):
            return genre

    # Then check the FULL artist string (including featured artists)
    for genre in genre_priority:
        if check_artist_match(artist_normalized, genre):
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
