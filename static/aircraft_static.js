var aircraftPositions;
var downloadingPositions = false;

var planeIcon = L.icon({
    iconUrl: 'static/aiga_air_transportation.svg',
    iconSize: [16, 16]
})

var aircraftMarkers = L.geoJSON(null, {
    onEachFeature: function(feature, layer) {
        var tooltipContent =
            "" + feature.properties.callsign + "<br>" +
            "FL " + feature.properties.flight_level + "<br>" +
            feature.properties.heading + " deg<br>" +
            feature.properties.ground_speed + " kn<br>" +
            feature.properties.vertical_speed + " ft/min";
        layer.bindTooltip(tooltipContent, {
            direction: "top",
            offset: [0, -5]
        });
    },
    filter: function(feature) {
        switch (feature.properties.ul_visible) {
            case 'both':
                return true;
            case 'lower':
                return (map.hasLayer(lowerAirspace) || !map.hasLayer(upperAirspace));
            case 'upper':
                return (map.hasLayer(upperAirspace) || !map.hasLayer(lowerAirspace));
        }
    },
    pointToLayer: function(feature, latlng) {
        return L.marker(latlng, {
            icon: planeIcon,
            rotationOrigin: 'center center',
            rotationAngle: feature['properties']['heading']
        });
    }
});
var clusteredAircraftMarkers = L.markerClusterGroup({
    disableClusteringAtZoom: 8,
    spiderfyOnMaxZoom: false,
    maxClusterRadius: 60
});
map.addLayer(clusteredAircraftMarkers);
layerControl.addOverlay(clusteredAircraftMarkers, "<span>Aircraft</span>");

map.on('baselayerchange', function(eo) {
    if ((eo.name.indexOf('Lower Airspace') == -1) &&
        (eo.name.indexOf('Upper Airspace') != -1)) {
        return
    }
    aircraftMarkers.clearLayers();
    aircraftMarkers.addData(aircraftPositions);
});

function refreshAircraftPositions() {
    if (downloadingPositions == true) {
        return
    };
    downloadingPositions = true;
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'https://opensky-network.org/api/states/all');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            aircraftPositions = [];
            var response = JSON.parse(xhr.responseText);
            response.states.forEach(function(aircraft) {
                var callsign = aircraft[1].trim();
                if (callsign.length == 0)
                    return;
                else if (aircraft[5] === null || aircraft[6] === null)
                    return;
                var aircraftPosition = ({
                    "geometry": {
                        "type": "Point",
                        "coordinates": [aircraft[5], aircraft[6]]
                    },
                    "type": "Feature",
                    "properties": {
                        "callsign": callsign,
                        "heading": Math.round(aircraft[10]),
                        "ul_visible": "both",
                        "flight_level": Math.round(aircraft[7] / 0.3048 / 100),
                        "ground_speed": Math.round(aircraft[9] * (3600 / 1852)),
                        "vertical_speed": Math.round(aircraft[11] * (60 / 0.3048))
                    }
                });
                for (var i = 0, len = upper_lower_airspace_limits.features.length; i < len; i++) {
                    let airspace = upper_lower_airspace_limits.features[i];
                    if (aircraftPosition.properties.flight_level < airspace.properties.MIN_FLIGHT)
                        continue;
                    else if (aircraftPosition.properties.flight_level > airspace.properties.MAX_FLIGHT)
                        continue;
                    else if (turf.booleanPointInPolygon(aircraftPosition, airspace)) {
                        aircraftPosition.properties.ul_visible = airspace.properties.UL_VISIBLE;
                        break;
                    }
                }
                aircraftPositions.push(aircraftPosition);
            });
            aircraftMarkers.clearLayers();
            aircraftMarkers.addData(aircraftPositions);
            clusteredAircraftMarkers.clearLayers();
            clusteredAircraftMarkers.addLayer(aircraftMarkers);
        }
        downloadingPositions = false;
    };
    xhr.send();
}
refreshAircraftPositions();
var myInterval = window.setInterval("refreshAircraftPositions()", 10000);
