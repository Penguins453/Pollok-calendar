#!/usr/bin/env python3

"""Pollok FC Calendar Generator."""

from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup

FIXTURES_URL = "https://www.pollokfc.com/calendar/fixtures-and-results-2026-27/"

@dataclass
class Fixture:
    date: datetime
    match: str
    opponent: str
    home: bool
    result: str
    competition: str
    ground: str
    
def download_page():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    response = requests.get(
        FIXTURES_URL,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")

def extract_fixtures(soup):
    table = soup.find_all("table")[0]

    rows = table.find_all("tr")

    print(f"Found {len(rows)-1} fixtures\n")

    fixtures = []

    for row in rows[1:]:
        cells = row.find_all("td")

        match = cells[1].get_text(strip=True)

        if match.startswith("Pollok v "):
            home = True
            opponent = match.removeprefix("Pollok v ")
        elif match.endswith(" v Pollok"):
            home = False
            opponent = match.removesuffix(" v Pollok")
        else:
            home = False
            opponent = match

        fixture = Fixture(
            date=datetime.fromisoformat(cells[0]["content"]),
            match=match,
            opponent=opponent,
            home=home,
            result=cells[2].get_text(strip=True),
            competition=cells[3].get_text(strip=True),
            ground=cells[4].get_text(strip=True),
        )
        fixtures.append(fixture)

    return fixtures

def main():
    print("⚽ Pollok Calendar Generator")
    print("=" * 40)

    soup = download_page()

    fixtures = extract_fixtures(soup)

    print(f"Extracted {len(fixtures)} fixtures.\n")

    for fixture in fixtures[:5]:
        print(fixture)

if __name__ == "__main__":
    main()