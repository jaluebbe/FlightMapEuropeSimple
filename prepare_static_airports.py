#!/usr/bin/env python
# encoding: utf-8
import csv
import requests
import json
import clip_geojson_precision

CSV_URL = 'https://ourairports.com/data/airports.csv'

ignored_icaos = ['SDZY', 'FAJS', 'KCVC', 'OPDD', 'OP17', 'UA30', 'VO55',]
ignored_types = []
# possible types: 'balloonport', 'heliport', 'seaplane_base', 'small_airport',
# 'medium_airport', 'large_airport', ''

airport_id_replacement = {
    'FLLS': 'FLKK', 'HE13': 'HECP', 'LTGP': 'LTFG', 'SPIM': 'SPJC',
    'SSZW': 'SBPG','UAFM': 'UCFM', 'VAGO': 'VOGO', 'VGZR': 'VHGS',
    'YSCH': 'YCFS'}

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
    if len(row['gps_code']) != 4:
        continue
    if not len(row['iata_code']) in (0, 3):
        continue
    if row['type'] == 'closed':
        continue
    if len(row['ident']) != 4:
        continue
    if len(row['iata_code']) != 3 and row['scheduled_service'] == 'no':
        continue
    if row['ident'].upper() != row['gps_code'].upper():
        if row['type'] == 'small_airport':
            continue
        row['ident'] = airport_id_replacement.get(row['ident'])
        if row['ident'] is None:
            continue
    if row['name'] == 'Airport':
        # useless information to identifiy the Airport
        continue
    if row['ident'] == 'EDDG':
        print(row)
    _point = {"type": "Point", "coordinates": [float(row['longitude_deg']),
        float(row['latitude_deg'])]}
    _feature = {"geometry": _point, "type": "Feature", "properties": {
        'name': row['name'],
        'icao': row['ident'],
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
