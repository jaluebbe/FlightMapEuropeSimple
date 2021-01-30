import os
from fastapi import FastAPI, Query, HTTPException, Response
from starlette.staticfiles import StaticFiles, FileResponse
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, confloat, conint, constr
import redis
import backend_vrs_db
import logging
logging.basicConfig(level=logging.INFO)

redis_connection = redis.Redis(os.getenv('REDIS_HOST'), decode_responses=True)

app = FastAPI(
    title='FlightMapEuropeSimple',
    openapi_url='/api/openapi.json',
    docs_url="/api/docs"
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


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse('static/index.html')


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
    json_data = redis_connection.get('covid_data')
    if json_data is not None:
        return Response(content=json_data, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/api/flights_statistics.json")
def get_flights_statistics():
    json_data = redis_connection.get('flights_statistics')
    if json_data is not None:
        return Response(content=json_data, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/api/fir_uir_statistics.json")
def get_fir_uir_statistics():
    json_data = redis_connection.get('fir_uir_statistics')
    if json_data is not None:
        return Response(content=json_data, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="Item not found")


app.mount("/", StaticFiles(directory="static"), name="static")
