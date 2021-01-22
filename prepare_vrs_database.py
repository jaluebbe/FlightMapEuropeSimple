import time
import requests
import os
import sqlite3
import gzip
import numpy as np
import math
import json

def get_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return
    degRad = 2 * math.pi / 360
    distance = (
        6.370e6 * math.acos(math.sin(lat1 * degRad) * math.sin(lat2 * degRad)
        + math.cos(lat1 * degRad) * math.cos(lat2 * degRad) * math.cos((lon2 - lon1)
        * degRad)))
    return int(round(distance))

vrs_url = "http://www.virtualradarserver.co.uk/Files/StandingData.sqb.gz"
directory = "flightroutes/"
file_info = {}
if os.path.isfile(directory + "StandingData.sqb"):
    file_info['vrs'] = os.stat(directory + "StandingData.sqb").st_ctime

def check_data():
#    if not os.path.isfile(directory + "StandingData.sqb") or (
#            time.time() - file_info['vrs'] > 86400):
        download_vrs_database()
        create_flightroute_table()

def download_vrs_database():
    if not os.path.exists(directory):
        os.makedirs(directory)
    r = requests.get(vrs_url)
    if r.status_code == requests.codes.ok:
        with open(directory + "StandingData.sqb.gz", 'wb') as f:
            f.write(r.content)
        with gzip.GzipFile(directory + "StandingData.sqb.gz", 'rb') as infile:
            data = infile.read()
        with open(directory + "StandingData.sqb", 'wb') as outfile:
            outfile.write(data)
        file_info['vrs'] = time.time()

def create_flightroute_table():
    """
    SQL statements were formatted using
    https://www.freeformatter.com/sql-formatter.html
    """
    connection = sqlite3.connect(os.path.join(directory, "StandingData.sqb"))
    connection.create_function('distance', 4, get_distance)
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS FlightRoute")
    cursor.execute("""
        CREATE TABLE FlightRoute AS
        SELECT
            Callsign,
            OperatorIcao,
            OperatorIata,
            OperatorName,
            FromAirportIcao || '-' || IFNULL(GROUP_CONCAT(
                RouteStopView.AirportIcao, '-') || '-', '') || ToAirportIcao
                    AS Route
        FROM
            RouteView
            LEFT JOIN
                RouteStopView 
                ON RouteView.RouteId = RouteStopView.RouteId
        WHERE
            LENGTH(FromAirportIcao) > 0
            AND LENGTH(ToAirportIcao) > 0
        GROUP BY
            Callsign
        """)
    with open(os.path.join(directory, "recurring_callsigns.json")) as f:
        recurring_callsigns = json.load(f)['recurring_callsigns']

    cursor.execute("DROP TABLE IF EXISTS RecentFlightRoutes")
    cursor.execute("""
        CREATE TABLE RecentFlightRoutes AS
        SELECT
            Callsign,
            OperatorIcao,
            Route
        FROM
            FlightRoute
        WHERE
            Callsign IN {}
        """.format(tuple(recurring_callsigns)))

    cursor.execute("DROP TABLE IF EXISTS FlightLegs")
    cursor.execute("""
        CREATE TABLE FlightLegs AS
        SELECT
            Origin,
            Destination,
            OperatorIcao,
            DISTANCE(o.Latitude, o. Longitude, d.Latitude, d.Longitude)
                AS Length
        FROM
            (
                SELECT DISTINCT
                    SUBSTR(Route, 1, 4) AS Origin,
                    SUBSTR(Route, 6, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 6, 4) AS Origin,
                    SUBSTR(Route, 11, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 11, 4) AS Origin,
                    SUBSTR(Route, 16, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 16, 4) AS Origin,
                    SUBSTR(Route, 21, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 21, 4) AS Origin,
                    SUBSTR(Route, 26, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 26, 4) AS Origin,
                    SUBSTR(Route, 31, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 31, 4) AS Origin,
                    SUBSTR(Route, 36, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 36, 4) AS Origin,
                    SUBSTR(Route, 41, 4) AS Destination,
                    OperatorIcao 
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 41, 4) AS Origin,
                    SUBSTR(Route, 46, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 46, 4) AS Origin,
                    SUBSTR(Route, 51, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
                UNION
                SELECT DISTINCT
                    SUBSTR(Route, 51, 4) AS Origin,
                    SUBSTR(Route, 56, 4) AS Destination,
                    OperatorIcao
                FROM
                    RecentFlightRoutes
                WHERE
                    LENGTH(Destination) > 0
            )
        ,
            Airport AS o,
            Airport AS d
        WHERE
            Origin = o.Icao 
            AND Destination = d.Icao
            AND Origin != Destination
        """)
    cursor.execute("ALTER TABLE Airport ADD COLUMN Destinations INTEGER "
        "DEFAULT 0")
    cursor.execute("ALTER TABLE Airport ADD COLUMN Origins INTEGER DEFAULT 0")
    cursor.execute("UPDATE Airport SET Destinations = (SELECT COUNT("
        "Destination) FROM FlightLegs WHERE Origin=Airport.Icao)")
    cursor.execute("UPDATE Airport SET Origins = (SELECT COUNT(Origin) FROM "
        "FlightLegs WHERE Destination=Airport.Icao)")
    connection.commit()
    connection.close()

if __name__ == '__main__':

    check_data()
