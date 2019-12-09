from fastapi import FastAPI, Query
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel, confloat, conint, constr
import backend_vrs_db

app = FastAPI(
    openapi_prefix='',
    title='FlightMapEuropeSimple',
    description=''
    )

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
async def root():
    return FileResponse('static/flightsearch.html')

@app.get("/api/geojson/airports")
def get_geojson_airports():
    return backend_vrs_db.get_geojson_airports()

@app.get("/api/geojson/callsign/")
def get_geojson_callsign(
    callsign: str = Query(..., min_length=4, max_length=8, regex=(
    '^([A-Z]{3})[0-9](([0-9]{0,3})|([0-9]{0,2})([A-Z])|([0-9]?)([A-Z]{2}))$'))):
    return backend_vrs_db.get_geojson_callsign(callsign)

@app.get("/api/geojson/airline/")
def get_geojson_airline(
    icao: str = Query(..., min_length=3, max_length=3, regex=(
    '^[A-Z]{3}$'))):
    return backend_vrs_db.get_geojson_airline(icao)

@app.get("/api/geojson/airport/")
def get_geojson_airport(
    icao: str = Query(..., min_length=4, max_length=4, regex="^[0-9A-Z]{4}$")):
    return backend_vrs_db.get_geojson_airport(icao)

@app.post("/api/geojson/flightsearch")
def post_geojson_flightsearch(data: FlightSearch):
    return {'data': data}
