import json
import re
import pandas as pd
from sqlalchemy import select, func, text
from pyopensky.schema import StateVectorsData4
from pyopensky.trino import Trino

raw_callsign_pattern = re.compile(
    r"^(?P<operator>[A-Z]{3})0*(?P<suffix>[1-9][A-Z0-9]*)$"
)
callsign_pattern = re.compile(
    r"^(?:[A-Z]{3})[1-9](?:(?:[0-9]{0,3})|(?:[0-9]{0,2})"
    "(?:[A-Z])|(?:[0-9]?)(?:[A-Z]{2}))$"
)


def recombine_callsign_components(callsign):
    raw_match = raw_callsign_pattern.match(callsign)
    if not raw_match:
        return
    combined_callsign = raw_match.group("operator") + raw_match.group("suffix")
    if not callsign_pattern.match(combined_callsign):
        return
    return combined_callsign


def fetch_data(trino_connection, start_hour, stop_hour):
    query = (
        select(
            StateVectorsData4.callsign,
            func.min(StateVectorsData4.time).label("first_seen"),
            func.max(StateVectorsData4.time).label("last_seen"),
        )
        .where(
            StateVectorsData4.hour >= start_hour,
            StateVectorsData4.hour < stop_hour,
            StateVectorsData4.callsign.isnot(None),
            StateVectorsData4.onground == False,
            StateVectorsData4.time.isnot(None),
            StateVectorsData4.icao24.isnot(None),
            StateVectorsData4.lat.isnot(None),
            StateVectorsData4.lon.isnot(None),
            StateVectorsData4.velocity.isnot(None),
            StateVectorsData4.heading.isnot(None),
            StateVectorsData4.vertrate.isnot(None),
            StateVectorsData4.baroaltitude.isnot(None),
            StateVectorsData4.lastposupdate.isnot(None),
            StateVectorsData4.baroaltitude <= 18288,
            text(
                "REGEXP_LIKE(RTRIM(callsign), "
                "'^[A-Z][A-Z][A-Z][0-9][0-9]?[0-9A-Z]?[0-9A-Z]?$')"
            ),
        )
        .group_by(StateVectorsData4.callsign)
    )
    return trino_connection.query(query)


stop_ts = pd.Timestamp.utcnow().floor("D") - pd.Timedelta(hours=1)
start_ts = stop_ts - pd.Timedelta(days=22)
stop_hour = stop_ts.floor("1h")
start_hour = start_ts.floor("1h")

_before = pd.Timestamp.utcnow()
trino = Trino()
callsign_occurences = fetch_data(trino, start_hour, stop_hour)
_after = pd.Timestamp.utcnow()
duration = (_after - _before).total_seconds()

callsign_occurences.callsign = callsign_occurences.callsign.str.rstrip()
callsign_occurences["callsign"] = callsign_occurences["callsign"].apply(
    recombine_callsign_components
)
callsign_occurences.dropna(subset=["callsign"], inplace=True)

recurring_callsigns = callsign_occurences[
    callsign_occurences.last_seen - callsign_occurences.first_seen
    > pd.Timedelta(days=1)
]
_json_data = json.dumps(
    {
        "start_date": start_ts.timestamp(),
        "end_date": stop_ts.timestamp(),
        "recurring_callsigns": recurring_callsigns.index.to_list(),
    }
)
with open("flightroutes/recurring_callsigns.json", "w") as f:
    f.write(_json_data + "\n")

print(
    f"Found {len(recurring_callsigns)} recurring callsigns out of "
    f"{len(callsign_occurences)} different callsigns in the time range from "
    f"{start_hour.strftime('%Y-%m-%d %H:%M')} to "
    f"{stop_hour.strftime('%Y-%m-%d %H:%M')} within {duration:.1f}s."
)
