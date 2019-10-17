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

# Static version of the map
The version of the map hosted at 
https://jaluebbe.github.io/FlightMapEuropeSimple/ 
consists of HTML, CSS and JavaScript only. 
Airspaces and airports consist of static data. 
Aircraft positions are downloaded directly from OpenSky Network every 10s. 
Interactive controls providing flight route information for airports or
aircraft are not available on this map. 
