map.createPane('firs');
map.getPane('firs').style.zIndex = 390;

var airspaceData;

function clickAirspace(eo) {
    return;
}

function styleAirspace(feature, styleProperties) {
    return styleProperties;
}

function onEachFeatureFir(feature, layer) {
    layer.on('click', function(eo) {
        clickAirspace(eo);
    });
    var tooltipContent =
        "" + feature.properties.AV_NAME +
        " (" + feature.properties.AV_AIRSPAC + ")<BR>FL" +
        feature.properties.MIN_FLIGHT + " to FL" +
        feature.properties.MAX_FLIGHT + "<BR>";
    layer.bindTooltip(tooltipContent, {
        sticky: true,
        direction: "top",
        offset: [0, -5]
    });
}

var upperAirspace = L.geoJSON([], {
    onEachFeature: onEachFeatureFir,
    pane: 'firs',
    filter: function(feature) {
        return ('upper'.includes(feature.properties.UL_VISIBLE))
    },
    style: function(feature) {
        if (feature.properties.UL_VISIBLE == 'upper') {
            return styleAirspace(feature, {
                fillColor: "#003399",
                fillOpacity: 0.1,
                weight: 1.5,
                color: "grey"
            });
        }
    }
});

var lowerAirspace = L.geoJSON([], {
    onEachFeature: onEachFeatureFir,
    pane: 'firs',
    filter: function(feature) {
        return ('lower'.includes(feature.properties.UL_VISIBLE))
    },
    style: function(feature) {
        return styleAirspace(feature, {
            fillColor: "#ffcc00",
            fillOpacity: 0.15,
            weight: 1.5,
            color: "grey"
        });
    }
}).addTo(map);

var singleAirspace = L.geoJSON([], {
    onEachFeature: onEachFeatureFir,
    pane: 'firs',
    filter: function(feature) {
        return ('both'.includes(feature.properties.UL_VISIBLE))
    },
    style: function(feature) {
        return styleAirspace(feature, {
            fillColor: "#00ee00",
            fillOpacity: 0.1,
            weight: 1.5,
            color: "grey"
        });
    }

}).addTo(map);

var lowerAirspaceLabel = "<span style='background-color:rgba(255, 204, 0, 0.2)'>Lower Airspace (FIRs)</span>";
var upperAirspaceLabel = "<span style='background-color:rgba(0, 51, 153, 0.2)'>Upper Airspace (UIRs)</span>";
var singleAirspaceLabel = "<span style='background-color:rgba(0, 238, 0, 0.2)'>Airspaces (FIR/UIR)</span>";
layerControl.addOverlay(lowerAirspace, lowerAirspaceLabel);
layerControl.addOverlay(upperAirspace, upperAirspaceLabel);
layerControl.addOverlay(singleAirspace, singleAirspaceLabel);
layerControl.addTo(map);

function reloadAircraftPositions() {
    return;
}
// For regions where upper airspaces (UIR) as well as lower airspaces (FIR)
// exist, shapes are treated as baselayers to allow a choice by radio buttons.
// To make upperAirspace and lowerAirspace mutually exclusive the setTimeout
// is needed to keep the 'overlayadd' event from firing multiple times.
map.on('overlayadd', function(eo) {
    if (eo.name === lowerAirspaceLabel) {
        setTimeout(function() {
            map.removeLayer(upperAirspace);
            reloadAircraftPositions();
        }, 10);
    } else if (eo.name === upperAirspaceLabel) {
        setTimeout(function() {
            map.removeLayer(lowerAirspace);
            reloadAircraftPositions();
        }, 10);
    }
});
function refreshAirspaces() {
    if (typeof airspaceData === 'undefined') {
        return
    }
    lowerAirspace.clearLayers();
    lowerAirspace.addData(airspaceData);
    upperAirspace.clearLayers();
    upperAirspace.addData(airspaceData);
    singleAirspace.clearLayers();
    singleAirspace.addData(airspaceData);
}

function loadFirUirShapes(shapefile) {
    if (!shapefile) shapefile = './flightmap_europe_fir_uir.json';
    var xhr = new XMLHttpRequest();
    xhr.open('GET', shapefile);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            airspaceData = JSON.parse(xhr.responseText);
            refreshAirspaces();
        }

    };
    xhr.send();
}
