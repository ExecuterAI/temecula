#!/usr/bin/env python3
"""Build expanded The Wine Collection catalog JSON."""
from __future__ import annotations

import json
import re
from pathlib import Path

TAG_MAP = {
    "🍇": "wine",
    "🥂": "lifestyle",
    "🏡": "estate",
    "🍽️": "food",
    "🌎": "travel",
    "❤️": "romance",
    "🌅": "scenery",
    "👨‍👩‍👧": "family",
    "👩‍🌾": "craft",
    "🏆": "education",
    "💎": "luxury",
    "🍷": "wine",
    "🌾": "scenery",
    "👨‍🌾": "craft",
    "👨‍👦": "family",
    "👩‍💼": "lifestyle",
}
FMT = {"🎬": "film", "📺": "tv", "🎥": "doc", "🎞️": "indie"}
WEIGHTS = {
    "wine": 0.20,
    "lifestyle": 0.20,
    "scenery": 0.15,
    "food": 0.10,
    "travel": 0.10,
    "luxury": 0.10,
    "story": 0.05,
    "family": 0.05,
    "education": 0.05,
}


def slugify(s: str) -> str:
    s = s.lower().strip().replace("'", "'")
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def parse_imdb(x):
    if x is None or x in ("", "—", "-"):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", str(x))
    return float(m.group(1)) if m else None


def parse_tags(s):
    if not s:
        return []
    if isinstance(s, list):
        return list(s)
    out = []
    for ch in s:
        if ch in TAG_MAP and TAG_MAP[ch] not in out:
            out.append(TAG_MAP[ch])
    return out


titles: dict = {}


def upsert(
    title,
    year=None,
    year_label=None,
    fmt="film",
    imdb=None,
    rating=None,
    region=None,
    tags=None,
    platform=None,
    platform_original=False,
    aka=None,
    editorial=None,
    wine_connection=None,
    why=None,
    shelves=None,
):
    t = title.strip()
    low = t.lower()
    if low.startswith("wine documentaries"):
        return None
    if "sideways" in low:
        return None
    if low == "the widow clicquot":
        t = "Widow Clicquot"
    if low in ("the vintner's luck", "the vintners luck"):
        base = titles.get("a-heavenly-vintage")
        if base:
            base["aka"] = "The Vintner's Luck"
            if shelves:
                for s in shelves:
                    if s not in base["shelves"]:
                        base["shelves"].append(s)
            return base["id"]
        t = "A Heavenly Vintage"
        aka = aka or "The Vintner's Luck"

    tid = slugify(t)
    yl = year_label
    y = year
    if isinstance(y, str):
        m = re.search(r"(\d{4})", y)
        y = int(m.group(1)) if m else None
        if year_label is None:
            yl = year
    if yl is None and y is not None:
        yl = str(y)

    if tid not in titles:
        titles[tid] = {
            "id": tid,
            "title": t,
            "aka": aka,
            "year": y,
            "yearLabel": yl or (str(y) if y else "—"),
            "format": fmt,
            "imdb": parse_imdb(imdb),
            "rating": rating if rating not in (None, "—", "-") else None,
            "region": region,
            "tags": parse_tags(tags) if not isinstance(tags, list) else list(tags or []),
            "platform": platform,
            "platformOriginal": bool(platform_original),
            "editorial": editorial,
            "wineConnection": wine_connection or "Lifestyle",
            "why": why,
            "shelves": [],
            "homepageFeatured": False,
        }
    else:
        e = titles[tid]
        if aka and not e.get("aka"):
            e["aka"] = aka
        if y and not e.get("year"):
            e["year"] = y
        if yl:
            e["yearLabel"] = yl
        if fmt == "indie":
            e["format"] = "indie"
        elif fmt and e.get("format") in (None, "film"):
            e["format"] = fmt
        if parse_imdb(imdb) is not None:
            e["imdb"] = parse_imdb(imdb)
        if rating and rating not in ("—", "-"):
            e["rating"] = rating
        if region and (
            not e.get("region") or len(str(region)) >= len(str(e.get("region") or ""))
        ):
            e["region"] = region
        nt = parse_tags(tags) if not isinstance(tags, list) else list(tags or [])
        for x in nt:
            if x not in e["tags"]:
                e["tags"].append(x)
        if platform:
            e["platform"] = platform
        if platform_original:
            e["platformOriginal"] = True
        if editorial:
            e["editorial"] = editorial
        if why:
            e["why"] = why
        wc = wine_connection
        if wc == "Direct" or (
            wc
            and e.get("wineConnection") in (None, "Lifestyle")
            and wc in ("Strong", "Direct", "Adjacent")
        ):
            e["wineConnection"] = wc

    if shelves:
        for s in shelves:
            if s not in titles[tid]["shelves"]:
                titles[tid]["shelves"].append(s)
    return tid


def add_rows(rows, shelf, default_wc="Lifestyle"):
    for row in rows:
        yl = row[7] if len(row) > 7 else None
        upsert(
            row[0],
            row[1],
            yl,
            FMT[row[2]],
            row[3],
            row[4],
            row[5],
            row[6],
            shelves=[shelf],
            wine_connection=default_wc,
        )


def mark(names, shelf, tag=None):
    for n in names:
        upsert(n, shelves=[shelf])
        tid = slugify(n)
        if tag and tid in titles and tag not in titles[tid]["tags"]:
            titles[tid]["tags"].append(tag)


