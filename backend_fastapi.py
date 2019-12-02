from fastapi import FastAPI, Query
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
import backend_vrs_db

app = FastAPI(
    openapi_prefix='',
    title='FlightMapEuropeSimple',
    description=''
    )

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def root():
#    return FileResponse('static/flightmap_europe_static.html')
    return FileResponse('static/flightmap_europe_simple.html')

@app.get("/api/geojson/airports")
def get_geojson_airports():
    return backend_vrs_db.get_geojson_airports()

@app.get("/api/geojson/callsign/")
def get_geojson_callsign(
    callsign: str = Query(..., min_length=4, max_length=8, regex=(
    '^([A-Z]{3})[0-9](([0-9]{0,3})|([0-9]{0,2})([A-Z])|([0-9]?)([A-Z]{2}))$'))):
    return backend_vrs_db.get_geojson_callsign(callsign)

#http://localhost:8000/items/?q=foo&q=bar
@app.get("/api/geojson/airport/")
def get_geojson_airport(
    icao: str = Query(..., min_length=4, max_length=4, regex="^[0-9A-Z]{4}$")):
    return backend_vrs_db.get_geojson_airport(icao)

