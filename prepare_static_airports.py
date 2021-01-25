#!/usr/bin/env python
# encoding: utf-8
import csv
import requests
import json
import re
import clip_geojson_precision

CSV_URL = 'https://ourairports.com/data/airports.csv'

ignored_icaos = ['OPDD', 'OP17', 'VO55', 'EK_4']
ignored_types = []
# possible types: 'balloonport', 'heliport', 'seaplane_base', 'small_airport',
# 'medium_airport', 'large_airport', ''

with requests.Session() as s:
    download = s.get(CSV_URL)
    print(download.encoding)
    download.encoding = 'utf-8' 
reader = csv.DictReader(download.text.splitlines(), delimiter=',')
_features = []
for row in reader:
    if row['ident'] in ignored_icaos:
        continue
    if row['type'] in ignored_types:
        continue
    if re.match('^[A-Z]{4}$', row['gps_code']) is None:
        continue
    if not len(row['iata_code']) in (0, 3):
        if row['iata_code'] == '0':
            row['iata_code'] = ''
        else:
            continue
    if row['type'] == 'closed':
        continue
    if len(row['iata_code']) != 3 and row['scheduled_service'] == 'no':
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
with open(file_name, 'w') as f:
    json.dump(_collection, f)

clip_geojson_precision.clip(file_name)
