import time
import requests
import os
import sqlite3
import gzip

vrs_url = "http://www.virtualradarserver.co.uk/Files/StandingData.sqb.gz"
directory = "flightroutes/"
file_info = {}
if os.path.isfile(directory + "StandingData.sqb"):
    file_info['vrs'] = os.stat(directory + "StandingData.sqb").st_ctime

def check_data():
    if not os.path.isfile(directory + "StandingData.sqb") or (
            time.time() - file_info['vrs'] > 86400):
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
    connection = sqlite3.connect(os.path.join(directory, "StandingData.sqb"))
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS FlightRoute")
    cursor.execute("""
        CREATE TABLE FlightRoute AS
        SELECT Callsign, OperatorIcao, OperatorIata, OperatorName,
        FromAirportIcao || '-' || IFNULL(GROUP_CONCAT(RouteStopView.AirportIcao,
        '-')||'-','') || ToAirportIcao AS Route FROM RouteView
        LEFT JOIN RouteStopView ON RouteView.RouteId=RouteStopView.RouteId
        WHERE LENGTH(FromAirportIcao) > 0 AND LENGTH(ToAirportIcao) > 0
        GROUP BY Callsign;
        """)
    connection.commit()
    connection.close()

if __name__ == '__main__':

    check_data()
