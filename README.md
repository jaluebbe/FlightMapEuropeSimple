# FlightMapEuropeSimple
Aircraft positions received by OpenSky Network contributors as well as airports and airspaces are shown on a map.

## Airspace shapefiles
The GeoJSON shapefile flightmap_europe_fir_uir_ec_only.json contains simplified
shapes of the FIRs and UIRs of all Eurocontrol member states. 
It was created from the shapefile found at
https://github.com/euctrl-pru/eurocontrol-atlas/blob/master/zip/FirUir_NM.zip . 
The shapefile was converted from SHP to GeoJSON by ```ogr2ogr -f geoJSON
fir_uir_nm.json FirUir_NM/FirUir_NM.shp```.

The GeoJSON shapefile flightmap_europe_fir_uir.json covers the whole world. 
However, the focus of this map is Europe. Distant airspaces are shown with
less detail and are approximately merged according to the ICAO regions. It
may not reflect the most recent situation as some publicly available data
sources may be outdated. 
This file is generated using prepare_fir_uir_shapefile.py . 
It requires flightmap_europe_fir_uir_ec_only.json to be generated first. 
Further data sources are an GeoJSON API for FAA airspace boundary 
(https://ais-faa.opendata.arcgis.com/datasets/67885972e4e940b2aa6d74024901c561_0) 
and another shapefile found at 
https://github.com/euctrl-pru/eurocontrol-atlas/blob/master/zip/FirUir_EAD.zip .
The preparation script may be modified to show other regions in more detail. 

## Airport shapefiles
The shapefile containing the airports for the static version of the map is 
created using prepare_static_airports.py . 
Data from ourairports.com is filtered and converted to GeoJSON.

## Static version of the map
The version of the map hosted at 
https://jaluebbe.github.io/FlightMapEuropeSimple/ 
consists of HTML, CSS and JavaScript only. 
Airspaces and airports consist of static data. 
Aircraft positions are downloaded directly from OpenSky Network every 10s. 
Interactive controls providing flight route information for airports or
aircraft are not available on this map. 

## Dynamic version of the map
Airports as well as flight routes are taken from the VRS database which is published daily. 
Clicking on an aircraft shows the current flight route while clicking on an airport shows all known destinations at once.

### Software requirements

#### conda/apt

gunicorn or hypercorn (alternative to gunicorn+uvicorn which may run on windows)

#### pip

fastapi uvicorn aiofiles

### Data Sources

#### Flight route database of the Virtual Radar Server project

A crowd-sourced flight route database is available at http://www.virtualradarserver.co.uk/FlightRoutes.aspx . 

Call prepare_vrs_database.py to download the VRS database and to create a table FlightRoute.

### Startup of the web interface

The web interface and API is hosted using FastAPI. It could also be run as a Docker container.

#### FastAPI
```
gunicorn -w8 -b 0.0.0.0:5000 backend_fastapi:app -k uvicorn.workers.UvicornWorker
```
or
```
hypercorn -w8 -b 0.0.0.0:5000 backend_fastapi:app
```
The number of workers is defined via the -w argument. Instead of using multiple workers the --reload argument would restart the worker as soon as any source code is changed.
#### Build and run as a Docker container
```
docker build -t flightroute_europe_simple ./
docker run -d -p 80:80 --mount src=`pwd`/flightroutes,target=/app/flightroutes,type=bind flightmap_europe_simple
```
