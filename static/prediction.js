DUBLIN_LAT = 53.349804;
DUBLIN_LNG = -6.260310;

let map;

function initMap() {
    fetch("/get_stations").then(response => {
        return response.json();
    }).then(stations => {
        map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: DUBLIN_LAT, lng: DUBLIN_LNG },
        zoom: 14,
        });
        
        var infoWindow = new google.maps.InfoWindow();
        
        stations.forEach(station => {
            const marker = new google.maps.Marker({
                position: {lat: station.latitude, lng: station.longitude},
                    map: map,
            });
            
            marker.addListener("click", () => {
                displayPrediction(map, marker, station, infoWindow)
            });
        });
    });
}

function displayPrediction(map, marker, station, infoWindow) {

    date = document.getElementById("date").value
    time = document.getElementById("time").value
    
    fetch("/get_prediction/"+station.number+"/"+String(date) +"T" + time).then (response => {
        return response.json();
    }).then(prediction => {
        /*infoWindow.setContent('<h3>'  + time + '</h3><h3>Estimated Bikes: ' + prediction + "</h3>");
        infoWindow.open(map, marker);*/
        console.log(prediction)
    });
    
}