# ---- data load (sections I-XXXIX concrete titles) ----
add_rows(
    [
        ("A Good Year", 2006, "🎬", 6.9, "PG-13", "Provence, France", "🍇🥂🏡🍽️🌎❤️🌅"),
        ("A Walk in the Clouds", 1995, "🎬", 6.7, "PG-13", "Napa Valley, CA", "🍇❤️🏡🌅"),
        ("Bottle Shock", 2008, "🎬", 6.8, "PG-13", "Napa Valley, CA", "🍇👩‍🌾🏆🌅"),
        ("The Secret of Santa Vittoria", 1969, "🎬", 7.2, "PG-13", "Italy", "🍇👨‍👩‍👧🍽️🌎"),
        ("Back to Burgundy", 2017, "🎬", 6.8, None, "Burgundy, France", "🍇👨‍👩‍👧👩‍🌾🌅"),
        ("You Will Be My Son", 2011, "🎬", 6.9, None, "Bordeaux, France", "🍇👨‍👩‍👧🏡👩‍🌾"),
        ("Under the Tuscan Sun", 2003, "🎬", 6.7, "PG-13", "Tuscany, Italy", "🥂🏡🍽️🌎❤️🌅"),
        ("Letters to Juliet", 2010, "🎬", 6.5, "PG", "Tuscany / Verona, Italy", "🥂🌎❤️🌅"),
        ("Widow Clicquot", 2024, "🎬", None, "PG-13", "Champagne, France", "🍇🥂💎"),
        ("The Wine Show", 2016, "📺", 8.8, "TV", "Global", "🍇🥂🌎🏆", "2016–"),
        ("Drops of God", 2023, "📺", 8.0, "TV-MA", "France / Italy / Japan", "🍇🥂💎🌎🏆", "2023–"),
        ("Somm", 2012, "🎥", 7.0, "NR", "Global / USA", "🥂🏆🍽️"),
        ("Somm: Into the Bottle", 2015, "🎥", 7.3, "NR", "Global", "🍇🏆🌎"),
        ("Somm 3", 2018, "🎥", 7.3, "NR", "France / USA", "🍇🏆"),
        ("A Year in Burgundy", 2013, "🎥", None, "TV-14", "Burgundy", "🍇👩‍🌾🌅"),
        ("A Year in Champagne", 2014, "🎥", None, "TV-PG", "Champagne", "🍇🥂🌅"),
        ("Red Obsession", 2013, "🎥", 7.0, "NR", "Bordeaux / China", "🍇💎🌎"),
        ("Mondovino", 2004, "🎥", 7.0, "PG-13", "Global", "🍇🏆🌎"),
        ("From the Vine", 2019, "🎞️", None, "TV-MA", "Italy", "🍇👨‍👩‍👧🏡🍽️🌅"),
        ("Uncorked", 2020, "🎬", None, "TV-MA", "USA", "🥂🏆🍽️👨‍👩‍👧"),
        ("A Perfect Pairing", 2022, "🎬", 6.1, "TV-14", "Australia", "🍇🥂🌎❤️"),
        ("The Chateau Meroux", 2011, "🎞️", 5.2, "PG-13", "California", "🍇🏡❤️🥂"),
        ("The Wine of Summer", 2013, "🎞️", 5.1, "PG", "Spain", "🍷🌎❤️🌅"),
        ("A Heavenly Vintage", 2009, "🎬", 5.6, "R", "France", "🍇❤️🌅"),
    ],
    "essentials",
    "Direct",
)
titles["a-heavenly-vintage"]["aka"] = "The Vintner's Luck"

add_rows(
    [
        ("Wine Country", 2019, "🎬", 5.4, "R", "Napa Valley, CA", "🥂🌎🍽️"),
        ("The Parent Trap", 1998, "🎬", 6.6, "PG", "Napa Valley, CA", "🍇🏡👨‍👩‍👧"),
        ("Decanted", 2016, "🎥", None, "NR", "Napa Valley, CA", "🍇🌅👩‍🌾"),
        ("Napa", None, "📺", None, None, "Napa Valley, CA", "🍇🌎", "various"),
        ("Falcon Crest", 1981, "📺", 6.1, "TV-PG", "Napa / Northern California", "🍇🏡👨‍👩‍👧💎", "1981–1990"),
        ("The Bachelor", 1999, "🎬", 5.1, "PG-13", "California", "🏡🌅"),
        ("Bottle Shock: The Wine Game", 2020, "🎬", None, None, "California", "🍷🏆", "2020s"),
        ("A Walk in the Clouds", 1995, "🎬", 6.7, "PG-13", "Napa Valley, CA", "🍇❤️🏡🌅"),
        ("Bottle Shock", 2008, "🎬", 6.8, "PG-13", "Napa Valley, CA", "🍇🏆👩‍🌾"),
        ("The Chateau Meroux", 2011, "🎞️", 5.2, "PG-13", "California", "🍇🏡❤️"),
    ],
    "california-napa",
    "Direct",
)
titles["wine-country"]["platform"] = "netflix"
titles["wine-country"]["platformOriginal"] = True
titles["wine-country"]["editorial"] = (
    "Lighter comedy/lifestyle — Napa birthday getaway among friends. Not an aspirational standard-setter."
)
titles["wine-country"]["wineConnection"] = "Lifestyle"

add_rows(
    [
        ("The Big Chill", 1983, "🎬", 7.1, "R", "USA", "🥂🍽️"),
        ("The Holiday", 2006, "🎬", 6.9, "PG-13", "England / California", "🥂🏡❤️"),
        ("It's Complicated", 2009, "🎬", 6.5, "R", "Santa Barbara / California", "🥂🏡🍽️❤️"),
        ("The Parent Trap", 1998, "🎬", 6.6, "PG", "Napa Valley, CA", "🍇🏡👨‍👩‍👧"),
        ("A Walk in the Clouds", 1995, "🎬", 6.7, "PG-13", "California", "🍇❤️🌅"),
        ("The Chateau Meroux", 2011, "🎞️", 5.2, "PG-13", "California", "🍇🏡❤️"),
    ],
    "central-coast",
    "Lifestyle",
)

add_rows(
    [
        ("Under the Tuscan Sun", 2003, "🎬", 6.7, "PG-13", "Tuscany, Italy", "🥂🏡🌎❤️🌅"),
        ("Letters to Juliet", 2010, "🎬", 6.5, "PG", "Tuscany / Verona, Italy", "🌎❤️🌅"),
        ("Stealing Beauty", 1996, "🎬", 6.5, "R", "Tuscany, Italy", "🏡🌅🌎"),
        ("A Room with a View", 1985, "🎬", 7.2, "G", "Italy", "🏡❤️🌎"),
        ("Much Ado About Nothing", 1993, "🎬", 7.3, "PG-13", "Italy", "🏡🌅❤️"),
        ("Tea with Mussolini", 1999, "🎬", 6.9, "PG", "Italy", "🏡🌅👨‍👩‍👧"),
        ("The English Patient", 1996, "🎬", 7.4, "R", "Italy / North Africa", "🌅❤️🏡"),
        ("The Talented Mr. Ripley", 1999, "🎬", 7.4, "R", "Italy", "💎🌎🏡"),
        ("Life Is Beautiful", 1997, "🎬", 8.6, "PG-13", "Italy", "🍽️👨‍👩‍👧"),
        ("The Best of Youth", 2003, "🎬", 8.5, "NR", "Italy", "👨‍👩‍👧"),
        ("La Dolce Villa", 2025, "🎬", None, "TV-PG", "Tuscany, Italy", "🏡🌎❤️🌅"),
        ("Love in the Villa", 2022, "🎬", 5.4, "TV-PG", "Verona, Italy", "🌎❤️🏡"),
        ("Eat Pray Love", 2010, "🎬", 5.8, "PG-13", "Italy / Global", "🍽️🌎❤️"),
    ],
    "tuscany",
    "Lifestyle",
)
titles["la-dolce-villa"]["platform"] = "netflix"
titles["la-dolce-villa"]["editorial"] = (
    "Crumbling Tuscan villa, beauty, romance, and finding new purpose."
)
titles["love-in-the-villa"]["platform"] = "netflix"

