import geojson
import shapely
import requests
import copy
from shapely.geometry import shape
from shapely.geometry import Polygon
from shapely.ops import cascaded_union

import remove_third_dimension
import clip_geojson_precision

file_name = 'static/flightmap_europe_fir_uir_ec_only.json'
with open(file_name) as f:
    ec_data = geojson.load(f)

file_name = 'fir_uir_nm.json'
with open(file_name) as f:
    nm_data = geojson.load(f)

file_name = 'fir_uir_ead.json'
with open(file_name) as f:
    ead_data = geojson.load(f)

uri = ('https://opendata.arcgis.com/'
    'datasets/67885972e4e940b2aa6d74024901c561_0.geojson')
faa_airspace_data = requests.get(uri).json()

ignored_objectids = [24764, 24995, 24989, 24944, 25042, 24928, 24951, 24961,]

total_bounds = Polygon([(-180, -90), (180, -90), (180, 90),(-180, 90)])

icao_south_hole = Polygon([[-120, 5], [-104.5, 10], [-92, 1.416666031],
    [-92, -3.4], [-90, -3.4], [-90, -15], [-120, -15], [-120, 5]])

uhhh_mask = Polygon(
    [[130.57, 42.52], [130.62, 42.42], [130.67, 42.33], [130.70, 42.29],
    [130.88, 42.15], [131.52, 41.67], [135.93, 40.5], [136, 40.55],
    [140, 45.75], [142, 45.75], [145.67, 44.5], [145.32, 44.05], [145.37, 43.5],
    [145.58, 43.4], [145.81, 43.43], [145.83, 43.38], [145.83, 43.33],
    [146.83, 43], [150, 45], [150, 54.87], [130.57, 42.52]])

afghanistan_pakistan_mask = Polygon(
    [[59.79, 37.32], [61.33, 24.66], [61.33, 23.5], [68.38, 23.5],
    [71.51, 23.85], [80.2, 36.15], [70.6, 38.93], [59.79, 37.32]])

car_shape = Polygon([[-120.84, 40], [-120, 5], [-104.5, 10], [-92, 1.416666031],
    [-92.0, -0.5], [-89.8, -0.5], [-58.8, -0.5], [-58.8, 40], [-120.84, 40]])

nam_polygons = []
afi_polygons = []
russia_polygons = []
asia_polygons = []
mid_polygons =[]
sam_polygons = []
kzny_polygons = []
uaaa_polygons = []
utaa_polygons = []

for _feature in faa_airspace_data['features']:
    if _feature['properties']['NAME'] == 'ANCHORAGE ARCTIC FIR':
        (minx, miny, maxx, maxy) = shape(_feature['geometry']).bounds
        north_of_alaska = Polygon([[maxx+1, miny], [minx, miny], [minx, maxy],
            [maxx+1, maxy]])
        nam_polygons.append(north_of_alaska)
    if (_feature['properties']['COUNTRY'] == 'United States' and
        _feature['properties']['TYPE_CODE'] == 'ARTCC' and
        _feature['properties']['LOCAL_TYPE'] == 'ARTCC_L' or
        _feature['properties']['TYPE_CODE'] == 'FIR' and
        _feature['properties']['IDENT'] in ['PAZA', 'CZVR', 'CZWG', 'CZYZ',
        'CZQM', 'CZUL']):
        nam_polygons.append(shape(_feature['geometry']))
    if (_feature['properties']['TYPE_CODE'] == 'FIR' and
        _feature['properties']['IDENT'] in ['UHMM',]):
        russia_polygons.append(shape(_feature['geometry']))
    if (_feature['properties']['TYPE_CODE'] == 'FIR' and
        _feature['properties']['IDENT'] in ['KZAK', 'NZZO', 'RJJJ',
        'NFFF', 'RPHI', 'WAAZ', 'ANAU', 'AGGG']
        or _feature['properties']['TYPE_CODE'] == 'OCA' and
        _feature['properties']['IDENT'] in ['NTTT',]):
        asia_polygons.append(shape(_feature['geometry']))
    if (_feature['properties']['TYPE_CODE'] == 'FIR' and
        _feature['properties']['IDENT'] in ['KZWY']):
        _polygon = shape(_feature['geometry'])
        kzny_polygons.append(_polygon)
