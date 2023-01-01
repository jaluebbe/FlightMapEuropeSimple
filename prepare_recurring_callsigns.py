import json
import pandas as pd
import arrow
from traffic.data import opensky

end_date = arrow.utcnow().shift(hours=-1).floor('day')
start_date = end_date.shift(days=-22)

_before = arrow.utcnow()
callsign_occurences = opensky.request(
    "SELECT callsign, MIN(time) as first_seen, MAX(time) AS last_seen FROM "
    "state_vectors_data4 WHERE hour >= {before_hour} and hour < {after_hour} "
    "AND callsign IS NOT NULL AND onground = false AND "
    "NOT (time IS NULL OR icao24 IS NULL OR lat IS NULL OR lon IS NULL OR "
    "velocity IS NULL OR heading IS NULL OR vertrate IS NULL OR baroaltitude "
    "IS NULL OR lastposupdate IS NULL) AND baroaltitude <= 18288 AND "
    "RTRIM(callsign) REGEXP '^[A-Z][A-Z][A-Z][0-9][0-9]?[0-9A-Z]?[0-9A-Z]?$' "
    "group by callsign ",
    start_date.timestamp(),
    end_date.timestamp(),
    date_delta=pd.Timedelta("1 days"),
    columns=["callsign", "first_seen", "last_seen"],
    cached=False,
)
_after = arrow.utcnow()
duration = (_after - _before).total_seconds()

callsign_occurences.callsign = callsign_occurences.callsign.str.rstrip()
callsign_components = callsign_occurences.callsign.str.extract(
    '^([A-Z]{3})0*([1-9][A-Z0-9]*)$', expand=True)
callsign_occurences.callsign = callsign_components[0] + callsign_components[1]
callsign_occurences.dropna(subset=['callsign'], inplace=True)
callsign_occurences = callsign_occurences[
    callsign_occurences.callsign.str.contains(
        '^(?:[A-Z]{3})[1-9](?:(?:[0-9]{0,3})|(?:[0-9]{0,2})'
        '(?:[A-Z])|(?:[0-9]?)(?:[A-Z]{2}))$', regex=True, na=False)]
callsign_occurences = callsign_occurences.groupby(['callsign']).agg({
    'last_seen': 'max', 'first_seen': 'min'})

recurring_callsigns = callsign_occurences[
    callsign_occurences.last_seen - callsign_occurences.first_seen > 86400]

_json_data = json.dumps({
    'start_date': start_date.timestamp(), 'end_date': end_date.timestamp(),
    'recurring_callsigns': recurring_callsigns.index.to_list()})

with open('flightroutes/recurring_callsigns.json', 'w') as f:
    f.write(_json_data+'\n')

print(
    f"Found {len(recurring_callsigns)} recurring callsigns out of "
    f"{len(callsign_occurences)} different callsigns in the time range from "
    f"{start_date.format('YYYY-MM-DD HH:mm:ss')} to "
    f"{end_date.format('YYYY-MM-DD HH:mm:ss')} within {duration:.1f}s.")
