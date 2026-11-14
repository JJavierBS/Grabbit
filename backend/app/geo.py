"""Match a headquarters ("City, Country", as Cala gives it) against countries or regions.

The investor says "Europe" or "the Nordics" as often as a country, so a profile's
`filters.countries` may hold region names; they expand to their countries here.
"""

NORDICS = ["Denmark", "Finland", "Iceland", "Norway", "Sweden"]
BALTICS = ["Estonia", "Latvia", "Lithuania"]
DACH = ["Austria", "Germany", "Switzerland"]
EU = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Czech Republic",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland",
    "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland",
    "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
]  # fmt: skip
EUROPE = EU + [
    "Albania", "Andorra", "Armenia", "Bosnia and Herzegovina", "Georgia", "Iceland",
    "Kosovo", "Liechtenstein", "Moldova", "Monaco", "Montenegro", "North Macedonia",
    "Norway", "San Marino", "Serbia", "Switzerland", "Turkey", "Ukraine",
    "United Kingdom", "UK", "England", "Scotland", "Wales",
]  # fmt: skip

REGIONS: dict[str, list[str]] = {
    "europe": EUROPE,
    "european union": EU,
    "eu": EU,
    "nordics": NORDICS,
    "nordic countries": NORDICS,
    "scandinavia": ["Denmark", "Norway", "Sweden"],
    "baltics": BALTICS,
    "dach": DACH,
    "cee": ["Bulgaria", "Croatia", "Czechia", "Czech Republic", "Estonia", "Hungary",
            "Latvia", "Lithuania", "Poland", "Romania", "Slovakia", "Slovenia", "Ukraine"],
    "uk": ["United Kingdom", "UK", "England", "Scotland", "Wales", "Northern Ireland"],
    "usa": ["United States"],
    "us": ["United States"],
}  # fmt: skip


def expand(places: list[str]) -> set[str]:
    """Lower-case country names for a list of countries and regions."""
    out: set[str] = set()
    for place in places:
        key = place.strip().lower()
        out.update(c.lower() for c in REGIONS.get(key, [place.strip()]))
    return out


def hq_in(hq: str, places: list[str]) -> bool:
    """True when the headquarters' country, its city or the whole string is one of the places."""
    wanted = expand(places)
    text = hq.strip().lower()
    return text in wanted or any(part.strip() in wanted for part in text.split(","))
