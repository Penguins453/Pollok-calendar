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
GROUND_LOCATIONS = {
    "Newlandsfield Park": "3 Newlandsfield Rd, Glasgow G43 2XU, UK",
    "Winton Park": "Winton Street, Ardrossan KA22 8JG, UK",
    "Netherdale": "Nether Road, Galashiels TD1 3HE, UK",
    "New Western Park": "1 Argyll Avenue, Renfrew PA4 9EF, UK",
    "Islecroft Stadium": "Mill Street, Dalbeattie DG5 4HE, UK",
    "Blairmount Park": "Corsbie Road, Newton Stewart DG8 6NU, UK",
    "Glebe Park": "Trinity Road, Brechin DD9 6BJ, UK",
    "Raydale Park": "18-30 Dominion Rd, Gretna DG16 5AP, UK",
    "Holm Park": "Dock Street, Yoker, Clydebank G81 1LX, UK",
    "Carmuirs Park": "Fairlie Drive, Camelon, Falkirk FK1 4NP, UK",
    "Barrfields Park": "Brisbane Road, Largs KA30 8NP, UK",
    "Keanie Park": "57 Auchenlodment Rd, Elderslie, Johnstone PA5 9PE, UK",
    "Broadwood Stadium": "1 Ardgoil Drive, Cumbernauld G68 9NE, UK",
    "Beechwood Park": "Beechwood Avenue, Auchinleck KA18 2AR, UK",
    "Townhead Park": "148 Townhead Street, Cumnock KA18 1LZ, UK",
    "Cliftonhill": "Main Street, Coatbridge ML5 3RB, UK",
    "Alliance Park": "Alliance Park, Motherwell ML1 3RB, UK",
    "The Albert Bartlett Stadium": "Craigneuk Avenue, Airdrie ML6 8QZ, UK",
    "Bellsdale Park": "Meadowside Terrace, Beith KA15 2AF, UK",
    "Portland Park": "Portland Street, Troon KA10 6QN, UK",
    "Buffs Park": "Pennyburn Road, Kilwinning KA13 6LF, UK",
}
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
        location = GROUND_LOCATIONS.get(fixture.ground, fixture.ground)
        event.add("location", location)
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