add_rows(
    [
        ("Barolo Boys", 2014, "🎥", 7.1, "NR", "Piedmont, Italy", "🍇🏆👩‍🌾🌎"),
        ("The Truffle Hunters", 2020, "🎥", 7.2, "PG-13", "Piedmont, Italy", "🍽️🌎👩‍🌾🌅"),
        ("The Wine Show — Italy episodes", 2016, "📺", 8.8, "TV", "Italy", "🍇🥂🌎", "2016–"),
        ("Stealing Beauty", 1996, "🎬", 6.5, "R", "Italy", "🌅🏡"),
        ("A Room with a View", 1985, "🎬", 7.2, "G", "Italy", "🌎🏡❤️"),
    ],
    "piedmont",
    "Direct",
)

add_rows(
    [
        ("A Good Year", 2006, "🎬", 6.9, "PG-13", "Provence, France", "🍇🥂🏡🍽️🌎❤️"),
        ("A Year in Provence", 1993, "📺", None, "TV", "Provence, France", "🏡🍽️🌎🌅"),
        ("Jean de Florette", 1986, "🎬", 8.0, "PG", "Provence, France", "🌾🏡🌅"),
        ("Manon des Sources", 1986, "🎬", 8.0, "PG", "Provence, France", "🌾🌅"),
        ("Chocolat", 2000, "🎬", 7.2, "PG-13", "France", "🍽️🥂🌅"),
        ("French Kiss", 1995, "🎬", 6.6, "PG-13", "France", "🌎❤️🍽️"),
        ("A Heavenly Vintage", 2009, "🎬", 5.6, "R", "France", "🍇❤️🌅"),
        ("The Wine of Summer", 2013, "🎞️", 5.1, "PG", "Spain", "🍷🌎❤️"),
    ],
    "provence",
    "Strong",
)

add_rows(
    [
        ("Back to Burgundy", 2017, "🎬", 6.8, None, "Burgundy, France", "🍇👨‍👩‍👧👩‍🌾🌅"),
        ("A Year in Burgundy", 2013, "🎥", None, "TV-14", "Burgundy, France", "🍇👩‍🌾🌅"),
        ("Burgundy: People with a Passion for Wine", 2016, "🎥", None, None, "Burgundy, France", "🍇🏆🌅"),
        ("Saint Amour", 2016, "🎬", 6.2, None, "France", "🍷👨‍👦🌎"),
        ("The Wine Show — Burgundy episodes", 2016, "📺", 8.8, "TV", "Burgundy, France", "🍇🏆🌎", "2016–"),
    ],
    "burgundy",
    "Direct",
)

add_rows(
    [
        ("You Will Be My Son", 2011, "🎬", 6.9, None, "Bordeaux, France", "🍇🏡👨‍👩‍👧"),
        ("Red Obsession", 2013, "🎥", 7.0, "NR", "Bordeaux / China", "🍇💎🌎"),
        ("Mondovino", 2004, "🎥", 7.0, "PG-13", "Global", "🍇🏆🌎"),
        ("The Wine Show — Bordeaux episodes", 2016, "📺", 8.8, "TV", "Bordeaux, France", "🍇💎", "2016–"),
    ],
    "bordeaux",
    "Direct",
)

add_rows(
    [
        ("Widow Clicquot", 2024, "🎬", None, "PG-13", "Champagne, France", "🍇🥂💎"),
        ("A Year in Champagne", 2014, "🎥", None, "TV-PG", "Champagne, France", "🍇🥂🌅"),
        ("Champagne Charlie", 1989, "🎬", None, None, "Champagne, France", "🥂🍇"),
    ],
    "champagne",
    "Direct",
)

add_rows(
    [
        ("The Wine of Summer", 2013, "🎞️", 5.1, "PG", "Spain", "🍷🌎❤️🌅"),
        ("The Trip to Spain", 2017, "🎬", 6.8, "R", "Spain", "🍽️🥂🌎"),
        ("Vicky Cristina Barcelona", 2008, "🎬", 6.9, "PG-13", "Spain", "🌎🍷❤️"),
        ("The Way", 2010, "🎬", 7.3, "PG-13", "Spain", "🌎🍽️"),
        ("The Trip — Spain episodes", None, "📺", None, None, "Spain", "🍽️🥂🌎", "various"),
    ],
    "spain",
    "Lifestyle",
)

add_rows(
    [
        ("A Year in Port", 2016, "🎥", None, "NR", "Douro, Portugal", "🍇🥂🌎"),
        ("Porto", 2016, "🎬", 6.1, "R", "Portugal", "🌎❤️"),
        ("Night Train to Lisbon", 2013, "🎬", 6.8, "PG-13", "Portugal", "🌎🏡"),
        ("The Wine Show — Portugal episodes", 2016, "📺", 8.8, "TV", "Portugal", "🍇🥂🌎", "2016–"),
    ],
    "portugal",
    "Strong",
)

