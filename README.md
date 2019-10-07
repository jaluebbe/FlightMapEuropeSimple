# FlightMapEuropeSimple
Aircraft positions received by OpenSky Network contributors as well as airports and airspaces are shown on a map.

## Airspace shapefiles
The GeoJSON shapefile flightmap_europe_fir_uir_ec_only.json contains simplified
shapes of the FIRs and UIRs of all Eurocontrol member states. 
It was created
from the shapefile found at
https://github.com/euctrl-pru/eurocontrol-atlas/blob/master/zip/FirUir_NM.zip . 
The shapefile was converted from SHP to GeoJSON by ```ogr2ogr -f geoJSON
fir_uir_nm.json FirUir_NM/FirUir_NM.shp```.
