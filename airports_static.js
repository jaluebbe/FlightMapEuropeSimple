map.createPane('routePlot');
map.getPane('routePlot').style.zIndex = 395;

map.createPane('airports');
map.getPane('airports').style.zIndex = 396;

var airportMarkers = L.geoJSON(null, {
    pane: 'airports',
    onEachFeature: function(feature, layer) {
        var iata = feature.properties.iata;
        if (typeof iata === 'undefined' || iata == '') {
            iata = '-';
        }
        var tooltipContent =
            "" + feature.properties.name + "<BR>" +
            feature.properties.icao + " / " +
            feature.properties.iata;
        layer.bindTooltip(tooltipContent, {
            direction: "top",
            offset: [0, -5]
        });

    },
    pointToLayer: function(feature, latlng) {
        var radius = 1000;
        if (feature.properties.type == 'medium_airport') {
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
var latlngs;

layerControl.addOverlay(airportMarkers,
    "<span style='background-color:rgba(213, 0, 0, 0.2)'>Airports</span>");

function loadAirportData() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './airports_static.json');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            airports = JSON.parse(xhr.responseText);
            airportMarkers.addData(airports);
        }
    };
    xhr.send();
}
loadAirportData();