add_rows(
    [
        ("A Perfect Pairing", 2022, "🎬", 6.1, "TV-14", "Australia", "🍇🥂🌎❤️"),
        ("Chateau Chunder: A Wine Revolution", 2009, "🎥", None, "NR", "Australia", "🍇🏆"),
        ("The Australian Wine Revolution", 2019, "🎥", None, "NR", "Australia", "🍇👩‍🌾🏆"),
        ("The Wine Show — Australia episodes", 2016, "📺", 8.8, "TV", "Australia", "🍇🥂🌎", "2016–"),
        ("The Dressmaker", 2015, "🎬", 7.0, "R", "Australia", "🌅🏡"),
        ("Australia", 2008, "🎬", 6.6, "PG-13", "Australia", "🌅🌎🏡"),
        ("The Sapphires", 2012, "🎬", 7.0, "PG-13", "Australia", "🌎"),
        ("A Few Best Men", 2011, "🎬", 5.7, "R", "Australia", "🥂🍽️"),
    ],
    "australia",
    "Strong",
)
titles["a-perfect-pairing"]["platform"] = "netflix"
titles["a-perfect-pairing"]["editorial"] = (
    "LA wine-company executive travels to Australia to land a wine client."
)

add_rows(
    [
        ("El camino del vino", 2010, "🎬", 7.1, None, "Argentina", "🍇🏆🍽️"),
        ("Somm 3", 2018, "🎥", 7.3, "NR", "Global", "🍷🏆"),
        ("The Wine Show — Argentina episodes", 2016, "📺", 8.8, "TV", "Argentina", "🍇🥂🌎", "2016–"),
    ],
    "argentina",
    "Direct",
)

add_rows(
    [
        ("Somm: Into the Bottle", 2015, "🎥", 7.3, "NR", "Global", "🍇🏆🌎"),
        ("Mondovino", 2004, "🎥", 7.0, "PG-13", "Global", "🍇🌎"),
    ],
    "chile",
    "Strong",
)

add_rows(
    [
        ("The Winemaker's Secret", 2016, "🎬", None, None, "South Africa", "🍇🏡👨‍👩‍👧"),
    ],
    "south-africa",
    "Direct",
)

for name, year, fmt, imdb, tags in [
    ("Somm", 2012, "🎥", 7.0, "🏆🍷"),
    ("Somm: Into the Bottle", 2015, "🎥", 7.3, "🏆🍇🌎"),
    ("Somm 3", 2018, "🎥", 7.3, "🏆🍇"),
    ("Uncorked", 2020, "🎬", None, "🏆🥂👨‍👩‍👧"),
    ("Wine for the Confused", 2004, "🎥", None, "🏆"),
    ("Wine Calling", 2018, "🎥", None, "🍇👩‍🌾🌎"),
    ("A Year in Burgundy", 2013, "🎥", None, "🍇🏆"),
    ("A Year in Champagne", 2014, "🎥", None, "🍇🏆"),
    ("A Year in Port", 2016, "🎥", None, "🍇🏆"),
    ("Red Obsession", 2013, "🎥", 7.0, "🍇💎🏆"),
    ("Mondovino", 2004, "🎥", 7.0, "🍇🏆🌎"),
    ("Barolo Boys", 2014, "🎥", 7.1, "🍇🏆🌎"),
    ("Decanted", 2016, "🎥", None, "🍇🌅"),
    ("Sour Grapes", 2016, "🎥", 7.0, "🍷🏆"),
]:
    upsert(
        name,
        year,
        None,
        FMT[fmt],
        imdb,
        None,
        None,
        tags,
        shelves=["wine-education"],
        wine_connection="Direct",
    )

for row in [
    ("From the Vine", 2019, "🎞️", None, "TV-MA", "Italy", "🍇🏡🍽️👨‍👩‍👧"),
    ("The Chateau Meroux", 2011, "🎞️", 5.2, "PG-13", "California", "🍇🏡❤️"),
    ("The Wine of Summer", 2013, "🎞️", 5.1, "PG", "Spain", "🍷🌎❤️"),
    ("A Heavenly Vintage", 2009, "🎞️", 5.6, "R", "France", "🍇❤️🌅"),
    ("Barolo Boys", 2014, "🎥", 7.1, "NR", "Italy", "🍇🏆🌎"),
    ("Decanted", 2016, "🎥", None, "NR", "Napa", "🍇🌅"),
    ("Wine Calling", 2018, "🎥", None, "NR", "France", "🍇👩‍🌾"),
    ("Burgundy: People with a Passion for Wine", 2016, "🎥", None, None, "France", "🍇👩‍🌾"),
    ("A Year in Port", 2016, "🎥", None, "NR", "Portugal", "🍇🌎"),
    ("The Winemaker's Secret", 2016, "🎬", None, None, "South Africa", "🍇🏡"),
    ("Year of the Comet", 1992, "🎬", 5.9, "PG-13", "Europe", "🍷🌎"),
]:
    upsert(
        row[0],
        row[1],
        None,
        FMT[row[2]],
        row[3],
        row[4],
        row[5],
        row[6],
        shelves=["indie-gems"],
        wine_connection="Strong",
    )

for name, y, imdb, rating, orig, tags, region in [
    ("Uncorked", 2020, None, "TV-MA", True, "🍷🏆🍽️👨‍👩‍👧", "USA"),
    ("A Perfect Pairing", 2022, 6.1, "TV-14", False, "🍇🥂🌎❤️", "Australia"),
    ("Wine Country", 2019, 5.4, "R", True, "🍇🥂🌎", "Napa Valley, CA"),
    ("Holiday in the Vineyards", 2023, 6.2, "PG", False, "🍇❤️🏡", "California"),
    ("A California Christmas", 2020, 5.9, "PG-13", False, "🌾❤️🌅", "California"),
    ("A California Christmas: City Lights", 2021, 5.6, "PG-13", False, "🍇❤️🏡", "California"),
    ("From the Vine", 2019, None, "TV-MA", False, "🍇🏡", "Italy"),
    ("A Year in Burgundy", 2013, None, "TV-14", False, "🍇", "Burgundy, France"),
]:
    fmt = "doc" if name == "A Year in Burgundy" else "film"
    if name == "From the Vine":
        fmt = "indie"
    upsert(
        name,
        y,
        None,
        fmt,
        imdb,
        rating,
        region,
        tags,
        platform="netflix",
        platform_original=orig,
        shelves=["netflix-wine"],
        wine_connection="Direct",
    )
titles["uncorked"]["platformOriginal"] = True
titles["wine-country"]["platformOriginal"] = True

