DUBLIN_LAT = 53.349804;
DUBLIN_LNG = -6.260310;

let map;

//Makes Map
function initMap() {
    fetch("/get_availability").then(response =>{   
        return response.json();   
    }).then(availability_data => {  
    
        fetch("/get_stations").then(response => {
            return response.json();
        }).then(stations => {
            
            map = new google.maps.Map(document.getElementById("map"), {
                center: { lat: DUBLIN_LAT, lng: DUBLIN_LNG },
                zoom: 14,
            });


            stations.forEach(station => {
                const marker = new google.maps.Marker({
                    position: {lat: station.latitude, lng: station.longitude},
                    map: map,
                });

                availability_data.forEach(data => {



                    if (station.number == data.number) {

                        marker.addListener("click", () => {
                            displayInfo(map, marker, station, data)
                            makeGraphs(station)
                        });
                    }
                })
                
            });
        }).catch(err => {
            console.log("error:",err);
        });



    }).catch(err => {
        console.log("error:",err);
    })
}

//Creates and Displays Info Window
function displayInfo(map, marker, station, data) {
<<<<<<< Upstream, based on Primary
<<<<<<< Upstream, based on Primary
=======

>>>>>>> 8a41d7e function implemented to display availability charts when marker clicked
=======
>>>>>>> 24a2a97 Fixed Infowindow Problem
    const infowindow = new google.maps.InfoWindow({
        content: '<h1>Station ' + station.number + '</h1><h2>' + station.address +'</h2>'
            + '<ul><li>' + data.status + '</li>'
            + '<li>' + station.banking +  '</li>'
            + '<li>Bikes: ' +  data.available_bikes +'/' + data.bike_stands + '<ul>'
            + '<li>Mechanical: ' + data.mechanical_bikes
            + '<li>Electrical: ' + data.electrical_bikes + '<ul>'
            + '<li>Internal_Battery: ' + data.electrical_internal_battery_bikes + '</li>'
            + '<li>Removable_Battery: ' + data.electrical_removable_battery_bikes + '</li></ul></li></ul></li>'
            + '<li>Free Stands: ' + data.available_bike_stands +'/' + data.bike_stands + '</li>'
        });
        infowindow.open(map, marker);

}

//Creates Graph when given the Station
function makeGraphs(station){
    fetch("/get_availability/"+station.number).then(response => {
        return response.json();
    }).then(data => {

        var weekly_options = {
            title: station.name + ": Bike availability (Weekly)",
            explorer: {
                    actions: ['dragToZoom', 'rightClickToReset'],
                    axis: 'horizontal',
                    keepInBounds: true,
                    maxZoomIn: 4.0
            }
        }
        var chart = new google.visualization.LineChart(document.getElementById('Week_Charts'));
        var chart_data = new google.visualization.DataTable();
        chart_data.addColumn("datetime", "Date");
        chart_data.addColumn("number", "Bike Availability");
        chart_data.addColumn("number", "Bike Spaces");
        data.forEach(x=>{
                    chart_data.addRow([new Date(x.last_update),x.available_bikes,x.available_bike_stands]);
        })
        chart.draw(chart_data, weekly_options);
    });


}

//Fetches and Returns current Weather
function get_current_weather(id) {
    fetch("/get_weather").then(response => response.json())
        .then(function(data) {
        var content = "";
        var date = new Date(data[0]['time']);
        content = "<h2>" + data[0]['main'] + "</h2>" +
            "<ul><li>" + data[0]['description'] + 
            "</li><li>Temperature: " + data[0]['temp'] + 
            "C</li><li>Humidity: " + data[0]['humidity'] +
            "%</li><li>Visibility: " + data[0]['visibility'] + 
            "m</li><li>Wind Speed: " + data[0]['wind_speed'] +
            "m/s</li></ul><h4>Time Taken: " + date + "</h4>"
        document.getElementById(id).innerHTML = content;
    })
    .catch(err => {
        console.log("Unable to collect/format current weather data");
    })
}

get_current_weather("weather");


function initCharts(){
    google.charts.load('current',{'packages':['corechart']});
    google.charts.setOnLoadCallback(initMap);
    google.charts.load('current', {'packages':['bar']});
    }


