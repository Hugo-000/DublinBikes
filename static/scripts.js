DUBLIN_LAT = 53.349804;
DUBLIN_LNG = -6.260310;

        let map;
        //markers0 is the stations that banking=0
        let markers0 = [];
        let markers1 = [];
        //markers_label is the availability
        var markers0_label_bikes=[];
        var markers0_label_spaces=[];
        var markers0_label_e_bikes=[];
        var markers1_label_bikes=[];
        var markers1_label_spaces=[];
        var markers1_label_e_bikes=[];
        //station_list is used for the datalist
        var station_list ='<input list="station_datalist" class="input"  id="search_datalist" ><datalist id="station_datalist">';
        //station_option is to store all the options for route planning
        var station_option="<option value=''> </option>";
	const DUBLIN_BOUNDS = {
            north: 53.4,
            south: 53.3,
            west: -6.3103,
            east: -6.2305,
        };
//Makes Map
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
                center: { lat: DUBLIN_LAT, lng: DUBLIN_LNG },
                zoom: 14,
	    	restriction: {
                            latLngBounds: DUBLIN_BOUNDS,
                            strictBounds: false,
                        },
                disableDefaultUI: true,
		//The map style is learnt from Google map style Night Mode sample
                styles: [
                            {elementType: "geometry", stylers: [{ color: "#242f3e" }]},
                            {elementType: "labels.text.stroke",stylers: [{ color: "#242f3e" }]},
                            {elementType: "labels.text.fill",stylers: [{ color: "#746855" }]},
                            {featureType: "administrative.locality",elementType: "labels.text.fill",stylers: [{ color: "#d59563" }]},
                            {featureType: "poi",elementType: "labels.text.fill",stylers: [{ color: "#d59563" }]},
                            {featureType: "poi.park",elementType: "geometry",stylers: [{ color: "#263c3f" }]},
                            {featureType: "poi.park",elementType: "labels.text.fill",stylers: [{ color: "#6b9a76" }]},
                            {featureType: "road",elementType: "geometry",stylers: [{ color: "#38414e" }]},
                            {featureType: "road",elementType: "geometry.stroke",stylers: [{ color: "#212a37" }]},
                            {featureType: "road",elementType: "labels.text.fill",stylers: [{ color: "#9ca5b3" }]},
                            {featureType: "road.highway",elementType: "geometry",stylers: [{ color: "#746855" }]},
                            {featureType: "road.highway",elementType: "geometry.stroke",stylers: [{ color: "#1f2835" }]},
                            {featureType: "road.highway",elementType: "labels.text.fill",stylers: [{ color: "#f3d19c" }]},
                            {featureType: "transit",elementType: "geometry",stylers: [{ color: "#2f3948" }]},
                            {featureType: "transit.station",elementType: "labels.text.fill",stylers: [{ color: "#d59563" }]},
                            {featureType: "water",elementType: "geometry",stylers: [{ color: "#17263c" }]},
                            {featureType: "water",elementType: "labels.text.fill",stylers: [{ color: "#515c6d" }]},
                            {featureType: "water",elementType: "labels.text.stroke",stylers: [{ color: "#17263c" }]},
                        ],	    
            });
    //Create an info window to share between markers
    const stationWindow= new google.maps.InfoWindow();
    //Create a search window to display the search result
    const geocoder = new google.maps.Geocoder();
    const searchwindow = new google.maps.InfoWindow();
    //Match the Markers with corresponding information
    fetch("/get_availability").then(response =>{   
        return response.json();   
    }).then(availability_data => {  
        fetch("/get_stations").then(response => {
            return response.json();
        }).then(stations => {
            stations.forEach(station => {
                availability_data.forEach(availability => {
                    if (station.number == availability.number) {
                        station_option+="<option value='"+station.latitude+","+station.longitude+"'>"+station.name+"</option>";
                        station_list+='<option value="'+station.name+'" data-value="'+station.latitude+','+station.longitude+'">';
                        const marker = new google.maps.Marker({
                            position: {lat: station.latitude, lng: station.longitude},
                            map: map,
                            title:station.name,
                            label: `${availability.available_bikes}`,
                            optimized: false,
                        });
                        marker.addListener("click", () => {
                            stationWindow.close();
                            pay_terminal = station.banking ? "Yes" : "No";
                            var station_info='<h1>Station ' + station.number + '</h1><h2>' + station.address
                                                    + '</h2><ul><li>Status: ' + availability.status
                                                    + '</li><li>Banking' + pay_terminal
                                                    + '</li><li>Bikes: ' +  availability.available_bikes
                                                    + '<ul><li>Mechanical: ' + availability.mechanical_bikes
                                                    + '<li>Electrical: ' + availability.electrical_bikes
                                                    + '<ul><li>Internal_Battery: ' + availability.electrical_internal_battery_bikes
                                                    + '</li><li>Removable_Battery: ' + availability.electrical_removable_battery_bikes
                                                    + '</li></ul></li></ul></li><li>Stands: ' + availability.available_bike_stands +'/' + availability.bike_stands + '</li>';
                            stationWindow.setContent(station_info);
                            stationWindow.open(marker.getMap(), marker);
                            makeGraphs(station);
                        });
                        if (station.banking == "1"){
                                markers1.push(marker);
                                markers1_label_bikes.push(String(availability.available_bikes));
                                markers1_label_spaces.push(String(availability.available_bike_stands));
                                markers1_label_e_bikes.push(String(availability.electrical_bikes));
                        } else {
                                markers0.push(marker);
                                markers0_label_bikes.push(String(availability.available_bikes));
                                markers0_label_spaces.push(String(availability.available_bike_stands));
                                markers0_label_e_bikes.push(String(availability.electrical_bikes));
                        }
                    }
                }) 
            });
	station_list+='</datalist>';
        document.getElementById("search_bar_datalist").innerHTML=station_list;
	document.getElementById("start").innerHTML=station_option;
        document.getElementById("end").innerHTML=station_option;	
        }).catch(err => {
            console.log("error:",err);
        });
    }).catch(err => {
        console.log("error:",err);
    })
    //Get location with google map geolocation api, this function is learnt from Google map geolocation API sample
    locationWindow = new google.maps.InfoWindow();
    const locationButton = document.createElement("button");
    locationButton.textContent = "Move to Current Location";
    locationButton.classList.add("custom-map-control-button");
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(
                locationButton
            );
    locationButton.addEventListener("click", () => {
          if (navigator.geolocation) {
               navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const pos = {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude,
                        };
                    //Due to the area is restricted, there needs to check if the user is in the area
                    if (position.coords.latitude>53.365||position.coords.latitude<53.325||position.coords.longitude>-6.2307||position.coords.longitude<-6.3101){
                            handleLocationError("type1", locationWindow, map.getCenter());
                    }else{
                            locationWindow.setPosition(pos);
                            locationWindow.setContent("Location found.");
                            locationWindow.open(map);
                            map.setCenter(pos);
                    }
               },() => {
                    handleLocationError("type2", locationWindow, map.getCenter());
                     });
           } else {
               // Browser doesn't support Geolocation
               handleLocationError("type3", locationWindow, map.getCenter());
           }
      });
      //Use google map geocoding API to find the search result, this function is learnt from Google map geocoding API sample
      document.getElementById("submit").addEventListener("click", () => {
                geocodeLatLng(geocoder, map, searchwindow);
            });
      //Calculate And Display Route with google direction API, this function is learnt from Google map direction API sample
      const directionsService = new google.maps.DirectionsService();
      const directionsRenderer = new google.maps.DirectionsRenderer();
      directionsRenderer.setMap(map);
      const onChangeHandler = function () {
           calculateAndDisplayRoute(directionsService, directionsRenderer);
      };
      document.getElementById("start").addEventListener("change", onChangeHandler);
      document.getElementById("end").addEventListener("change", onChangeHandler);
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
        chart_data.addColumn("number", "Bikes");
        chart_data.addColumn("number", "Free Spaces");
        data.forEach(x=>{
                    chart_data.addRow([new Date(x.last_update),x.available_bikes,x.available_bike_stands]);
        })
        chart.draw(chart_data, weekly_options);
    });
}
//Handle geoLocation Error
function handleLocationError(browserHasGeolocation, locationWindow, pos) {
        locationWindow.setPosition(pos);
        if (browserProblem=="type1"){
                var problem="Error: Currently there is no station near your position"
            }else{
                if (browserProblem=="type2"){
                    var problem="Error: The Geolocation service failed."
                }else{
                    var problem="Error: Your browser doesn't support geolocation."
                }
            }
        locationWindow.open(map);
 }
