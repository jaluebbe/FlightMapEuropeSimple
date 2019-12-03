var aircraftPositions;
var downloadingPositions = false;

var planeIcon = L.icon({
    iconUrl: 'static/aiga_air_transportation.svg',
    iconSize: [16, 16]
})
function processedActiveFeature(feature) {
    return false;
}
function clickAircraft(eo) {
    return;
}
var aircraftMarkers = L.geoJSON(null, {
    onEachFeature: function(feature, layer) {
        layer.once('click', function(eo) {
            clickAircraft(eo);
        });
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
        if (processedActiveFeature(feature))
            return false;
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

function reloadAircraftPositions() {
    aircraftMarkers.clearLayers();
    aircraftMarkers.addData(aircraftPositions);
    clusteredAircraftMarkers.clearLayers();
    clusteredAircraftMarkers.addLayer(aircraftMarkers);
}
map.on('overlayremove', function(eo) {
    if ((eo.name.indexOf('Lower Airspace') != -1) &&
        (eo.name.indexOf('Upper Airspace') != -1)) {
        return
    }
    if (!map.hasLayer(upperAirspace) && !map.hasLayer(lowerAirspace))
        reloadAircraftPositions();
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
            var t_start = Date.now();
            aircraftPositions = [];
            var response = JSON.parse(xhr.responseText);
            response.states.forEach(function(aircraft) {
                var callsign = aircraft[1].trim();
                if (callsign.length == 0)
                    return;
                else if (aircraft[5] === null || aircraft[6] === null)
                    return;
                else if (!callsign.match('^[A-Z]{3}[0-9]{1,4}[A-Z]{0,2}'))
                    return;
                var aircraftPosition = turf.point([aircraft[5], aircraft[6]], {
                    "callsign": callsign,
                    "heading": Math.round(aircraft[10]),
                    "ul_visible": "both",
                    "flight_level": Math.round(aircraft[7] / 0.3048 / 100),
                    "ground_speed": Math.round(aircraft[9] * (3600 / 1852)),
                    "vertical_speed": Math.round(aircraft[11] * (60 / 0.3048))
                });
                turf.featureEach(upper_lower_airspace_limits, function (airspace, featureIndex) {
                    if (aircraftPosition.properties.flight_level >= airspace.properties.MIN_FLIGHT &&
                        aircraftPosition.properties.flight_level <= airspace.properties.MAX_FLIGHT &&
                        turf.booleanPointInPolygon(aircraftPosition, airspace)) {
                            aircraftPosition.properties.ul_visible = airspace.properties.UL_VISIBLE;
                    }
                });
                aircraftPositions.push(aircraftPosition);
            });
            reloadAircraftPositions()
            var t_stop = Date.now();
            console.log('duration: ' + (t_stop-t_start) / 1e3 + 's');
        }
        downloadingPositions = false;
    };
    xhr.send();
}
