import time
import json
import sqlite3
from collections import namedtuple
import logging
logger = logging.getLogger(__name__)

directory = "flightroutes/"

def namedtuple_factory(cursor, row):
    """
    Usage:
    con.row_factory = namedtuple_factory
    """
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)

def get_geojson_airports():
    try:
        connection = sqlite3.connect("file:" + directory +
            "StandingData.sqb?mode=ro", uri=True)
        connection.row_factory = namedtuple_factory
        cursor = connection.cursor()
        cursor.execute(
            "SELECT Name, Icao, Iata, ROUND(Latitude, 6) AS Latitude, "
            "ROUND(Longitude, 6) AS Longitude FROM Airport "
            "WHERE LENGTH(Icao) = 4")
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
            'known_departures': 0}}
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
        cursor = connection.cursor()
        cursor.execute(
            "SELECT Icao, ROUND(Latitude, 6) AS Latitude, "
            "ROUND(Longitude, 6) AS Longitude FROM Airport "
            "WHERE LENGTH(Icao) = 4")
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
            "SELECT DISTINCT SUBSTR(Route, myIndex, 9) AS DirectRoute FROM "
            "(SELECT Route, INSTR(Route, ? || '-') AS myIndex FROM "
            "(SELECT Callsign, Route FROM FlightRoute) WHERE myIndex > 0)",
            (airport_icao,))
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
            "SELECT DISTINCT Route, OperatorName, OperatorIata "
            "FROM FlightRoute WHERE OperatorIcao=?", (operator_icao,))
        result = cursor.fetchall()
        connection.close()
    except sqlite3.DatabaseError:
        logger.exception(
            'get_distinct_routes_by_airline({})'.format(operator_icao))
        return None
    if result is not None:
        return {
            'routes': [row.Route for row in result],
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
            'iata': _info.Iata,})
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
