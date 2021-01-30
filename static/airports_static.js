map.createPane('routePlot');
map.getPane('routePlot').style.zIndex = 395;

map.createPane('airports');
map.getPane('airports').style.zIndex = 397;

function clickAirport(eo) {
    return;
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
            tooltipContent += "<br>" + feature.properties.known_destinations + " known destinations";
        }
        if (typeof feature.properties.known_departures !== 'undefined') {
            tooltipContent += "<br>" + feature.properties.known_departures + " known departures";
        }
        layer.bindTooltip(tooltipContent, {
            direction: "top",
            offset: [0, -5]
        });

    },
    pointToLayer: function(feature, latlng) {
        var radius = 1000;
        if (typeof feature.properties.known_departures !== 'undefined') {
            radius += feature.properties.known_departures * 3.5;
        } else if (typeof feature.properties.known_destinations !== 'undefined') {
            radius += feature.properties.known_destinations * 5;
        } else if (feature.properties.type == 'medium_airport') {
            radius += 1500;
        } else if (feature.properties.type == 'large_airport') {
            radius += 3000;
        };
        return L.circle(latlng, {
            color: '#d50000',
            fillColor: '#d50000',
            fillOpacity: 0.2,
            radius: radius
        })
    }
})

layerControl.addOverlay(airportMarkers,
    "<span style='background-color:rgba(213, 0, 0, 0.2)'>Airports</span>");

function loadAirportData(url) {
    if (!url) url = './airports_static.json';
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            var airports = JSON.parse(xhr.responseText);
            airportMarkers.clearLayers();
            airportMarkers.addData(airports);
        }
    };
    xhr.send();
}
