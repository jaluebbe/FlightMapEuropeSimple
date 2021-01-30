var map = L.map('map', {
    zoomSnap: 0.5,
    zoomDelta: 0.5
});
map.attributionControl.addAttribution(
    '<a href="https://github.com/jaluebbe/FlightMapEuropeSimple" target="_blank">Source on GitHub</a>');
// add link to an imprint and a privacy statement if the file is available.
function addPrivacyStatement() {
    var xhr = new XMLHttpRequest();
    xhr.open('HEAD', "./datenschutz.html");
    xhr.onload = function() {
        if (xhr.status === 200)
            map.attributionControl.addAttribution(
                '<a href="./datenschutz.html" target="_blank">Impressum & Datenschutzerkl&auml;rung</a>'
            );
    }
    xhr.send();
}
addPrivacyStatement();
if (L.Browser.mobile) {
    map.setView([52, 4.5], 3.5);
    map.removeControl(map.zoomControl);
} else {
    map.setView([52, 4.5], 4);
}
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    minZoom: 1,
    maxZoom: 15,
    attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        '&copy; <a href="https://carto.com/attributions">CARTO</a>',
}).addTo(map);
var layerControl = L.control.layers({}, {}, {
    collapsed: L.Browser.mobile, // hide on mobile devices
    position: 'topright',
    hideSingleBase: true
})