//Calculate And Display Route with google direction API, this function is learnt from Google map direction API sample
function calculateAndDisplayRoute(directionsService, directionsRenderer) {
       directionsService.route({
                origin: {query: document.getElementById("start").value,},
                destination: {query: document.getElementById("end").value,},
                travelMode: google.maps.TravelMode.BICYCLING,
       },(response, status) => {
                if (status === "OK") {
                    directionsRenderer.setDirections(response);
                } else {
                    window.alert("Directions request failed due to " + status);
                }
            }
        );
}
//Display the station the user is searching for on the map with google geocoding API, this function is learnt from Google map reverse geocoding sample
function geocodeLatLng(geocoder, map, searchwindow) {
                var searchInput=document.getElementById("search_datalist").value;
                if(!searchInput) return;
                var position= document.querySelector("#station_datalist"+" option[value='"+searchInput+"']").dataset.value;
                const latlngStr = position.split(",", 2);
                const latlng = {
                    lat: parseFloat(latlngStr[0]),
                    lng: parseFloat(latlngStr[1]),
                };
                geocoder.geocode({ location: latlng }, (results, status) => {
                    if (status === "OK") {
                        if (results[0]) {
                            map.setZoom(14);
                            const marker = new google.maps.Marker({
                                position: latlng,
                                map: map,
                                });
                            searchwindow.setContent(results[0].formatted_address);
                            searchwindow.open(map, marker);
                        } else {
                            window.alert("No results found");
                        }
                    } else {
                        window.alert("Geocoder failed due to: " + status);
                    }
                });
}
// Shows bikes availability on the marker
function show_available_bikes() {
       for (let i = 0; i < markers1.length; i++) {
                  markers1[i].setLabel(markers1_label_bikes[i]);
        }
        for (let i = 0; i < markers0.length; i++) {
                  markers0[i].setLabel(markers0_label_bikes[i]);
        }
}
// Shows spaces availability on the marker
function show_available_spaces() {
           for (let i = 0; i < markers1.length; i++) {
                  markers1[i].setLabel(markers1_label_spaces[i]);
           }
           for (let i = 0; i < markers0.length; i++) {
                  markers0[i].setLabel(markers0_label_spaces[i]);
           }
}
 // Shows e-bikes availability on the marker
function show_available_e_bikes() {
           for (let i = 0; i < markers1.length; i++) {
                  markers1[i].setLabel(markers1_label_e_bikes[i]);
           }
           for (let i = 0; i < markers0.length; i++) {
                  markers0[i].setLabel(markers0_label_e_bikes[i]);
           }
}

// Show/Hide the markers0.
function showhideMarkers() {
            if(document.getElementById("banking_switch").checked == true){
                //Show markers0
                for (let i = 0; i < markers0.length; i++) {
                  markers0[i].setMap(map);
                }
                document.getElementById("banking_switch").checked = false;
            }else{
                //Hide markers0
                for (let i = 0; i < markers0.length; i++) {
                  markers0[i].setMap(null);
                }
                document.getElementById("banking_switch").checked = true;
            }
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


