var initialDestination = [51.5, -0.12]
var initialOrigin = [52.5, 7.3]
var numberOfStops = {
    value: 0
};
var legend = L.control({
    position: 'topright'
});
legend.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'info legend');
    div.innerHTML =
        '<table><tr><td>Origin</td><td><select id="originRadiusKm">' +
        '<option value=25>25km</option><option value=50>50km</option>' +
        '<option selected value=75>75km</option><option value=100>100km</option>' +
        '<option value=125>125km</option><option value=150>150km</option>' +
        '<option value=175>175km</option>' +
        '<option value=200>200km</option><option value=250>250km</option>' +
        '<option value=300>300km</option><option value=400>400km</option>' +
        '<option value=500>500km</option><option value=600>600km</option>' +
        '</select><br></td></tr>' +
        '<tr><td>Destination</td><td><select id="destinationRadiusKm">' +
        '<option value=25>25km</option><option selected value=50>50km</option>' +
        '<option value=75>75km</option><option value=100>100km</option>' +
        '<option value=125>125km</option><option value=150>150km</option>' +
        '<option value=175>175km</option>' +
        '<option value=200>200km</option><option value=250>250km</option>' +
        '<option value=300>300km</option><option value=400>400km</option>' +
        '<option value=500>500km</option><option value=600>600km</option>' +
        '</select></td></tr>' +
        '<tr><td>Stops</td><td><select id="numberOfStops">' +
        '<option selected>0</option><option>1</option><option>2</option>' +
        '</select></td></tr>' +
        '<tr><td>Filter</td><td><select id="filterAirlineAlliance">' +
        '<option value="" selected>-</option><option>Star Alliance</option>' +
        '<option>Oneworld</option><option>SkyTeam</option>' +
        '</select></td></tr>' +
        '<tr><td colspan=2><div id="helptext">Click for your origin!</div></td></tr>'
    '</table>';
    L.DomEvent.on(div, 'click', function(ev) {
        L.DomEvent.stopPropagation(ev);
    });

    return div;
};

legend.addTo(map)

map.createPane('radius');
map.getPane('radius').style.zIndex = 396;
map.createPane('searchPlot');
map.getPane('searchPlot').style.zIndex = 398;

document.getElementById("originRadiusKm").onchange = function() {
    originCircle.setRadius(document.getElementById("originRadiusKm").value * 1e3);
};
document.getElementById("destinationRadiusKm").onchange = function() {
    destinationCircle.setRadius(document.getElementById("destinationRadiusKm").value * 1e3);
};
//document.getElementById("numberOfStops").onchange = function() {
//TODO: max 300km radius for 2 stops
//};
map.on('mouseup', () => { 
  map.dragging.enable();
  map.removeEventListener('mousemove');
});
originCircle = L.circle(initialOrigin, document.getElementById("originRadiusKm").value * 1e3, {
    color: 'blue',
    fillColor: '#00f',
    fillOpacity: 0.1,
    pane: 'radius'
});
destinationCircle = L.circle(initialDestination, document.getElementById("destinationRadiusKm").value * 1e3, {
    draggable: true,
    color: 'green',
    fillColor: '#0f0',
    fillOpacity: 0.1,
    pane: 'radius'
});
    L.DomEvent.on(originCircle, 'click', function(ev) {
        if (map.hasLayer(destinationCircle)) {
            flightSearch();
        }
        L.DomEvent.stopPropagation(ev);
    });
    L.DomEvent.on(destinationCircle, 'click', function(ev) {
        if (map.hasLayer(originCircle)) {
            flightSearch();
        }
        L.DomEvent.stopPropagation(ev);
    });

originCircle.on('mousedown', function(event) {
    if (!map.hasLayer(destinationCircle)) {
        return;
    }
    map.dragging.disable();
    let {
        lat: circleStartingLat,
        lng: circleStartingLng
    } = originCircle._latlng;
    let {
        lat: mouseStartingLat,
        lng: mouseStartingLng
    } = event.latlng;

    map.on('mousemove', event => {
        let {
            lat: mouseNewLat,
            lng: mouseNewLng
        } = event.latlng;
        let latDifference = mouseStartingLat - mouseNewLat;
        let lngDifference = mouseStartingLng - mouseNewLng;

        let center = [circleStartingLat - latDifference, circleStartingLng - lngDifference];
        originCircle.setLatLng(center);
    });
});

destinationCircle.on('mousedown', function(event) {
    if (!map.hasLayer(originCircle)) {
        return;
    }
    map.dragging.disable();
    let {
        lat: circleStartingLat,
        lng: circleStartingLng
    } = destinationCircle._latlng;
    let {
        lat: mouseStartingLat,
        lng: mouseStartingLng
    } = event.latlng;

    map.on('mousemove', event => {
        let {
            lat: mouseNewLat,
            lng: mouseNewLng
        } = event.latlng;
        let latDifference = mouseStartingLat - mouseNewLat;
        let lngDifference = mouseStartingLng - mouseNewLng;

        let center = [circleStartingLat - latDifference, circleStartingLng - lngDifference];
        destinationCircle.setLatLng(center);
    });
});

var searchPlot = L.geoJSON(null, {
    pane: 'searchPlot',
    style: function (feature) {
        return {
            weight: 2.5,
            opacity: 1,
            color: 'darkorange',
        };
    }
});

function flightSearch(e) {
    var data = {
        destination: destinationCircle.getLatLng(),
        origin: originCircle.getLatLng(),
        destinationRadius: destinationCircle.getRadius(),
        originRadius: originCircle.getRadius(),
        numberOfStops: document.getElementById("numberOfStops").value,
        filterAirlineAlliance: document.getElementById("filterAirlineAlliance").value
    }
    var xhr = new XMLHttpRequest();
    xhr.open('POST', './api/geojson/flightsearch');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            var routes_info = JSON.parse(xhr.responseText);
            if (typeof routes_info.features === 'undefined') {} else {
                searchPlot.clearLayers();
                turf.meta.segmentEach(routes_info, function(currentSegment, featureIndex, multiFeatureIndex, geometryIndex, segmentIndex) {
                    var start = currentSegment.geometry.coordinates[0];
                    var end = currentSegment.geometry.coordinates[1];
                    var distance = turf.distance(start, end);
                    if (distance > 0)
                        searchPlot.addData(turf.greatCircle(start, end, {
                            npoints: Math.round(distance * 0.009),
                            offset: 10
                        }));
                });
                searchPlot.addTo(map);
            }
        }
    };
    xhr.send(JSON.stringify(data));
}

function clickMap(eo) {
    if (!putCircle(eo)) {
        info.reset();
    }
}

function clickAirport(eo) {
    if (!putCircle(eo)) {
        routesInfo(eo.target.feature.properties);
    }
}

function putCircle(eo) {
    if (!map.hasLayer(originCircle)) {
        originCircle.setLatLng(eo.latlng).addTo(map);
        document.getElementById("helptext").innerHTML =
            'Select destination! <button onclick="resetMap()">reset</button>'
    }
    else if (!map.hasLayer(destinationCircle)) {
        destinationCircle.setLatLng(eo.latlng).addTo(map);
        document.getElementById("helptext").innerHTML =
            '<button onclick="flightSearch()">search</button>' +
            '<button onclick="resetMap()">reset</button>'
    }
    else {
        return false;
    }
        L.DomEvent.stopPropagation(eo);
        return true;
}

function resetMap() {
    map.removeLayer(searchPlot);
    map.removeLayer(destinationCircle);
    map.removeLayer(originCircle);
    document.getElementById("helptext").innerHTML = "Click for your origin!"
}
