#!/usr/bin/env python
# encoding: utf-8
import csv
import requests
import json
import re
from collections import Counter
import clip_geojson_precision

CSV_URL = 'https://ourairports.com/data/airports.csv'

accepted_icaos = []
ignored_types = []
# possible types: 'balloonport', 'heliport', 'seaplane_base', 'small_airport',
# 'medium_airport', 'large_airport', ''

icao_pattern = re.compile('^[A-Z]{4}$')

with requests.Session() as s:
    download = s.get(CSV_URL)
    download.encoding = 'utf-8'
reader = csv.DictReader(download.text.splitlines(), delimiter=',')
airports = [
    row for row in reader if icao_pattern.match(row['gps_code']) is not None]

icao_count = Counter()
for row in airports:
    icao_count.update([row['gps_code']])
icao_count.subtract(list(icao_count))
duplicate_icaos = set(+icao_count)

_features = []
for row in airports:
    if row['type'] in ignored_types:
        continue
    if not len(row['iata_code']) in (0, 3):
        if row['iata_code'] == '0':
            row['iata_code'] = ''
        else:
            continue
    if row['type'] == 'closed':
        continue
    if len(row['iata_code']) != 3 and not row['gps_code'] in accepted_icaos:
        continue
    if row['scheduled_service'] == 'no':
        continue
    if row['gps_code'] in duplicate_icaos and row['ident'] != row['gps_code']:
        print(
            f"ignoring duplicate entry {row['ident']} for "
            f"{row['gps_code']} / {row['iata_code']}.")
        continue
    _point = {"type": "Point", "coordinates": [float(row['longitude_deg']),
        float(row['latitude_deg'])]}
    _feature = {"geometry": _point, "type": "Feature", "properties": {
        'name': row['name'],
        'icao': row['gps_code'],
        'iata': row['iata_code'],
        'type': row['type']
        }}
    _features.append(_feature)
_collection = {"type": "FeatureCollection", "properties": {},
    "features": _features}

file_name = 'static/airports_static.json'
print(f"writing {len(_features)} airports to {file_name}.")
with open(file_name, 'w') as f:
    json.dump(_collection, f)

clip_geojson_precision.clip(file_name)
