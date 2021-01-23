import geojson
from shapely.geometry import shape
import numpy as np

import remove_third_dimension
import clip_geojson_precision

bounds = []

eurocontrol_fir_icaos = [
    'ENOR', 'EHAA', 'LTAA', 'LGGG', 'LECB', 'LFBB', 'LZBB', 'EDWW',
    'LFRR', 'LIBB', 'EBBU', 'LHCC', 'LRBB', 'LUUU', 'EFIN', 'LTBB',
    'UKDV', 'EKDK', 'UKLV', 'EDGG', 'LPPC', 'LJLA', 'EGTT', 'LECM',
    'LMMM', 'LFMM', 'LIMM', 'EDMM', 'GCCC', 'LCCC', 'LFFF', 'LKAA',
    'LFEE', 'EVRR', 'LIRR', 'LQSB', 'EGPX', 'EISN', 'ESAA', 'LBSR',
    'LSAS', 'EETT', 'UGGG', 'LAAA', 'EYVL', 'EPWW', 'LOVV', 'UDDD',
    'LDZO', 'LWSS', 'LYBA', 'UKFV', 'UKOV', 'UKBV', 'ENOB', 'EGGX',
    'LPPO', 'EDUU', 'EDVV', 'EBUR', 'UKBU']

file_name = 'fir_uir_nm.json'
with open(file_name) as f:
    data = geojson.load(f)

for firuir in data['features']:
    properties = firuir['properties']
    if firuir['properties']['AV_NAME'] == 'CANARIS UIR':
        firuir['properties']['AV_NAME'] = 'CANARIAS UIR'
    if firuir['properties']['AV_AIRSPAC'] == 'EFINFIR':
        firuir['properties']['AV_NAME'] = 'HELSINKI FIR'
        firuir['properties']['UL_VISIBLE'] = 'both'
        firuir['properties']['MAX_FLIGHT'] = 999
    elif firuir['properties']['AV_AIRSPAC'] == 'ENORFIR':
        firuir['properties']['AV_NAME'] = 'POLARIS FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'EDMMFIR':
        firuir['properties']['AV_NAME'] = 'MUENCHEN FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'LDZOFIR':
        firuir['properties']['AV_NAME'] = 'ZAGREB FIR/UIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'LGGGUIR':
        firuir['properties']['AV_NAME'] = 'HELLAS UIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'LPPOFIR':
        firuir['properties']['AV_NAME'] = 'SANTA MARIA OCEANIC FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'LRBBFIR':
        firuir['properties']['AV_NAME'] = 'BUCURESTI FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'UKBVUIR':
        firuir['properties']['AV_NAME'] = 'KYIV UIR'
        firuir['properties']['AV_AIRSPAC'] = 'UKBUUIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'UKBVFIR':
        firuir['properties']['AV_NAME'] = 'KYIV FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'UKDVFIR':
        firuir['properties']['AV_NAME'] = 'DNIPRO FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'UKLVFIR':
        firuir['properties']['AV_NAME'] = 'LVIV FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'UKOVFIR':
        firuir['properties']['AV_NAME'] = 'ODESA FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'EKDKFIR':
        firuir['properties']['AV_NAME'] = 'KOEBENHAVN FIR'
    elif firuir['properties']['OBJECTID'] == 24929:
        firuir['properties']['MIN_FLIGHT'] = 0
        firuir['properties']['MAX_FLIGHT'] = 660  # TBILISI FIR
        firuir['properties']['AV_NAME'] = 'TBILISI FIR'

    polygon = shape(firuir['geometry'])
    firuir['bbox'] = list(polygon.bounds)
    if properties['MIN_FLIGHT'] == 0 and properties['MAX_FLIGHT'] > 450:
        properties['UL_VISIBLE'] = 'both'
    elif properties['MIN_FLIGHT'] == 0:
        properties['UL_VISIBLE'] = 'lower'
    elif properties['MAX_FLIGHT'] > 450:
        properties['UL_VISIBLE'] = 'upper'

    if firuir['properties']['AV_AIRSPAC'][:4] in eurocontrol_fir_icaos:
        bounds.append(polygon.bounds)

min_bounds = np.min(bounds, axis=0)
max_bounds = np.max(bounds, axis=0)
ec_bounds = (min_bounds[0], min_bounds[1], max_bounds[2], max_bounds[3])
print(f'Eurocontrol area bounds: lon_ll={ec_bounds[0]}, '
    f'lat_ll={ec_bounds[1]}, lon_ur={ec_bounds[2]}, lat_ur={ec_bounds[3]}')

ignored_objectids = [24764, 24995, 24989, 24944, 25042, 24928, 24951, 24961,]
data['features'][:] = [d for d in data['features'] if
    d['properties']['OBJECTID'] not in ignored_objectids]

for feature in data['features']:
    del feature['properties']['SHAPE_AREA']
    del feature['properties']['OBJECTID']
    del feature['properties']['SHAPE_LEN']
    del feature['properties']['AV_ICAO_ST']
    del feature['properties']['AC_ID']

data['features'][:] = [d for d in data['features'] if
    d['properties']['AV_AIRSPAC'][:4] in eurocontrol_fir_icaos]

for feature in data['features']:
    feature['geometry'] = remove_third_dimension.remove_third_dimension(
        shape(feature['geometry']))

file_name = 'static/flightmap_europe_fir_uir_ec_only.json'
with open(file_name, 'w') as f:
    geojson.dump(data, f)

clip_geojson_precision.clip(file_name)
