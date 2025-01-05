import time
import requests
import os
from dataclasses import dataclass
from datetime import datetime
import pytz

from tqdm import tqdm
from dotenv import load_dotenv
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.calendar import Calendar

from queries import tournaments_by_game_id, ROA2_ID


@dataclass
class Tourney:
    name: str
    location: str
    date: int
    timezone: str
    url: str


def retrieve_tourneys(game_id: str, online: bool, upcoming: bool):
    query = tournaments_by_game_id(game_id, online, upcoming)
    res = requests.post(
        "https://api.smash.gg/gql/alpha",
        headers={"Authorization": "Bearer " + os.environ.get("STARTGG_TOKEN")},
        json={"query": query},
    )

    tourneys_raw = res.json()["data"]["tournaments"]["nodes"]

    tourneys = []
    for t in tourneys_raw:
        location = "Online" if not t["venueAddress"] else t["venueAddress"]

        tourneys.append(
            Tourney(
                name=t["name"],
                location=location,
                date=t["startAt"],
                url=t["url"],
                timezone=t["timezone"],
            )
        )

    return tourneys


def init_calendar(gc, email_addr: str, timezone: str):
    # TODO: properly handle calendars: only create if needed
    new_cal = Calendar(
        summary="RoAII Tournaments",
        description="Offline and online Rivals of Aether II tournaments, fetched directly from start.gg",
        timezone=timezone,
    )

    created_calendar = gc.add_calendar(new_cal)

    return created_calendar.id


if __name__ == "__main__":
    load_dotenv()

    email_addr = "linkohprismriver@gmail.com"
    timezone = "Europe/Rome"

    # setup gcsa
    gc = GoogleCalendar(email_addr, credentials_path="./.credentials/cred.json")
    cal_id = init_calendar(gc, email_addr, timezone)

    # setup target timezone
    target_tz = pytz.timezone(timezone)

    # retrieve online and offline tournaments
    tourneys = retrieve_tourneys(ROA2_ID, online=False, upcoming=True)
    tourneys.extend(retrieve_tourneys(ROA2_ID, online=True, upcoming=True))

    for i, t in enumerate(tqdm(tourneys)):
        # TODO: properly handle rate limiting
        if i % 50 == 0 and i > 0:
            print("Sleeping for 30 sec to prevent rate limiting...")
            time.sleep(30)

        # handle timezone conversion
        if t.timezone:
            source_tz = pytz.timezone(t.timezone)
            start = source_tz.localize(datetime.fromtimestamp(t.date))
            start = start.astimezone(target_tz)
        else:
            start = datetime.fromtimestamp(t.date)

        event = Event(
            t.name,
            start=start,
            location=t.location,
            description=f"https://start.gg{t.url}/details",
        )
        gc.add_event(event, calendar_id=cal_id)