for name, y, tags, region in [
    ("Under the Tuscan Sun", 2003, "🏡🍽️🌎❤️", "Tuscany, Italy"),
    ("Letters to Juliet", 2010, "🌎❤️🌅", "Italy"),
    ("Eat Pray Love", 2010, "🍽️🌎❤️", "Italy / Global"),
    ("Love in the Villa", 2022, "🏡❤️🌎", "Italy"),
    ("La Dolce Villa", 2025, "🏡❤️🌅", "Tuscany, Italy"),
    ("The Last Letter from Your Lover", 2021, "❤️🏡", "Italy / UK"),
    ("Falling Inn Love", 2019, "🏡❤️🌅", "New Zealand"),
    ("The Trip to Italy", 2014, "🍽️🥂", "Italy"),
    ("The Trip to Spain", 2017, "🍽️🥂", "Spain"),
]:
    upsert(
        name,
        y,
        None,
        "film",
        None,
        None,
        region,
        tags,
        platform="netflix",
        shelves=["netflix-lifestyle"],
        wine_connection="Lifestyle",
    )

for name, y, fmt, tags, region, plat, yl in [
    ("The Bear", 2022, "📺", "🍽️🥂🏆", "USA", "hulu_fx", "2022–"),
    ("The Great", 2020, "📺", "🏡🍽️🌎", "Europe", "hulu", "2020–2023"),
    ("Taste the Nation", 2020, "📺", "🍽️🌎", "USA", "hulu", "2020–"),
    ("Stanley Tucci: Searching for Italy", 2021, "📺", "🍽️🍷", "Italy", "hulu", "2021–"),
    ("The Next Thing You Eat", 2021, "📺", "🍽️🌎", "USA", "hulu", None),
]:
    upsert(
        name,
        y,
        yl,
        FMT[fmt],
        None,
        None,
        region,
        tags,
        platform=plat,
        shelves=["food-hospitality-streaming"],
        wine_connection="Adjacent",
    )

for name, y, region, tags in [
    ("Call Me by Your Name", 2017, "Northern Italy", "🌅🍽️🏡❤️"),
    ("Only You", 1994, "Italy", "🌎❤️"),
    ("The Best Exotic Marigold Hotel", 2011, "India", "🌎🏡"),
    ("The Trip to Italy", 2014, "Italy", "🍽️🥂🌎"),
]:
    upsert(
        name,
        y,
        None,
        "film",
        None,
        None,
        region,
        tags,
        shelves=["want-that-life"],
        wine_connection="Lifestyle",
    )

mark(
    [
        "Under the Tuscan Sun",
        "A Good Year",
        "Letters to Juliet",
        "A Room with a View",
        "Stealing Beauty",
        "Much Ado About Nothing",
        "The Talented Mr. Ripley",
        "The English Patient",
        "Call Me by Your Name",
        "Only You",
        "Eat Pray Love",
        "The Trip to Italy",
        "The Trip to Spain",
        "Chocolat",
        "French Kiss",
        "La Dolce Villa",
        "Love in the Villa",
        "Falling Inn Love",
        "The Holiday",
        "It's Complicated",
        "The Big Chill",
        "The Best Exotic Marigold Hotel",
        "A California Christmas",
        "A California Christmas: City Lights",
        "The Dressmaker",
        "Australia",
        "Vicky Cristina Barcelona",
    ],
    "want-that-life",
)

for name, y, fmt, yl in [
    ("Big Night", 1996, "🎬", None),
    ("Babette's Feast", 1987, "🎬", None),
    ("The Hundred-Foot Journey", 2014, "🎬", None),
    ("Chef", 2014, "🎬", None),
    ("Julie & Julia", 2009, "🎬", None),
    ("Eat Pray Love", 2010, "🎬", None),
    ("Chocolat", 2000, "🎬", None),
    ("The Trip to Italy", 2014, "🎬", None),
    ("The Trip to Spain", 2017, "🎬", None),
    ("The Trip to Greece", 2020, "🎬", None),
    ("A Good Year", 2006, "🎬", None),
    ("Under the Tuscan Sun", 2003, "🎬", None),
    ("The Bear", 2022, "📺", "2022–"),
    ("Stanley Tucci: Searching for Italy", 2021, "📺", "2021–"),
    ("Somebody Feed Phil", 2018, "📺", "2018–"),
    ("Anthony Bourdain: Parts Unknown", 2013, "📺", "2013–2018"),
    ("Chef's Table", 2015, "📺", "2015–"),
    ("The Wine Show", 2016, "📺", "2016–"),
]:
    upsert(
        name,
        y,
        yl,
        FMT[fmt],
        None,
        None,
        None,
        "🍽️🥂",
        shelves=["food-wine-entertaining"],
        wine_connection="Strong",
    )

for name, y, region in [
    ("A Good Year", 2006, "Provence"),
    ("Under the Tuscan Sun", 2003, "Tuscany"),
    ("A Walk in the Clouds", 1995, "Napa"),
    ("The Chateau Meroux", 2011, "California"),
    ("Back to Burgundy", 2017, "Burgundy"),
    ("You Will Be My Son", 2011, "Bordeaux"),
    ("Stealing Beauty", 1996, "Tuscany"),
    ("A Room with a View", 1985, "Italy"),
    ("La Dolce Villa", 2025, "Tuscany"),
    ("The Talented Mr. Ripley", 1999, "Italy"),
    ("The English Patient", 1996, "Italy/North Africa"),
    ("The Parent Trap", 1998, "Napa"),
    ("Much Ado About Nothing", 1993, "Italy"),
    ("Letters to Juliet", 2010, "Tuscany"),
    ("The Holiday", 2006, "England/California"),
    ("It's Complicated", 2009, "Santa Barbara/California"),
]:
    upsert(
        name,
        y,
        None,
        "film",
        None,
        None,
        region,
        "🏡🍇",
        shelves=["estates-villas"],
        wine_connection="Lifestyle",
    )

mark(
    [
        "A Good Year",
        "A Walk in the Clouds",
        "Under the Tuscan Sun",
        "Letters to Juliet",
        "The Wine of Summer",
        "A Heavenly Vintage",
        "The Chateau Meroux",
        "Love in the Villa",
        "La Dolce Villa",
        "Only You",
        "A Room with a View",
        "Stealing Beauty",
        "Much Ado About Nothing",
        "French Kiss",
        "Call Me by Your Name",
        "Vicky Cristina Barcelona",
        "A Perfect Pairing",
        "Holiday in the Vineyards",
        "A California Christmas",
        "A California Christmas: City Lights",
    ],
    "romance",
    "romance",
)

