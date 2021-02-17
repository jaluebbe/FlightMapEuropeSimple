import time
import json
import re
import sqlite3
import math
from collections import namedtuple
import logging
logger = logging.getLogger(__name__)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logger.warning('%r  %2.2f ms' %
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed


directory = "flightroutes/"

# The following lists of airline alliances including affiliate members are
# based on several public non-authoritative sources and may be incorrect,
# incomplete or outdated.
skyteam_icaos = [
    'CYL', 'CSH', 'CXA', 'HVN', 'ROT', 'SVA', 'MEA', 'KAL', 'KLM', 'KQA', 'GIA',
    'DAL', 'EDV', 'CPZ', 'GJS', 'RPA', 'SKW', 'CSA', 'CES', 'CAL', 'AZA', 'AFR',
    'HOP', 'AEA', 'AMX', 'SLI', 'ARG', 'AUT', 'AFL', 'KLC']
star_alliance_icaos = [
    'SWR', 'NIS', 'GLG', 'THY', 'CLH', 'LRC', 'LLR', 'EVS', 'ASH', 'ROU', 'TAI',
    'SKV', 'GUG', 'OAL', 'GGN', 'EVA', 'BEL', 'UCA', 'CMP', 'CTN', 'JZA', 'AMU',
    'ANA', 'AWI', 'SAS', 'THA', 'AIC', 'UAL', 'LNK', 'AAR', 'AKX', 'SAA', 'AJX',
    'RLK', 'ANZ', 'EXY', 'CCA', 'AEE', 'AUA', 'AVA', 'TPU', 'EST', 'SKW', 'TAP',
    'CSZ', 'ASQ', 'MSR', 'LOF', 'ACA', 'ETH', 'RPA', 'DLH', 'SIA', 'LOT', 'GJS',
    'ISV', 'NZM']
oneworld_icaos = [
    'ENY', 'QTR', 'ASH', 'TAM', 'QFA', 'ARE', 'CPZ', 'JIA', 'CFE', 'JAL', 'FCM',
    'BAW', 'MAS', 'JLJ', 'AAL', 'QJE', 'ANE', 'GLP', 'JTA', 'FJI', 'IBE', 'FIN',
    'DSM', 'SUS', 'IBS', 'SHT', 'SBI', 'ALK', 'LNE', 'RJA', 'QLK', 'SKW', 'LTM',
    'PDT', 'RPA', 'CAW', 'NWK', 'LAN', 'LPE', 'CPA', 'HDA']


def get_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    deg_rad = 2 * math.pi / 360
    distance = (
        6.370e6 * math.acos(math.sin(lat1 * deg_rad) * math.sin(lat2 * deg_rad)
        + math.cos(lat1 * deg_rad) * math.cos(lat2 * deg_rad)
                            * math.cos((lon2 - lon1) * deg_rad)))
    return distance


def cos_deg(angle: float) -> float:
    return math.cos(angle * math.pi / 180)


def namedtuple_factory(cursor, row):
    """
    Usage:
    con.row_factory = namedtuple_factory
    """
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


def get_geojson_airports():
    try:
        connection = sqlite3.connect("file:" + directory +
            "StandingData.sqb?mode=ro", uri=True)
        connection.row_factory = namedtuple_factory
        connection.create_function("REGEXP", 2, regexp)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT Name, Icao, Iata, ROUND(Latitude, 6) AS Latitude, "
            "ROUND(Longitude, 6) AS Longitude, Destinations FROM Airport "
            "WHERE ICAO REGEXP '^[A-Z]{4}$' AND (LENGTH(IATA)=3 OR "
            "Destinations + Origins > 0)")
        result = cursor.fetchall()
        connection.close()
    except sqlite3.DatabaseError:
        logger.exception('get_geojson_airports()')
        return None
    _features = []
    for row in result:
        _point = {"type": "Point", "coordinates": [row.Longitude, row.Latitude]}
        _feature = {"geometry": _point, "type": "Feature", "properties": {
            'name': row.Name, 'icao': row.Icao, 'iata': row.Iata,
            'known_destinations': row.Destinations}}
        _features.append(_feature)
    _collection = {"type": "FeatureCollection", "properties": {
        "utc": time.time()}, "features": _features}
    airports_data = _collection
    return airports_data


