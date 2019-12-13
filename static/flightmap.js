var map = L.map('map', {
    zoomSnap: 0.5,
    zoomDelta: 0.5
});
map.attributionControl.addAttribution(
    '<a href="https://github.com/jaluebbe/FlightMapEuropeSimple" target="_blank">Source on GitHub</a>');
// add link to an imprint and a privacy statement if the file is available.
function addPrivacyStatement() {
    var http = new XMLHttpRequest();
    http.open('HEAD', "./static/datenschutz.html");
    http.send();
    if (http.status != 404)
        map.attributionControl.addAttribution(
            '<a href="./static/datenschutz.html" target="_blank">Impressum & Datenschutzerkl&auml;rung</a>'
        );
}
addPrivacyStatement();
map.setView([52, 4.5], 6);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    minZoom: 1,
    maxZoom: 15,
    attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        '&copy; <a href="https://carto.com/attributions">CARTO</a>',
}).addTo(map);
if (L.Browser.mobile) {
    map.removeControl(map.zoomControl);
}
var layerControl = L.control.layers({}, {}, {
    collapsed: L.Browser.mobile, // hide on mobile devices
    position: 'topright',
    hideSingleBase: true
})