for name, y, why in [
    ("Widow Clicquot", 2024, "Woman building a Champagne empire"),
    ("Under the Tuscan Sun", 2003, "Woman rebuilding her life in Italy"),
    ("The Chateau Meroux", 2011, "Woman inherits and runs a winery"),
    ("A California Christmas", 2020, "Woman protecting family land"),
    ("A California Christmas: City Lights", 2021, "Family / ranch / winery"),
    ("Holiday in the Vineyards", 2023, "Woman protecting a local vineyard"),
    ("Back to Burgundy", 2017, "Family vineyard legacy"),
    ("The Dressmaker", 2015, "Woman returning to rural Australia"),
    ("Julie & Julia", 2009, "Female creativity + food"),
    ("Babette's Feast", 1987, "Hospitality and culinary artistry"),
]:
    upsert(
        name,
        y,
        None,
        "film",
        None,
        None,
        None,
        None,
        why=why,
        shelves=["women-wine-legacy"],
        wine_connection="Strong",
    )

mark(
    [
        "Back to Burgundy",
        "You Will Be My Son",
        "The Secret of Santa Vittoria",
        "Bottle Shock",
        "From the Vine",
        "The Chateau Meroux",
        "The Parent Trap",
        "A California Christmas",
        "A California Christmas: City Lights",
        "Holiday in the Vineyards",
        "The Hundred-Foot Journey",
        "Big Night",
        "Babette's Feast",
    ],
    "family-heritage",
    "family",
)

mark(
    [
        "A Good Year",
        "Under the Tuscan Sun",
        "A Walk in the Clouds",
        "Back to Burgundy",
        "Letters to Juliet",
        "Stealing Beauty",
        "A Room with a View",
        "Call Me by Your Name",
        "The Wine Show",
        "La Dolce Villa",
        "The Talented Mr. Ripley",
        "Much Ado About Nothing",
        "The English Patient",
        "Wine Country",
        "A Perfect Pairing",
    ],
    "golden-hour",
    "scenery",
)

for shelf, names in {
    "road-california": [
        "A Walk in the Clouds",
        "Bottle Shock",
        "The Chateau Meroux",
        "Wine Country",
        "Decanted",
    ],
    "road-provence": [
        "A Good Year",
        "A Year in Provence",
        "Jean de Florette",
        "Manon des Sources",
    ],
    "road-burgundy": [
        "Back to Burgundy",
        "A Year in Burgundy",
        "Burgundy: People with a Passion for Wine",
    ],
    "road-bordeaux": ["You Will Be My Son", "Red Obsession", "Mondovino"],
    "road-champagne": ["Widow Clicquot", "A Year in Champagne"],
    "road-tuscany": [
        "Under the Tuscan Sun",
        "Letters to Juliet",
        "Stealing Beauty",
        "A Room with a View",
        "La Dolce Villa",
    ],
    "road-piedmont": ["Barolo Boys", "The Truffle Hunters"],
    "road-spain": ["The Wine of Summer", "The Trip to Spain", "Vicky Cristina Barcelona"],
    "road-portugal": ["A Year in Port", "Porto"],
    "road-australia": [
        "A Perfect Pairing",
        "Chateau Chunder: A Wine Revolution",
        "The Australian Wine Revolution",
    ],
    "road-argentina": ["El camino del vino"],
    "road-chile": ["Somm: Into the Bottle"],
    "road-south-africa": ["The Winemaker's Secret"],
}.items():
    for n in names:
        upsert(n, shelves=[shelf, "global-road-trip"])

for level, names in {
    "ladder-1": [
        "A Good Year",
        "A Walk in the Clouds",
        "Under the Tuscan Sun",
        "Bottle Shock",
        "Uncorked",
    ],
    "ladder-2": [
        "A Year in Burgundy",
        "A Year in Champagne",
        "Back to Burgundy",
        "The Wine Show",
        "From the Vine",
    ],
    "ladder-3": [
        "Somm",
        "Somm: Into the Bottle",
        "Somm 3",
        "Wine Calling",
        "Red Obsession",
    ],
    "ladder-4": [
        "Drops of God",
        "Mondovino",
        "You Will Be My Son",
        "Barolo Boys",
        "A Year in Burgundy",
    ],
}.items():
    for n in names:
        upsert(n, shelves=[level, "education-ladder"])

mark(
    [
        "From the Vine",
        "The Chateau Meroux",
        "The Wine of Summer",
        "A Heavenly Vintage",
        "Barolo Boys",
        "Decanted",
        "Wine Calling",
        "Burgundy: People with a Passion for Wine",
        "A Year in Port",
        "The Winemaker's Secret",
        "El camino del vino",
        "Chateau Chunder: A Wine Revolution",
        "The Australian Wine Revolution",
        "Saint Amour",
        "A Year in Provence",
        "The Truffle Hunters",
    ],
    "discover-gems",
)

for mood, names in {
    "date-romantic": [
        "A Good Year",
        "Under the Tuscan Sun",
        "Letters to Juliet",
        "A Walk in the Clouds",
        "Love in the Villa",
        "La Dolce Villa",
        "A Perfect Pairing",
        "The Chateau Meroux",
        "The Wine of Summer",
        "French Kiss",
    ],
    "date-sophisticated": [
        "A Room with a View",
        "The Talented Mr. Ripley",
        "Stealing Beauty",
        "Much Ado About Nothing",
        "The English Patient",
        "Call Me by Your Name",
    ],
    "date-food": [
        "Big Night",
        "Babette's Feast",
        "Julie & Julia",
        "The Hundred-Foot Journey",
        "The Trip to Italy",
        "A Good Year",
        "Chocolat",
    ],
}.items():
    for n in names:
        upsert(n, shelves=[mood, "date-night"])

mark(
    [
        "Under the Tuscan Sun",
        "Wine Country",
        "Letters to Juliet",
        "The Chateau Meroux",
        "A California Christmas",
        "A California Christmas: City Lights",
        "La Dolce Villa",
        "Love in the Villa",
        "The Holiday",
        "Eat Pray Love",
        "The Best Exotic Marigold Hotel",
        "The Dressmaker",
    ],
    "girls-getaway",
)

mark(
    [
        "A Good Year",
        "Bottle Shock",
        "The Wine Show",
        "Somm",
        "Red Obsession",
        "Mondovino",
        "Barolo Boys",
        "The Trip to Italy",
        "The Trip to Spain",
        "The Talented Mr. Ripley",
        "From the Vine",
        "The Secret of Santa Vittoria",
    ],
    "men-adventure",
)

