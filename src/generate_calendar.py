#!/usr/bin/env python3

"""Pollok FC Calendar Generator."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import uuid

from icalendar import Calendar, Event

import requests
from bs4 import BeautifulSoup

FIXTURES_URL = "https://www.pollokfc.com/calendar/fixtures-and-results-2026-27/"

@dataclass
class Fixture:
    date: datetime
    match: str
    opponent: str
    home: bool
    result: Optional[str]
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
        time_result = cells[2].get_text(strip=True)

        if ":" in time_result:
            result = None
        else:
            result = time_result
            
        fixture = Fixture(
            date=datetime.fromisoformat(cells[0]["content"]),
            match=match,
            opponent=opponent,
            home=home,
            result=result,
            competition=cells[3].get_text(strip=True),
            ground=cells[4].get_text(strip=True),
        )        
        fixtures.append(fixture)

    return fixtures

def create_calendar(fixtures):
    calendar = Calendar()

    calendar.add("prodid", "-//Pollok FC Calendar//pollokfc.com//")
    calendar.add("version", "2.0")
    calendar.add("X-WR-CALNAME", "Pollok FC Fixtures")

    for fixture in fixtures:
        event = Event()
        uid = uuid.uuid5(uuid.NAMESPACE_URL, f"{fixture.date.date()}-{fixture.match}")
        event.add("uid", f"{uid}@pollokfc.com")
        event.add("summary", f"⚽ {fixture.match.replace(' v ', ' vs ')}")
        start = fixture.date.astimezone(ZoneInfo("Europe/London"))
        start = start.replace(second=0, microsecond=0)
        end = start + timedelta(hours=2)
        event.add("dtstart", start)
        event.add("dtend", end)
        event.add("location", fixture.ground)
        description = f"Competition: {fixture.competition}"
        if fixture.result:
            description += f"\nResult: {fixture.result}"
        description += f"\nSource: {FIXTURES_URL}"

        event.add("description", description)
        calendar.add_component(event)

    return calendar

def main():
    print("⚽ Pollok Calendar Generator")
    print("=" * 40)

    soup = download_page()

    fixtures = extract_fixtures(soup)
    calendar = create_calendar(fixtures)
    with open("data/pollok-fixtures.ics", "wb") as file:
        file.write(calendar.to_ical())

    print(f"Extracted {len(fixtures)} fixtures.\n")

    for fixture in fixtures[:5]:
        print(fixture)

if __name__ == "__main__":
    main()