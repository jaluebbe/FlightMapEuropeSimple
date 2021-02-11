function clickAirport(eo) {
    routesInfo(eo.target.feature.properties);
}

var routePlot = L.geoJSON(null, {
    pane: 'routePlot',
    style: function(feature) {
        return {
            weight: 1.5,
            opacity: 1,
            color: 'blue'
        };
    }
});
routePlot.addTo(map);

var info = L.control({
    position: 'bottomright'
});

info.onAdd = function(map) {
    this._div = L.DomUtil.create('div', 'info');
    this.reset();
    return this._div;
};

info.reset = function() {
    this._div.innerHTML = '<h4>Route information</h4> Click on any airport';
    routePlot.clearLayers();
};
info.addTo(map);
info.updateAirportInfo = function(airportInfo) {
    var text = '<b>' + airportInfo.name + ' (' + airportInfo.icao;
    if (airportInfo.iata !== undefined && airportInfo.iata != '')
        text += ' / ' + airportInfo.iata;
    text += ')</b><br>';
    if (typeof airportInfo.known_destinations !== 'undefined') {
        text += airportInfo.known_destinations + ' known destinations<br>';
    }
    text += '<button onclick="info.reset()">reset airport routes</button>';
    this._div.innerHTML = text;
}

function routesInfo(airportInfo) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './api/geojson/airport/?icao=' + airportInfo.icao);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            var routes_info = JSON.parse(xhr.responseText);
            if (typeof routes_info.features === 'undefined') {} else {
                info.updateAirportInfo(airportInfo)
                routePlot.clearLayers();
                turf.meta.segmentEach(routes_info, function(currentSegment, featureIndex, multiFeatureIndex, geometryIndex, segmentIndex) {
                    var start = currentSegment.geometry.coordinates[0];
                    var end = currentSegment.geometry.coordinates[1];
                    var distance = turf.distance(start, end);
                    if (distance > 0)
                        routePlot.addData(turf.greatCircle(start, end, {
                            npoints: Math.round(distance * 0.009),
                            offset: 10
                        }));
                });
            }
        }
    };
    xhr.send();
}

map.on('click', function(eo) {
    clickMap(eo);
});

function clickMap(eo) {
    info.reset();
}