mark(
    [
        "A Good Year",
        "Under the Tuscan Sun",
        "A Walk in the Clouds",
        "The Chateau Meroux",
        "La Dolce Villa",
        "Back to Burgundy",
        "You Will Be My Son",
        "The Parent Trap",
        "Stealing Beauty",
        "A Room with a View",
        "Letters to Juliet",
        "Much Ado About Nothing",
        "The Holiday",
        "It's Complicated",
        "From the Vine",
    ],
    "wine-real-estate",
)

top25 = [
    "A Good Year",
    "A Walk in the Clouds",
    "Under the Tuscan Sun",
    "Bottle Shock",
    "Back to Burgundy",
    "Widow Clicquot",
    "The Wine Show",
    "Drops of God",
    "A Year in Burgundy",
    "A Year in Champagne",
    "Uncorked",
    "From the Vine",
    "The Chateau Meroux",
    "La Dolce Villa",
    "A Perfect Pairing",
    "Letters to Juliet",
    "The Secret of Santa Vittoria",
    "You Will Be My Son",
    "Somm",
    "Somm: Into the Bottle",
    "Red Obsession",
    "Barolo Boys",
    "The Wine of Summer",
    "Holiday in the Vineyards",
    "A California Christmas: City Lights",
]
for n in top25:
    tid = slugify(n)
    if tid in titles:
        titles[tid]["homepageFeatured"] = True
        if "homepage-top25" not in titles[tid]["shelves"]:
            titles[tid]["shelves"].append("homepage-top25")


def score_title(t):
    tags = set(t.get("tags") or [])
    shelves = set(t.get("shelves") or [])
    wc = t.get("wineConnection") or "Lifestyle"

    def cat(name):
        s = 5.0
        if name == "wine":
            s = {"Direct": 9.5, "Strong": 8.0, "Adjacent": 4.0}.get(wc, 6.0)
            if "wine" in tags:
                s = min(10, s + 0.5)
            if "craft" in tags:
                s = min(10, s + 0.5)
        elif name == "lifestyle":
            s = 8.5 if ("lifestyle" in tags or "want-that-life" in shelves) else 6.5
            if "estate" in tags:
                s = min(10, s + 1)
        elif name == "scenery":
            s = 9 if ("scenery" in tags or "golden-hour" in shelves) else 5.5
        elif name == "food":
            s = 8.5 if ("food" in tags or "food-wine-entertaining" in shelves) else 4.5
        elif name == "travel":
            s = 8.5 if "travel" in tags else 5.0
        elif name == "luxury":
            s = 8.5 if "luxury" in tags else 5.5
            if "estate" in tags:
                s = min(10, s + 0.5)
        elif name == "story":
            imdb = t.get("imdb")
            s = 6.5 if not imdb else max(4.0, min(9.5, imdb))
        elif name == "family":
            s = 8.5 if ("family" in tags or "family-heritage" in shelves) else 4.0
        elif name == "education":
            s = 9.0 if ("education" in tags or "wine-education" in shelves) else 3.5
        return s

    parts = {k: cat(k) for k in WEIGHTS}
    total = sum(parts[k] * WEIGHTS[k] for k in WEIGHTS) * 10
    t["scores"] = {k: round(v, 1) for k, v in parts.items()}
    t["wineLifeScore"] = int(round(total))
    return t


def why_watch(t):
    if t.get("why"):
        return t["why"]
    if t.get("editorial"):
        return t["editorial"]
    region = t.get("region") or "wine country"
    tags = t.get("tags") or []
    if "education" in tags:
        return f"Makes wine culture fascinating — craft, tasting, and place ({region})."
    if "romance" in tags:
        return f"Romance and atmosphere with a wine-country soul ({region})."
    if "craft" in tags:
        return f"Harvest, heritage, and the work behind the glass ({region})."
    if "estate" in tags:
        return f"Beautiful property energy — villas, estates, and destination living ({region})."
    if "food" in tags:
        return f"Food, hospitality, and the table as celebration ({region})."
    return f"Wine-life inspiration: place, pleasure, and atmosphere ({region})."


for t in titles.values():
    score_title(t)
    t["shortDescription"] = why_watch(t)

