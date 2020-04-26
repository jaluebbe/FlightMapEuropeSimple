var flightStatistics;
var firUirStatistics;
var selection = new Set();
var data = [];
var names = [];
var show_percentage = false;
var d3colors = Plotly.d3.scale.category10();
var firColors = new Map();

function plotStatistics() {
    data.length = 0;
    firColors.clear();
    var i = 0;
    selection.forEach(function(airspace) {
        var firUirData = firUirStatistics[airspace];
        data.push({
            x: firUirData.Dates,
            y: show_percentage ? firUirData.percentage : firUirData.FlightsDetected,
            name: "" + names[airspace] +
                "<br>(" + airspace + ")",
            type: 'scatter'
        });
        firColors.set(airspace, d3colors(i));
        i++;
    });
    if (selection.size == 0) {
        data.push({
            x: flightStatistics.Dates,
            y: show_percentage ? flightStatistics.percentage : flightStatistics.FlightsDetected,
            name: "the world",
            type: 'scatter'
        })
    }
    var percent_icon = {
        svg: '<svg id="レイヤー_1" data-name="レイヤー 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 325.98 283.46"><defs><style>.cls-1{fill:#231815;}</style></defs><title>%Logo</title><path class="cls-1" d="M330.07,155a72.29,72.29,0,1,0,72.29,72.29A72.29,72.29,0,0,0,330.07,155Zm0,109.14a36.85,36.85,0,1,1,36.85-36.85A36.85,36.85,0,0,1,330.07,264.12Z" transform="translate(-257.79 -154.98)"/><path class="cls-1"    d="M511.49,293.88a72.29,72.29,0,1,0,72.28,72.28A72.28,72.28,0,0,0,511.49,293.88Zm0,109.13a36.85,36.85,0,1,1,36.85-36.85A36.85,36.85,0,0,1,511.49,403Z" transform="translate(-257.79 -154.98)"/><polygon class="cls-1" points="240.61 0 42.12 283.46 85.38 283.46 283.86 0 240.61 0"/></svg>'
    };
    var config = {
        modeBarButtonsToAdd: [{
                name: show_percentage ? 'show absolute values' : 'show percentages',
                icon: show_percentage ? Plotly.Icons.pencil : percent_icon,
                click: function(gd) {
                    show_percentage = !show_percentage;
                    plotStatistics()
                }
            },
            {
                name: 'reset selection to world view',
                icon: Plotly.Icons.undo,
                click: function(gd) {
                    selection.clear();
                    plotStatistics()
                    refreshAirspaces();
                }
            },
        ],
        modeBarButtonsToRemove: [
            'select2d', 'lasso2d', 'toggleSpikelines', 'zoomIn2d',
            'zoomOut2d', 'resetScale2d', 'hoverClosestCartesian',
            'hoverCompareCartesian'
        ],
        displaylogo: false,
        responsive: true,
        displayModeBar: true
    };
    var layout = {
        margin: {
            t: 20,
            r: 0,
            b: 0,
            l: 0
        },
        xaxis: {
            automargin: true,
            title: {
                text: 'Date (UTC)',
                standoff: 15
            }
        },
        yaxis: {
            automargin: true,
            title: {
                text: show_percentage ? 'Airline flights (%)' : 'Airline flights',
                standoff: 20
            },
            rangemode: 'tozero',
        },
        showlegend: !L.Browser.mobile
    };
    Plotly.react('statistics', data, layout, config);
}

function clickAirspace(eo) {
    if (typeof firUirStatistics === 'undefined') {
        console.error('statistical data not available yet.');
        return;
    }
    var feature = eo.target.feature;
    names[feature.properties.AV_AIRSPAC] = feature.properties.AV_NAME;
    if (selection.has(feature.properties.AV_AIRSPAC)) {
        selection.delete(feature.properties.AV_AIRSPAC);
    } else if (selection.size < 10) {
        selection.add(feature.properties.AV_AIRSPAC);
    } else {
        console.error('Selection too large. Unselect airspaces or reset selection.');
    }
    plotStatistics();
    refreshAirspaces();
}

function styleAirspace(feature, styleProperties) {
    if (selection.has(feature.properties.AV_AIRSPAC)) {
        styleProperties.fillColor = firColors.get(feature.properties.AV_AIRSPAC);
        styleProperties.fillOpacity = 0.4;
    }
    return styleProperties;
}

function loadFirUirStatistics(url='./static/fir_uir_statistics.json') {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            firUirStatistics = JSON.parse(xhr.responseText);
        }
    };
    xhr.send();
}

function loadFlightStatistics(url='./static/flights_statistics.json') {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            flightStatistics = JSON.parse(xhr.responseText);
            plotStatistics();
        }
    };
    xhr.send();
}
