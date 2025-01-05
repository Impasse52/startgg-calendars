import requests
import os
from dataclasses import dataclass
from datetime import datetime

from dotenv import load_dotenv
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.calendar import Calendar
from beautiful_date import Jan

from queries import tournaments_by_game_id, ROA2_ID


@dataclass
class Tourney:
    name: str
    location: str
    date: int


def add_event():
    event = Event(
        "test!",
        start=(5 / Jan / 2025)[12:00],
    )

    gc.add_event(event, calendar_id=cal_id)


def retrieve_tourneys():
    query = tournaments_by_game_id(ROA2_ID)
    res = requests.post(
        "https://api.smash.gg/gql/alpha",
        headers={"Authorization": "Bearer " + os.environ.get("STARTGG_TOKEN")},
        json={"query": query},
    )

    tourneys_raw = res.json()["data"]["tournaments"]["nodes"]

    tourneys = []
    for t in tourneys_raw:
        tourneys.append(
            Tourney(
                name=t["name"],
                location=t["venueAddress"],
                date=datetime.utcfromtimestamp(t["startAt"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )
        )

    return tourneys


if __name__ == "__main__":
    load_dotenv()

    gc = GoogleCalendar(
        "linkohprismriver@gmail.com", credentials_path="./.credentials/cred.json"
    )

    cal_id = "15747f46c1e79126631f86d0277685ebc4456425153da2354fade080332f7b58@group.calendar.google.com"