SHELVES = [
    {"id": "essentials", "name": "The Bellie Acres Essentials", "blurb": "Highest prominence — foundational titles that define the Collection.", "order": 1},
    {"id": "california-napa", "name": "California Wine Country · Napa / Northern California", "blurb": "Napa light, valley estates, and Northern California wine-country screens.", "order": 2},
    {"id": "central-coast", "name": "Central Coast / Santa Barbara / Santa Ynez", "blurb": "California coast and entertaining-at-home energy with wine-country adjacency.", "order": 3},
    {"id": "tuscany", "name": "Tuscany / Central Italy", "blurb": "Villas, countryside, food, and the Italian dream.", "order": 4},
    {"id": "piedmont", "name": "Piedmont / Barolo / Northern Italy", "blurb": "Nebbiolo country, craft, and northern Italian atmosphere.", "order": 5},
    {"id": "provence", "name": "France — Provence", "blurb": "Lavender light, estates, and Provençal living.", "order": 6},
    {"id": "burgundy", "name": "France — Burgundy", "blurb": "Pinot and Chardonnay country — family domaines and terroir.", "order": 7},
    {"id": "bordeaux", "name": "France — Bordeaux", "blurb": "Châteaux, legacy, and the global Bordeaux story.", "order": 8},
    {"id": "champagne", "name": "France — Champagne", "blurb": "Bubbles, houses, and legacy in the north of France.", "order": 9},
    {"id": "spain", "name": "Spain", "blurb": "Spanish tables, travel, and Mediterranean ease.", "order": 10},
    {"id": "portugal", "name": "Portugal / Douro", "blurb": "Port, Douro valleys, and Portuguese atmosphere.", "order": 11},
    {"id": "australia", "name": "Australia", "blurb": "Down-under wine country, landscape, and hospitality.", "order": 12},
    {"id": "argentina", "name": "Argentina", "blurb": "Malbec country and South American wine roads.", "order": 13},
    {"id": "chile", "name": "Chile", "blurb": "Andean wine world and global craft connections.", "order": 14},
    {"id": "south-africa", "name": "South Africa", "blurb": "Cape winelands atmosphere and estate living.", "order": 15},
    {"id": "wine-education", "name": "Sommelier / Wine Education", "blurb": "Titles that make wine fascinating rather than intimidating.", "order": 16},
    {"id": "indie-gems", "name": "Lesser-Known / Indie Wine Gems", "blurb": "Discoveries beyond the usual top-10 wine-movie lists.", "order": 17},
    {"id": "netflix-wine", "name": "Netflix · Directly Wine-Related", "blurb": "Netflix titles with clear wine or winery storylines. Badges mark Original vs catalog.", "order": 18},
    {"id": "netflix-lifestyle", "name": "Netflix · Wine-Adjacent Lifestyle", "blurb": "Catalog lifestyle titles with villa, travel, food, and escape energy.", "order": 19},
    {"id": "food-hospitality-streaming", "name": "Hulu / FX · Food and Hospitality", "blurb": "Secondary shelf — food and hospitality, not forced as pure wine titles.", "order": 20},
    {"id": "want-that-life", "name": "Wine-Adjacent “I Want That Life”", "blurb": "Wine may be supporting — the lifestyle is the attraction.", "order": 21},
    {"id": "food-wine-entertaining", "name": "Food + Wine + Entertaining", "blurb": "Tables, kitchens, travel food, and hospitality culture.", "order": 22},
    {"id": "estates-villas", "name": "Estates, Villas, Châteaux and Vineyard Property", "blurb": "Architecture and destination property with wine-country soul.", "order": 23},
    {"id": "romance", "name": "The Romantic Cellar", "blurb": "Wine + romance — pour something red and press play.", "order": 24},
    {"id": "women-wine-legacy", "name": "Women, Wine and Legacy", "blurb": "Women building houses, protecting land, and rewriting their lives.", "order": 25},
    {"id": "family-heritage", "name": "Family, Heritage and Legacy", "blurb": "Lineage, land, and the long game of hospitality.", "order": 26},
    {"id": "golden-hour", "name": "Wine Country at Golden Hour", "blurb": "Selected primarily for visual atmosphere.", "order": 27},
    {"id": "global-road-trip", "name": "The Global Wine Road Trip", "blurb": "A passport of regions — California to the Cape.", "order": 28},
    {"id": "education-ladder", "name": "The Wine Education Ladder", "blurb": "From wine-curious to wine geek — climb at your pace.", "order": 29},
    {"id": "discover-gems", "name": "Discover Something You’ve Never Heard Of", "blurb": "Hidden gems we actively surface.", "order": 30},
    {"id": "date-night", "name": "Date Night + Wine", "blurb": "What to watch tonight with a bottle.", "order": 31},
    {"id": "girls-getaway", "name": "Girls’ Wine Country Getaway", "blurb": "Group-trip energy, villas, and getaway films.", "order": 32},
    {"id": "men-adventure", "name": "Men + Wine + Adventure", "blurb": "Craft, travel, competition, and estate adventure.", "order": 33},
    {"id": "wine-real-estate", "name": "Wine and Real Estate", "blurb": "Property, architecture, and destination living.", "order": 34},
]

assert all("sideways" not in t["title"].lower() for t in titles.values())

catalog = {
    "version": 2,
    "title": "The Wine Collection",
    "subtitle": "Movies, Television and Documentaries That Inspire the Wine Life",
    "brand": "Bellie Acres Wine",
    "homepageIntro": {
        "eyebrow": "THE WINE COLLECTION",
        "lines": [
            "Pour yourself a glass. Press play. Go somewhere.",
            "Some movies make you want to fall in love.",
            "Some make you want to travel.",
            "Some make you want to cook a beautiful dinner.",
            "And then there are the ones that make you want to pour a glass of wine, sit outside beneath the evening sky and imagine yourself somewhere else.",
            "Welcome to The Wine Collection.",
            "From California wine country to Tuscany, Provence, Burgundy, Bordeaux, Champagne, Australia, Argentina and beyond, we’ve gathered movies, series and documentaries that celebrate the places, people, food, landscapes and pleasures surrounding wine.",
            "Some are about winemaking. Some are about travel. Some are about family, friendship or romance. And some simply make you think: “I want to live there.”",
            "Pour something wonderful and press play.",
        ],
    },
    "exclusions": ["Sideways (2004)"],
    "formats": {
        "film": {"emoji": "🎬", "label": "Feature Film"},
        "tv": {"emoji": "📺", "label": "Television / Series"},
        "doc": {"emoji": "🎥", "label": "Documentary"},
        "indie": {"emoji": "🎞️", "label": "Independent / Lesser-Known"},
    },
    "tags": {
        "wine": {"emoji": "🍇", "label": "Wine / Vineyard"},
        "lifestyle": {"emoji": "🥂", "label": "Wine Lifestyle"},
        "estate": {"emoji": "🏡", "label": "Estate / Property"},
        "food": {"emoji": "🍽️", "label": "Food and Wine"},
        "travel": {"emoji": "🌎", "label": "Travel"},
        "romance": {"emoji": "❤️", "label": "Romance"},
        "scenery": {"emoji": "🌅", "label": "Scenery / Atmosphere"},
        "family": {"emoji": "👨‍👩‍👧", "label": "Family / Legacy"},
        "craft": {"emoji": "👩‍🌾", "label": "Winemaking / Agriculture"},
        "education": {"emoji": "🏆", "label": "Wine Education"},
        "luxury": {"emoji": "💎", "label": "Luxury / Sophistication"},
    },
    "platforms": {
        "netflix": {"label": "Netflix", "originalLabel": "Netflix Original"},
        "hulu": {"label": "Hulu"},
        "hulu_fx": {"label": "Hulu / FX"},
    },
    "scoreWeights": WEIGHTS,
    "shelves": SHELVES,
    "titles": sorted(
        titles.values(), key=lambda t: (-(t.get("wineLifeScore") or 0), t["title"])
    ),
}

out = Path(__file__).resolve().parents[1] / "src/data/wine-collection.json"
out.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
print("titles", len(catalog["titles"]))
print("shelves", len(SHELVES))
print("homepage", sum(1 for t in catalog["titles"] if t.get("homepageFeatured")))
print("top", [(t["title"], t["wineLifeScore"]) for t in catalog["titles"][:5]])
print("sideways", any("sideways" in t["title"].lower() for t in catalog["titles"]))
print("wrote", out)
