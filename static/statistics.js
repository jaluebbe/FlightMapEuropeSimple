var flightStatistics;
var firUirStatistics;
var covidData;
var selection = new Set(["EGTTFIR", "LFFFFIR"]);
var data = [];
var worldData = [];
var names = {
    EGTTFIR: "LONDON FIR",
    LFFFFIR: "PARIS FIR"
};
var show_percentage = false;
var show_percentage_fir_uir = false;
var d3colors = d3.scale.category10();
var firColors = new Map();

function plotFirUirStatistics() {
    data.length = 0;
    firColors.clear();
    var i = 0;
    var gridSetting = undefined;
    selection.forEach(function(airspace) {
        var firUirData = firUirStatistics[airspace];
        data.push({
            x: firUirData.Dates,
            y: show_percentage_fir_uir ? firUirData.percentage : firUirData.FlightsDetected,
            name: "" + names[airspace],
            type: 'scatter'
        });
        firColors.set(airspace, d3colors(i));
        i++;
    });

    var percent_icon = {
        svg: '<svg id="レイヤー_1" data-name="レイヤー 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 325.98 283.46"><defs><style>.cls-1{fill:#231815;}</style></defs><title>%Logo</title><path class="cls-1" d="M330.07,155a72.29,72.29,0,1,0,72.29,72.29A72.29,72.29,0,0,0,330.07,155Zm0,109.14a36.85,36.85,0,1,1,36.85-36.85A36.85,36.85,0,0,1,330.07,264.12Z" transform="translate(-257.79 -154.98)"/><path class="cls-1"    d="M511.49,293.88a72.29,72.29,0,1,0,72.28,72.28A72.28,72.28,0,0,0,511.49,293.88Zm0,109.13a36.85,36.85,0,1,1,36.85-36.85A36.85,36.85,0,0,1,511.49,403Z" transform="translate(-257.79 -154.98)"/><polygon class="cls-1" points="240.61 0 42.12 283.46 85.38 283.46 283.86 0 240.61 0"/></svg>'
    };
    var config = {
        modeBarButtonsToAdd: [{
            name: show_percentage_fir_uir ? 'show absolute values' : 'show percentages',
            icon: show_percentage_fir_uir ? Plotly.Icons.pencil : percent_icon,
            click: function(gd) {
                show_percentage_fir_uir = !show_percentage_fir_uir;
                plotFirUirStatistics()
            }
        }],
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
        grid: gridSetting,
        xaxis: {
            automargin: true,
            range: ['2019-12-16', Date.now()],
            title: {
                text: 'Date (UTC)',
                standoff: 15
            }
        },
        yaxis: {
            automargin: true,
            title: {
                text: show_percentage_fir_uir ? 'Airline flights (%)' : 'Airline flights',
                standoff: 20
            },
            rangemode: 'tozero',
        },
        yaxis2: {
            automargin: true,
            title: {
                text: 'COVID-19',
                standoff: 20
            },
            type: 'log'
        },
        showlegend: !L.Browser.mobile
    };
    Plotly.react('fir_uir_statistics', data, layout, config);
}

function plotStatistics() {
    worldData.length = 0;
    var gridSetting = undefined;
    if (flightStatistics !== undefined) {
        worldData.push({
            x: flightStatistics.Dates,
            y: show_percentage ? flightStatistics.percentage : flightStatistics.FlightsDetected,
            name: "world flights",
            type: 'scatter'
        });
    }
    if (covidData !== undefined) {
        worldData.push({
            x: covidData.date,
            y: covidData.new_cases,
            name: "new cases",
            type: 'scatter',
            xaxis: 'x',
            yaxis: 'y2'
        });
        worldData.push({
            x: covidData.date,
            y: covidData.new_deaths,
            name: "new deaths",
            type: 'scatter',
            xaxis: 'x',
            yaxis: 'y2'
        });
        worldData.push({
            x: covidData.date,
            y: covidData.total_cases,
            name: "total cases",
            type: 'scatter',
            xaxis: 'x',
            yaxis: 'y2'
        });
        worldData.push({
            x: covidData.date,
            y: covidData.total_deaths,
            name: "total deaths",
            type: 'scatter',
            xaxis: 'x',
            yaxis: 'y2'
        });
        worldData.push({
            x: covidData.date,
            y: covidData.total_vaccinations,
            name: "total vaccinations",
            type: 'scatter',
            visible: 'legendonly',
            xaxis: 'x',
            yaxis: 'y2'
        });
        worldData.push({
            x: covidData.date,
            y: covidData.people_vaccinated,
            name: "people vaccinated",
            type: 'scatter',
            xaxis: 'x',
            yaxis: 'y2'
        });
        worldData.push({
            x: covidData.date,
            y: covidData.people_fully_vaccinated,
            name: "people fully vaccinated",
            type: 'scatter',
            xaxis: 'x',
            yaxis: 'y2'
        });
    }
    if (flightStatistics !== undefined && covidData !== undefined) {
        gridSetting = {
            rows: 2,
            columns: 1,
            subplots: [
                ['xy'],
                ['xy2']
            ]
        };
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
        }],
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
        grid: gridSetting,
        xaxis: {
            automargin: true,
            range: ['2019-12-16', Date.now()],
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
        yaxis2: {
            automargin: true,
            title: {
                text: 'COVID-19',
                standoff: 20
            },
            type: 'log'
        },
        showlegend: !L.Browser.mobile
    };
    Plotly.react('world_statistics', worldData, layout, config);

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
    plotFirUirStatistics();
    refreshAirspaces();
}

function styleAirspace(feature, styleProperties) {
    if (selection.has(feature.properties.AV_AIRSPAC)) {
        styleProperties.fillColor = firColors.get(feature.properties.AV_AIRSPAC);
        styleProperties.fillOpacity = 0.4;
    }
    return styleProperties;
}

function loadFirUirStatistics(url) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            firUirStatistics = JSON.parse(xhr.responseText);
            plotFirUirStatistics();
            refreshAirspaces();
        }
    };
    xhr.send();
}

function loadFlightStatistics(url) {
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

function loadCovidData(url) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            covidData = JSON.parse(xhr.responseText);
            plotStatistics();
        }
    };
    xhr.send();
}
