import geojson
from shapely.geometry import shape

import clip_geojson_precision

file_name = 'icao_regions.json'
with open(file_name) as f:
    data = geojson.load(f)

for _feature in data['features']:
    _properties = _feature['properties']
    _feature['geometry'] = shape(_feature['geometry']).simplify(0.001)

file_name = 'static/icao_regions_simplified.json'
with open(file_name, 'w') as f:
    geojson.dump(data, f)

clip_geojson_precision.clip(file_name)
