import os
import json
from fastapi import FastAPI, Query, HTTPException
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, confloat, conint, constr
import redis
import backend_vrs_db
import logging
logging.basicConfig(level=logging.INFO)

redis_connection = redis.Redis(os.getenv('REDIS_HOST'), decode_responses=True)

app = FastAPI(
    openapi_prefix='',
    title='FlightMapEuropeSimple',
    description=''
    )
app.add_middleware(GZipMiddleware, minimum_size=500)


class Location(BaseModel):
    lat: confloat(ge=-90, le=90)
    lng: confloat(ge=-180, le=180)


class FlightSearch(BaseModel):
    origin: Location
    destination: Location
    originRadius: conint(gt=0, le=600e3)
    destinationRadius: conint(gt=0, le=600e3)
    numberOfStops: conint(ge=0, le=2)
    filterAirlineAlliance: constr(regex='^(Star Alliance|Oneworld|SkyTeam|)$')


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse('static/flightmap_europe_simple.html')


@app.get("/flightsearch.html", include_in_schema=False)
async def flightsearch():
    return FileResponse('static/flightsearch.html')


@app.get("/statistics.html", include_in_schema=False)
async def statistics():  
    return FileResponse('static/statistics.html') 


@app.get("/test.html", include_in_schema=False)
async def testpage():
    return FileResponse('static/flightmap_test.html')


@app.get("/api/geojson/airports")
def get_geojson_airports():
    return backend_vrs_db.get_geojson_airports()


@app.get("/api/geojson/callsign/")
def get_geojson_callsign(
        callsign: str = Query(..., min_length=4, max_length=8, regex=(
                '^([A-Z]{3})[0-9](([0-9]{0,3})|([0-9]{0,2})([A-Z])|([0-9]?)'
                '([A-Z]{2}))$'))):
    return backend_vrs_db.get_geojson_callsign(callsign)


@app.get("/api/geojson/airline/")
def get_geojson_airline(
        icao: str = Query(..., min_length=3, max_length=3, regex='^[A-Z]{3}$')):
    return backend_vrs_db.get_geojson_airline(icao)


@app.get("/api/geojson/airport/")
def get_geojson_airport(
        icao: str = Query(..., min_length=4, max_length=4,
                          regex="^[0-9A-Z]{4}$")):
    return backend_vrs_db.get_geojson_airport(icao)


@app.post("/api/geojson/flightsearch")
def post_geojson_flightsearch(data: FlightSearch):
    return backend_vrs_db.get_geojson_flightsearch(data)


@app.get("/api/covid_data.json")
def get_covid_data():
    try:
        covid_data = json.loads(redis_connection.get('covid_data'))
    except TypeError:
        logging.exception('Found no covid_data in redis.')
        raise HTTPException(status_code=404, detail="Item not found")
    except redis.exceptions.ConnectionError:
        logging.exception('Problem with redis connection.')
        raise HTTPException(status_code=500, detail="Internal server error")
    return covid_data


@app.get("/api/flights_statistics.json")
def get_flights_statistics():
    try:
        flights_statistics = json.loads(redis_connection.get(
            'flights_statistics'))
    except TypeError:
        logging.exception('Found no flights_statistics in redis.')
        raise HTTPException(status_code=404, detail="Item not found")
    except redis.exceptions.ConnectionError:
        logging.exception('Problem with redis connection.')
        raise HTTPException(status_code=500, detail="Internal server error")
    return flights_statistics


@app.get("/api/fir_uir_statistics.json")
def get_fir_uir_statistics():
    try:
        fir_uir_statistics = json.loads(redis_connection.get(
            'fir_uir_statistics'))
    except TypeError:
        logging.exception('Found no fir_uir_statistics in redis.')
        raise HTTPException(status_code=404, detail="Item not found")
    except redis.exceptions.ConnectionError:
        logging.exception('Problem with redis connection.')
        raise HTTPException(status_code=500, detail="Internal server error")
    return fir_uir_statistics
