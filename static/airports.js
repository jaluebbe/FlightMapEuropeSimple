map.createPane('routePlot');
map.getPane('routePlot').style.zIndex = 395;

map.createPane('airports');
map.getPane('airports').style.zIndex = 397;

function clickAirport(eo) {
    routesInfo(eo.target.feature.properties);
}

var airportMarkers = L.geoJSON(null, {
    pane: 'airports',
    onEachFeature: function(feature, layer) {
        layer.on('click', function(eo) {
            clickAirport(eo);
        });
        var iata = feature.properties.iata;
        if (typeof iata === 'undefined' || iata == '') {
            iata = '-';
        }
        var tooltipContent =
            "" + feature.properties.name + "<br>" +
            feature.properties.icao + " / " +
            feature.properties.iata;
        if (typeof feature.properties.known_destinations !== 'undefined') {
            tooltipContent += "<br>" + feature.properties.known_destinations + " known destinations"
                + "<br>" + feature.properties.known_departures + " known departures";
        }
        layer.bindTooltip(tooltipContent, {
            direction: "top",
            offset: [0, -5]
        });

    },
    pointToLayer: function(feature, latlng) {
        var radius = 1000 + feature.properties.known_departures * 3.5;
        return L.circle(latlng, {
            color: '#d50000',
            fillColor: '#d50000',
            fillOpacity: 0.2,
            radius: radius
        })
    }
}).addTo(map)
var latlngs;
var routePlot = L.geoJSON(null, {
    pane: 'routePlot',
    style: function (feature) {
        return {
            weight: 1.5,
            opacity: 1,
            color: 'blue'
        };
    }
});
routePlot.addTo(map);

var info = L.control({position: 'bottomright'});

info.onAdd = function (map) {
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
        text +=  ' / ' + airportInfo.iata;
    text += ')</b><br>';
    if (typeof airportInfo.known_destinations !== 'undefined') {
        text += airportInfo.known_destinations + ' known destinations<br>';
    }
    text +=  '<button onclick="info.reset()">reset airport routes</button>';
    this._div.innerHTML = text;
}
layerControl.addOverlay(airportMarkers,
    "<span style='background-color:rgba(213, 0, 0, 0.2)'>Airports</span>");

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
                turf.segmentEach(routes_info, function(currentSegment, featureIndex, multiFeatureIndex, geometryIndex, segmentIndex) {
                    var start = currentSegment.geometry.coordinates[0];
                    var end = currentSegment.geometry.coordinates[1];
                    Math.round(turf.distance(start, end) * 0.009);
                    routePlot.addData(turf.greatCircle(start, end, {
                        npoints: Math.round(turf.distance(start, end) * 0.009),
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
function refreshAirportData() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './api/geojson/airports');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            airports = JSON.parse(xhr.responseText);
            airportMarkers.clearLayers();
            airportMarkers.addData(airports);
        }
    };
    xhr.send();
}