nam_shape = cascaded_union(nam_polygons)
kzny_shape = cascaded_union(kzny_polygons)
# closing gaps between USA and Canada
nam_shape = nam_shape.union(Polygon(
    [[-117.9, 35.3], [-100.9, 31.8], [-90.1, 30], [-79.8, 31.7], [-75, 35.5],
    [-72, 41.2], [-71.1, 42.4], [-63.6, 44.7], [-66.0, 50.3], [-97.2, 50],
    [-141.5, 69.8], [-142, 60], [-135.3, 57], [-123.9, 48.8], [-122.4, 37.8]]
    ))

ec_nm_neighbour_icaos = [
    'CZQX', 'DAAA', 'BGGL', 'UMMV', 'OLBB', 'LLLL', 'GMMM', 'UCFF', 'UMKK',
    'UTDD', 'DTTC', 'UTTT', 'BIRD', 'GOOO', 'UBBA', 'GVSC', 'GLRB']

for firuir in nm_data['features']:
    if firuir['properties']['OBJECTID'] in ignored_objectids:
        continue
    properties = firuir['properties']
    if firuir['properties']['AV_AIRSPAC'] == 'BGGLFIR':
        firuir['properties']['AV_NAME'] = 'NUUK FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'UTAKFIR':
        firuir['properties']['MAX_FLIGHT'] = 490
    elif firuir['properties']['AV_AIRSPAC'] == 'DAAAFIR':
        firuir['properties']['AV_NAME'] = 'ALGER FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'UTDDFIR':
        firuir['properties']['AV_NAME'] = 'DUSHANBE FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'UTTTFIR':
        firuir['properties']['AV_NAME'] = 'UZBEKISTAN MERGED FIRS'
    elif firuir['properties']['AV_AIRSPAC'] == 'HAAAFIR':
        firuir['properties']['AV_NAME'] = 'ADDIS ABEBA FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'HUECFIR':
        firuir['properties']['AV_NAME'] = 'ENTEBBE FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'HHAAFIR':
        firuir['properties']['AV_NAME'] = 'ASMARA FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'HCSMFIR':
        firuir['properties']['AV_NAME'] = 'MOGADISHU FIR/UIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'DNKKFIR':
        firuir['properties']['AV_NAME'] = 'KANO FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'HTDCFIR':
        firuir['properties']['AV_NAME'] = 'DAR-ES-SALAAM FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'HKNAFIR':
        firuir['properties']['AV_NAME'] = 'NAIROBI FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'CZZZFIR':
        firuir['properties']['AV_NAME'] = 'GANDER OCEANIC FIR'
        firuir['properties']['AV_AIRSPAC'] = 'CZQXFIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'URRVFIR':
        firuir['properties']['AV_NAME'] = 'ROSTOV-NA-DONU FIR'
    elif firuir['properties']['AV_AIRSPAC'] == 'OLBBFIR':
        olbbuir = copy.deepcopy(firuir)
        firuir['properties']['MAX_FLIGHT'] = 195
        firuir['properties']['UL_VISIBLE'] = 'lower'
        olbbuir['properties']['MIN_FLIGHT'] = 195
        olbbuir['properties']['MAX_FLIGHT'] = 460
        olbbuir['properties']['AV_NAME'] = 'BEIRUT UIR'
        olbbuir['properties']['AV_AIRSPAC'] = 'OLBBUIR'
        olbbuir['properties']['UL_VISIBLE'] = 'upper'
    elif firuir['properties']['AV_AIRSPAC'] == 'GVSCFIR':
        gvscuir = copy.deepcopy(firuir)
        firuir['properties']['MAX_FLIGHT'] = 245
        firuir['properties']['UL_VISIBLE'] = 'lower'
        gvscuir['properties']['MIN_FLIGHT'] = 245
        gvscuir['properties']['MAX_FLIGHT'] = 999
        gvscuir['properties']['AV_NAME'] = 'SAL OCEANIC UIR'
        gvscuir['properties']['AV_AIRSPAC'] = 'GVSCUIR'
        gvscuir['properties']['UL_VISIBLE'] = 'upper'
    elif firuir['properties']['AV_AIRSPAC'] == 'GOOOFIR':
        if firuir['properties']['MIN_FLIGHT'] ==0:
            firuir['properties']['AV_NAME'] = 'DAKAR FIR'
        else:
            firuir['properties']['AV_NAME'] = 'DAKAR UIR'
            firuir['properties']['AV_AIRSPAC'] = 'GOOOUIR'
    elif firuir['properties']['OBJECTID'] == 24945:
        firuir['geometry']['coordinates'].pop()
        firuir['properties']['AV_NAME'] = 'REYKJAVIK FIR'
        firuir['properties']['MIN_FLIGHT'] = 0
        firuir['properties']['AV_AIRSPAC'] = 'BIRDFIR'
        firuir['properties']['UL_VISIBLE'] = 'both'
    elif firuir['properties']['OBJECTID'] == 24763:
        firuir['properties']['MAX_FLIGHT'] = 660  # MINSK FIR
        firuir['properties']['UL_VISIBLE'] = 'both'

    polygon = shape(firuir['geometry'])
    firuir['bbox'] = list(polygon.bounds)
    if properties['MIN_FLIGHT'] == 0 and properties['MAX_FLIGHT'] > 450:
        properties['UL_VISIBLE'] = 'both'
    elif properties['MIN_FLIGHT'] == 0:
        properties['UL_VISIBLE'] = 'lower'
    elif properties['MAX_FLIGHT'] > 450:
        properties['UL_VISIBLE'] = 'upper'

    del firuir['properties']['SHAPE_AREA']
    del firuir['properties']['OBJECTID']
    del firuir['properties']['SHAPE_LEN']
    del firuir['properties']['AV_ICAO_ST']
    del firuir['properties']['AC_ID']
    if firuir['properties']['AV_AIRSPAC'][:4] in ec_nm_neighbour_icaos:
        ec_data['features'].append(firuir)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['CCCC',]:
        _polygon = shape(firuir['geometry'])
        nam_shape = nam_shape.union(_polygon)
    elif firuir['properties']['AV_AIRSPAC'][:4] in ['CZQX']:
        _polygon = shape(firuir['geometry'])
        nam_shape = nam_shape.difference(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['UAAA', 'UACC', 'UATT',
        'UAII']:
        _polygon = shape(firuir['geometry'])
        uaaa_polygons.append(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['UTAK', 'UTAA']:
        _polygon = shape(firuir['geometry'])
        utaa_polygons.append(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['ULMM', 'ULLL', 'UUWV',
        'UWWW', 'URRV', 'USCM', 'UUUU']:
        _polygon = shape(firuir['geometry'])
        russia_polygons.append(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['FAAA', 'DGAC', 'HHAA',
        'HCSM', 'DRRR', 'DNKK', 'HKNA', 'HTDC', 'HRYR', 'HBBA', 'HUEC', 'HAAA']:
        _polygon = shape(firuir['geometry'])
        afi_polygons.append(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['KZWY']:
        _polygon = shape(firuir['geometry'])
        kzny_shape = kzny_shape.union(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['CZQX']:
        _polygon = shape(firuir['geometry'])
        kzny_shape = kzny_shape.difference(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['YYYY', 'VVVV', 'ZYYY',
        'RJJJ', 'OOOO',]:
        _polygon = shape(firuir['geometry'])
        asia_polygons.append(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['OSTT', 'OJAC', 'HECC',
        'HLLL', 'HSSS', 'OYSC', 'OKAC', 'OBBB', 'OMAE', 'OOMM', 'OOOO']:
        _polygon = shape(firuir['geometry'])
        mid_polygons.append(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['SBBB',]:
        _polygon = shape(firuir['geometry'])
        sam_polygons.append(_polygon)

mid_shape = cascaded_union(mid_polygons)
mid_shape = mid_shape.difference(afghanistan_pakistan_mask)
sam_shape = cascaded_union(sam_polygons)
uaaa_shape = cascaded_union(uaaa_polygons)
utaa_shape = cascaded_union(utaa_polygons)
russia_shape = cascaded_union(russia_polygons)
russia_shape = russia_shape.intersection(total_bounds)
asia_shape = cascaded_union(asia_polygons)

for firuir in ead_data['features']:
    if firuir['properties']['IDENT'] in ['PAZA',
        ]:
        _polygon = shape(firuir['geometry'])
        nam_shape = nam_shape.union(_polygon)
        if firuir['properties']['IDENT'] == 'PAZA':
            nam_shape = nam_shape.union(shapely.affinity.translate(
                shape(firuir['geometry']), xoff=-360))
    if firuir['properties']['IDENT'] in ['TTZP', 'SOOO', 'SMPM', 'SVZM', 'MPZL',
            'SKEC', 'SKED',]:
        _polygon = shape(firuir['geometry'])
        sam_shape = sam_shape.union(_polygon)
    if firuir['properties']['IDENT'] in ['MHTG', 'NTTT',]:
        _polygon = shape(firuir['geometry'])
        sam_shape = sam_shape.difference(_polygon)
    if firuir['properties']['IDENT'] in ['ZKKP', 'RJJJ', 'ZWUQ', 'YBBB', 'YMMM',
            'AGGG', 'AYPM', 'ANAU', 'WAAF', 'NTTT', 'NZZO', 'NFFF',]:
        _polygon = shape(firuir['geometry'])
        asia_shape = asia_shape.union(_polygon)
    if firuir['properties']['IDENT'] in ['MMFR',]:
        _polygon = shape(firuir['geometry'])
        car_shape = car_shape.union(_polygon)
    if firuir['properties']['IDENT'] in ['NTTT',]:
        _polygon = shape(firuir['geometry'])
        car_shape = car_shape.difference(_polygon)
# fill residual gaps
sam_shape = sam_shape.union(Polygon(
    [[-90, -15], [-135, -15], [-135, -89], [-90, -89]]))
asia_shape = asia_shape.union(Polygon(
    [[180, -45.5], [180, 18.1], [107.6, 15.5], [101.8, -9.1]]))
asia_shape = asia_shape.union(Polygon(
    [[-180, -37.4], [-166.6, -37.4], [-166.6, 4.2], [-180, 4.2]]))

for _feature in faa_airspace_data['features']:
    if _feature['properties']['IDENT'] in ['RJJJ', 'KZMA', 'KZHU', 'KZWY',
        'KZAK',]:
        nam_shape = nam_shape.difference(shape(_feature['geometry']))
    if _feature['properties']['IDENT'] in ['NZZO', 'NTTT',]:
        _polygon = shape(_feature['geometry'])
        sam_shape = sam_shape.difference(_polygon)
    if _feature['properties']['IDENT'] == 'ZAN' and _feature['properties'][
        'LOCAL_TYPE'] == 'ARTCC_L' or _feature['properties']['IDENT'] in [
        'PAZA', 'KZAK']:
        _polygon = shape(_feature['geometry'])
        russia_shape = russia_shape.difference(_polygon)
    if _feature['properties']['IDENT'] in ['KZAK', 'NTTT',]:
        _polygon = shape(_feature['geometry'])
        car_shape = car_shape.difference(_polygon)

for firuir in nm_data['features']:
    if firuir['properties']['AV_AIRSPAC'][:4] in ['BGGL', 'CZZZ', 'LPPO']:
        _polygon = shape(firuir['geometry'])
        nam_shape = nam_shape.difference(_polygon)
    if firuir['properties']['AV_AIRSPAC'][:4] in ['OIIX', 'OMAE', 'ORBB']:
        # add shapes after application of the afghanistan_pakistan_mask
        _polygon = shape(firuir['geometry'])
        mid_shape = mid_shape.union(_polygon)

sam_shape = sam_shape.difference(icao_south_hole)
car_shape = car_shape.difference(nam_shape)

# remove small parts of KZNY between KZWY and NAM shapes
kzny_shape = kzny_shape.difference(Polygon([[-77.8, 26.8], [-69.6, 26.8],
    [-69.6, 35.5], [-77.8, 35.5], [-77.8, 26.8]]))
kzny_shape = kzny_shape.difference(car_shape)
nam_shape = nam_shape.difference(kzny_shape)

sam_shape = sam_shape.union(Polygon([[-78.4, 7.3], [-76.8, 6.9], [-77.3, 9.1]]))
car_shape = car_shape.difference(sam_shape)

russia_shape = russia_shape.union(uhhh_mask)
for firuir in ead_data['features']:
    if firuir['properties']['IDENT'] in ['CZEG', 'RJJJ', 'ZKKP',]:
        russia_shape = russia_shape.difference(shape(firuir['geometry']))

russia_shape = russia_shape.union(Polygon(
    [[-168.9, 65.9], [-180, 60.5], [-180, 59], [-168.7, 64.8]]))
russia_shape = russia_shape.intersection(total_bounds)
russia_shape = russia_shape.difference(nam_shape)

asia_shape = asia_shape.difference(russia_shape)
russia_shape = russia_shape.union(Polygon(
    [[158.8, 50.1], [156.9, 49.4], [157.3, 48.9], [159, 50]]))
russia_shape = russia_shape.difference(asia_shape)
asia_shape = asia_shape.difference(nam_shape)
nam_shape = nam_shape.union(Polygon(
    [[160, 48.6], [162.8, 45.4], [163.4, 45.5], [160.5, 48.8]]))
nam_shape = nam_shape.difference(asia_shape)
asia_shape = asia_shape.difference(mid_shape)
asia_shape = asia_shape.difference(uaaa_shape)
asia_shape = asia_shape.difference(utaa_shape)
nam_shape = nam_shape.intersection(total_bounds)

afi_shape = cascaded_union(afi_polygons)
afi_region = _feature = {
    "properties": {
        "AV_NAME": "AFRICA-INDIAN OCEAN (AFI) REGION",
        "AV_AIRSPAC": "FFFFFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": afi_shape,
    "bbox": afi_shape.bounds
}
nam_region = _feature = {
    "properties": {
        "AV_NAME": "NORTH AMERICAN (NAM) REGION",
        "AV_AIRSPAC": "CCCCFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": nam_shape,
    "bbox": nam_shape.bounds
}
car_region = _feature = {
    "properties": {
        "AV_NAME": "CARIBBEAN (CAR) REGION",
        "AV_AIRSPAC": "MMMMFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": car_shape,
    "bbox": car_shape.bounds
}
uaaa_region = _feature = {
    "properties": {
        "AV_NAME": "KAZAHKSTAN MERGED FIRS",
        "AV_AIRSPAC": "UAAAFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": uaaa_shape,
    "bbox": uaaa_shape.bounds
}
utaa_region = _feature = {
    "properties": {
        "AV_NAME": "TURKMENISTAN MERGED FIRS",
        "AV_AIRSPAC": "UTAAFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": utaa_shape,
    "bbox": utaa_shape.bounds
}
russia_region = _feature = {
    "properties": {
        "AV_NAME": "RUSSIA MERGED FIRS",
        "AV_AIRSPAC": "UUUUFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": russia_shape,
    "bbox": russia_shape.bounds
}
asia_region = _feature = {
    "properties": {
        "AV_NAME": "ASIA/PACIFIC (ASIA/PAC) REGION",
        "AV_AIRSPAC": "YYYYFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": asia_shape,
    "bbox": asia_shape.bounds
}
mid_region = _feature = {
    "properties": {
        "AV_NAME": "MIDDLE EAST (MID) REGION",
        "AV_AIRSPAC": "OOOOFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": mid_shape,
    "bbox": mid_shape.bounds
}
kzny_region = _feature = {
    "properties": {
        "AV_NAME": "NEW YORK OCEANIC EAST FIR",
        "AV_AIRSPAC": "KZWYFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": kzny_shape,
    "bbox": kzny_shape.bounds
}
sam_region = _feature = {
    "properties": {
        "AV_NAME": "SOUTH AMERICAN (SAM) REGION",
        "AV_AIRSPAC": "SSSSFIR",
        "MIN_FLIGHT": 0, "MAX_FLIGHT": 999, "UL_VISIBLE": "both"},
    "type": "Feature",
    "geometry": sam_shape,
    "bbox": sam_shape.bounds
}
polygon = shape(olbbuir['geometry'])
olbbuir['bbox'] = list(polygon.bounds)
ec_data['features'].extend([
    uaaa_region, utaa_region, gvscuir, olbbuir, afi_region, mid_region,
    sam_region, russia_region, kzny_region, car_region, nam_region, asia_region,
    ])

for feature in ec_data['features']:
    feature['geometry'] = remove_third_dimension.remove_third_dimension(
        shape(feature['geometry']))

file_name = 'static/flightmap_europe_fir_uir.json'
with open(file_name, 'w') as f:
    geojson.dump(ec_data, f)

clip_geojson_precision.clip(file_name)