def get_airport_position(airport_icao):
    try:
        connection = sqlite3.connect("file:" + directory +
            "StandingData.sqb?mode=ro", uri=True)
        connection.row_factory = namedtuple_factory
        cursor = connection.cursor()
        cursor.execute(
            "SELECT Name, Icao, Iata, ROUND(Latitude, 6) AS Latitude, "
            "ROUND(Longitude, 6) AS Longitude FROM Airport "
            "WHERE Icao = ?", (airport_icao,))
        result = cursor.fetchone()
        connection.close()
    except sqlite3.DatabaseError:
        logger.exception('get_airport_position({})'.format(airport_icao))
        return None
    return result


def get_airport_positions():
    try:
        connection = sqlite3.connect("file:" + directory +
            "StandingData.sqb?mode=ro", uri=True)
        connection.row_factory = namedtuple_factory
        connection.create_function("REGEXP", 2, regexp)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT Icao, ROUND(Latitude, 6) AS Latitude,
            ROUND(Longitude, 6) AS Longitude FROM Airport
            WHERE Icao REGEXP '^[A-Z]{4}$'
            OR Destinations > 0
            OR Origins > 0
            """)
        result = cursor.fetchall()
        connection.close()
    except sqlite3.DatabaseError:
        logger.exception('get_airport_positions()')
        return None
    airport_positions = {}
    for row in result:
        airport_positions[row.Icao] = [row.Longitude, row.Latitude]
    return airport_positions


def get_distinct_routes_by_airport(airport_icao):
    try:
        connection = sqlite3.connect("file:" + directory +
            "StandingData.sqb?mode=ro", uri=True)
        connection.row_factory = namedtuple_factory
        cursor = connection.cursor()
        cursor.execute(
           "SELECT DISTINCT Origin || '-' || Destination AS DirectRoute "
           "FROM FlightLegs WHERE Origin = ?", (airport_icao,))
        result = cursor.fetchall()
        connection.close()
    except sqlite3.DatabaseError:
        logger.exception(
            'get_distinct_routes_by_airport({})'.format(airport_icao))
        return None
    if result is not None:
        return [row.DirectRoute for row in result]


def get_distinct_routes_by_airline(operator_icao):
    try:
        connection = sqlite3.connect("file:" + directory +
            "StandingData.sqb?mode=ro", uri=True)
        connection.row_factory = namedtuple_factory
        cursor = connection.cursor()
        cursor.execute(
            "SELECT DISTINCT Origin || '-' || Destination AS DirectRoute, "
            "o.Name AS OperatorName, o.Iata AS OperatorIata "
            "FROM FlightLegs, Operator o "
            "WHERE OperatorIcao = ? AND o.Icao=OperatorIcao", (operator_icao,))
        result = cursor.fetchall()
        connection.close()
    except sqlite3.DatabaseError:
        logger.exception(
            'get_distinct_routes_by_airline({})'.format(operator_icao))
        return None
    if result is not None and len(result) > 0:
        return {
            'routes': [row.DirectRoute for row in result],
            'operator_icao': operator_icao,
            'operator_iata': result[0].OperatorIata,
            'operator_name': result[0].OperatorName}


def get_route_by_callsign(callsign):
    try:
        connection = sqlite3.connect("file:" + directory +
            "StandingData.sqb?mode=ro", uri=True)
        connection.row_factory = namedtuple_factory
        cursor = connection.cursor()
        cursor.execute(
            "SELECT Callsign, OperatorIcao, OperatorIata, OperatorName, Route "
            "FROM FlightRoute WHERE Callsign = ?", (callsign,))
        result = cursor.fetchone()
        connection.close()
    except sqlite3.DatabaseError:
        logger.exception('get_route_by_callsign({})'.format(callsign))
        return None
    return result


def get_geojson_callsign(callsign):
    _flight = get_route_by_callsign(callsign)
    if _flight is None:
        return '{}'
    _route_items = _flight.Route.split('-')
    _airport_infos = []
    _line_coordinates = []
    for _icao in _route_items:
        _info = get_airport_position(_icao)
        if _info is None:
            return '{}'
        _line_coordinates.append([_info.Longitude, _info.Latitude])
        _airport_infos.append({'name': _info.Name, 'icao': _icao,
            'iata': _info.Iata})
    _line_string = {
        "type": "LineString",
        "coordinates": _line_coordinates
    }
    _feature = {
        "properties": {
            'callsign': _flight.Callsign,
            'route': _flight.Route,
            'operator_name': _flight.OperatorName,
            'operator_iata': _flight.OperatorIata,
            'airports': _airport_infos},
        "geometry": _line_string,
        "type": "Feature"
    }
    _collection = {"type": "FeatureCollection", "features": [_feature]}
    return _collection


def get_geojson_airport(icao):
    _feature_collection = {
        "type": "FeatureCollection", "features": [{"type": "Feature",
        "properties": {}, "geometry": {"type": "MultiLineString",
        "coordinates": []}}]}
    _routes_info = get_distinct_routes_by_airport(icao)
    _info = get_airport_position(icao)
    if _info is None:
        return json.dumps(_feature_collection)
    local_coords = [_info.Longitude, _info.Latitude]
    if len(_routes_info) == 0:
        return json.dumps(_feature_collection)
    _features = []
    _coordinates = []
    for _route in _routes_info:
        _line_coordinates = []
        _route_items = _route.split('-')
        for _icao in _route_items:
            if _icao == icao:
                _line_coordinates.append(local_coords)
            else:
                _info = get_airport_position(_icao)
                if _info is None:
                    _line_coordinates = []
                    break
                _line_coordinates.append([_info.Longitude, _info.Latitude])
        if len(_line_coordinates) > 0:
            _coordinates.append(_line_coordinates)
    _feature_collection['features'] = [{"type": "Feature",
        "properties": {},
        "geometry": {"type": "MultiLineString",
        "coordinates": _coordinates}}]
    return _feature_collection


def get_geojson_airline(icao):
    _feature_collection = {
        "type": "FeatureCollection", "features": [{"type": "Feature",
        "properties": {}, "geometry": {"type": "MultiLineString",
        "coordinates": []}}]}
    _airline_info = get_distinct_routes_by_airline(icao)
    if _airline_info is None:
        return json.dumps(_feature_collection)
    _routes_info = _airline_info['routes']
    if len(_routes_info) == 0:
        return json.dumps(_feature_collection)
    _airport_positions = get_airport_positions()
    _features = []
    _coordinates = []
    for _route in _routes_info:
        _line_coordinates = []
        _route_items = _route.split('-')
        for _icao in _route_items:
            _position = _airport_positions.get(_icao)
            if _position is None:
                _line_coordinates = []
                break
            _line_coordinates.append(_position)
        if len(_line_coordinates) > 0:
            _coordinates.append(_line_coordinates)
    _feature_collection['features'] = [{"type": "Feature",
        "properties": {"operator_icao": _airline_info['operator_icao'],
        "operator_iata": _airline_info['operator_iata'],
        "operator_name": _airline_info['operator_name']},
        "geometry": {"type": "MultiLineString",
        "coordinates": _coordinates}}]
    return _feature_collection


@timeit
def flightsearch(request_data):
    stops = request_data.numberOfStops
    lat_origin = request_data.origin.lat
    lon_origin = request_data.origin.lng
    radius_origin = float(request_data.originRadius)
    lat_destination = request_data.destination.lat
    lon_destination = request_data.destination.lng
    radius_destination = float(request_data.destinationRadius)
    filter_airline_alliance = request_data.filterAirlineAlliance
    if filter_airline_alliance == 'Star Alliance':
        operator_icaos = ','.join(map(repr, star_alliance_icaos))
    elif filter_airline_alliance == 'Oneworld':
        operator_icaos = ','.join(map(repr, oneworld_icaos))
    elif filter_airline_alliance == 'SkyTeam':
        operator_icaos = ','.join(map(repr, skyteam_icaos))
    if filter_airline_alliance == '':
        filter_string_1 = ""
        filter_string_2 = ""
        filter_string_3 = ""
        filter_string_stopovers = ""
    else:
        filter_string_1 = f"AND FL1.OperatorIcao IN ({operator_icaos})"
        filter_string_2 = f"AND FL2.OperatorIcao IN ({operator_icaos})"
        filter_string_3 = f"AND FL3.OperatorIcao IN ({operator_icaos})"
        filter_string_stopovers = f"AND OperatorIcao IN ({operator_icaos})"
    distance = get_distance(lat_origin, lon_origin, lat_destination,
        lon_destination)
    max_distance = 16*math.sqrt(1e3)*math.sqrt(distance) + 1.05*distance
    logger.info(f'distance: {distance/1e3}km')
    connection = sqlite3.connect("file:" + directory +
        "StandingData.sqb?mode=ro", uri=True)
    connection.row_factory = namedtuple_factory
    connection.create_function('cosd', 1, cos_deg)
    connection.create_function('distance', 4, get_distance)
    cursor = connection.cursor()
    sql_query_origin = f"""
        SELECT Icao FROM Airport
        WHERE Destinations > 0
        AND {lat_origin} - {radius_origin}/110500 < Latitude
        AND Latitude < {lat_origin} + {radius_origin}/110500
        AND COSD({lat_origin}) * 110500 * ({lon_origin} - Longitude)
        < {radius_origin} 
        AND COSD({lat_origin}) * 110500 * (- {lon_origin} + Longitude)
        < {radius_origin} 
        AND DISTANCE(Latitude, Longitude, {lat_origin}, {lon_origin})
        < {radius_origin};
        """
    cursor.execute(sql_query_origin)
    origin_icaos = [x.Icao for x in cursor.fetchall()]
    origins = ','.join(map(repr, origin_icaos))
    logger.debug(f'origins: {origins}')
    sql_query_destination = f"""
        SELECT Icao FROM Airport
        WHERE Origins > 0
        AND {lat_destination} - {radius_destination}/110500 < Latitude
        AND Latitude < {lat_destination} + {radius_destination}/110500
        AND COSD({lat_destination}) * 110500
        * ({lon_destination} - Longitude) < {radius_destination}
        AND COSD({lat_destination}) * 110500
        * (- {lon_destination} + Longitude) < {radius_destination}
        AND DISTANCE(Latitude, Longitude, {lat_destination}, {lon_destination})
        < {radius_destination}
        """
    cursor.execute(sql_query_destination)
    destination_icaos = [x.Icao for x in cursor.fetchall()]
    destinations = ','.join(map(repr, destination_icaos))
    logger.debug(f'destinations: {destinations}')
    if not origins or not destinations:
        cursor.close()
        connection.close()
        return []
    sql_query = f"""
        SELECT DISTINCT
        FL1.Origin || '-' || FL1.Destination AS Route,
        FL1.Length AS TotalLength, 0 AS Stops
        FROM FlightLegs FL1
        WHERE FL1.Origin IN ({origins})
        AND FL1.Destination IN ({destinations})
        {filter_string_1}
        AND TotalLength < {max_distance};
        """
    logger.debug(f'flight search query: {sql_query}')
    cursor.execute(sql_query)
    sql_results = cursor.fetchall()
    direct_routes = [f"{x.Route}" for x in sql_results]
    logger.info(f'found {len(direct_routes)} direct routes.')
    logger.debug('direct_routes: {direct_routes}')
    if stops == 0 or len(direct_routes) > 10:
        cursor.close()
        connection.close()
        return direct_routes
    sql_query = f"""
        SELECT DISTINCT
        FL1.Origin || '-' || FL1.Destination || '-' || FL2.Destination AS
        Route, (FL1.Length+FL2.Length) AS TotalLength, 1 AS Stops
        FROM FlightLegs FL1, FlightLegs FL2
        WHERE FL1.Origin IN ({origins})
        AND NOT FL1.Destination IN ({destinations})
        AND FL2.Destination IN ({destinations})
        AND NOT FL2.Origin IN ({origins})
        AND FL1.Destination=FL2.Origin
        {filter_string_1}
        {filter_string_2}
        AND TotalLength < {max_distance}
        """
    logger.debug(f'flight search query: {sql_query}')
    cursor.execute(sql_query)
    sql_results = cursor.fetchall()
    single_stopover_routes = [f"{x.Route}" for x in sql_results]
    logger.info(f'found {len(single_stopover_routes)} single stopover routes.')
    logger.debug('single_stopover_routes: {single_stopover_routes}')
    if stops == 1 or len(single_stopover_routes + direct_routes) > 10:
        cursor.close()
        connection.close()
        return direct_routes + single_stopover_routes
    sql_query_stopover_origins = f"""
        SELECT DISTINCT Destination FROM FlightLegs
        WHERE Origin IN ({origins})
        AND Length < {max_distance}
        AND NOT Destination IN ({destinations})
        {filter_string_stopovers}
        """
    cursor.execute(sql_query_stopover_origins)
    stopover_origin_icaos = set([x.Destination for x in cursor.fetchall()])
    sql_query_stopover_destinations = f"""
        SELECT DISTINCT Origin FROM FlightLegs
        WHERE Destination IN ({destinations})
        AND Length < {max_distance}
        AND NOT Origin IN ({origins})
        {filter_string_stopovers}
        """
    cursor.execute(sql_query_stopover_destinations)
    stopover_destination_icaos = [x.Origin for x in cursor.fetchall()]
    stopover_origins = ','.join(map(repr, stopover_origin_icaos))
    stopover_destinations = ','.join(map(repr, stopover_destination_icaos))
    logger.debug(f'stopover destinations: {stopover_destinations}')
    logger.debug(f'stopover origins: {stopover_origins}')
    sql_query = f"""
        SELECT DISTINCT
        FL1.Origin || '-' || FL1.Destination || '-' || FL2.Destination ||
        '-' || FL3.Destination AS Route,
        FL1.Length+FL2.Length+FL3.Length AS TotalLength, 2 AS Stops
        FROM FlightLegs FL1, FlightLegs FL2, FlightLegs FL3
        WHERE FL1.Origin IN ({origins})
        AND NOT FL1.Destination IN ({destinations})
        AND FL1.Destination IN ({stopover_origins})
        AND FL3.Destination IN ({destinations}) 
        AND NOT FL3.Origin IN ({origins})
        AND FL3.Origin IN ({stopover_destinations})
        AND FL2.Origin IN ({stopover_origins})
        AND FL2.Destination IN ({stopover_destinations})
        AND FL2.Destination != FL1.Origin
        AND FL3.Destination != FL2.Origin
        AND FL1.Destination=FL2.Origin AND FL2.Destination=FL3.Origin
        {filter_string_1}
        {filter_string_2}
        {filter_string_3}
        AND TotalLength < {max_distance}
        """
    logger.debug(f'flight search query: {sql_query}')
    cursor.execute(sql_query)
    sql_results = cursor.fetchall()
    double_stopover_routes = [f"{x.Route}" for x in sql_results]
    logger.info(f'found {len(double_stopover_routes)} double stopover routes.')
    logger.debug('double_stopover_routes: {double_stopover_routes}')
    cursor.close()
    connection.close()
    return direct_routes + single_stopover_routes + double_stopover_routes


@timeit
def get_geojson_flightsearch(request_data):
    _airport_positions = get_airport_positions()
    _feature_collection = {
        "type": "FeatureCollection", "features": [{"type": "Feature",
        "properties": {}, "geometry": {"type": "MultiLineString",
        "coordinates": []}}]}
    _routes_info = flightsearch(request_data)
    _features = []
    _coordinates = []
    for _route in _routes_info:
        _line_coordinates = []
        _route_items = _route.split('-')
        for _icao in _route_items:
            _airport_coordinates = _airport_positions.get(_icao)
            if _airport_coordinates is None:
                break
            _line_coordinates.append(_airport_coordinates)
        if len(_line_coordinates) > 0:
            _coordinates.append(_line_coordinates)
    _feature_collection['features'] = [{"type": "Feature",
        "properties": {}, "geometry": {"type": "MultiLineString",
        "coordinates": _coordinates}}]
    return _feature_collection
