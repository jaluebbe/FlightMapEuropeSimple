import json
import logging
import shapely
import time
from shapely import speedups
if speedups.available:
    speedups.enable()
from shapely.geometry import shape, Point

logger = logging.getLogger(__name__)

# load GeoJSON file containing sectors
with open('static/flightmap_europe_fir_uir.json') as f:
    firuirs = json.load(f)

def get_fir_uir_by_position(latitude, longitude, flight_level=0):
    # construct point based on lon/lat of aircraft position
    point = Point(longitude, latitude)
    # check each polygon to see if it contains the point
    for feature in firuirs['features']:
        if feature['properties']['MAX_FLIGHT'] < flight_level:
            # altitude too high for this airspace
            continue
        elif feature['properties']['MIN_FLIGHT'] == 0:
            # altitude cannot be too low for this airspace
            pass
        elif feature['properties']['MIN_FLIGHT'] > flight_level:
            # altitude too low for this airspace
            continue
        minx, miny, maxx, maxy = feature['bbox']
        if not (maxy >= latitude >= miny and
                maxx >= longitude >= minx):
            continue
        polygon = shape(feature['geometry'])
        if feature['geometry']['type'] == 'MultiPolygon':
            # If the FIR consists of multiple polygons we need to iterate over
            # each single polygon.
            multipolygon = polygon
            for polygon in multipolygon:
                if polygon.contains(point):
                    return feature['properties']
        elif polygon.contains(point):
            return feature['properties']
    logging.debug('No FIR found at ({}, {}).'.format(latitude, longitude))

if __name__ == '__main__':

    latitude = 52.
    longitude = 7.3
    flight_level = 244.9+0.1
    t_start = time.time()
    data = get_fir_uir_by_position(latitude, longitude, flight_level)
    t_stop = time.time()
    print (t_stop - t_start)
    print (data)
