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
        //station_list is the list to store all the station names
        var station_list = [];
        //position_list is the list to store all the station position
        var position_list = [];
        //station_option is to store all the options for route planning
        var station_option="<option value=''> </option>";
        var user_input = document.getElementsByClassName("input")[0];
        var SelectedStation = document.getElementById("SelectedStation");
//Makes Map
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
                center: { lat: DUBLIN_LAT, lng: DUBLIN_LNG },
                zoom: 14,
                disableDefaultUI: true,
            });
    //Create an info window to share between markers
    const stationWindow= new google.maps.InfoWindow();
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
                        station_list.push(station.name);
                        position_list.push(station.latitude+","+station.longitude)
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
                                                    + '</h2><ul><li>Status' + availability.status
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
                        document.getElementById("start").innerHTML=station_option;
                        document.getElementById("end").innerHTML=station_option;
                    }
                }) 
            });
        }).catch(err => {
            console.log("error:",err);
        });
    }).catch(err => {
        console.log("error:",err);
    })
    //Get location with google map geolocation api
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
                    locationWindow.setPosition(pos);
                    locationWindow.setContent("Location found.");
                    locationWindow.open(map);
                    map.setCenter(pos);
               },() => {
                    handleLocationError(true, locationWindow, map.getCenter());
                     });
           } else {
               // Browser doesn't support Geolocation
               handleLocationError(false, locationWindow, map.getCenter());
           }
      });
      //Calculate And Display Route with google direction API
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
//Handle Location Error
function handleLocationError(browserHasGeolocation, locationWindow, pos) {
        locationWindow.setPosition(pos);
        locationWindow.setContent(
            browserHasGeolocation
                    ? "Error: The Geolocation service failed."
                    : "Error: Your browser doesn't support geolocation."
        );
        locationWindow.open(map);
 }
//Calculate And Display Route with google direction API
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
 //Display Result when the user click on search bar
 user_input.onfocus = function(){
        var stationButtons = document.createElement("div");
        stationButtons.id = "buttons";
        SelectedStation.appendChild(stationButtons);
	    showResult();
}
//Display Result when the user is inputting
 user_input.oninput = function() {
        var buttons_before = document.getElementById("buttons");
	    SelectedStation.removeChild(buttons_before);
	    var stationButtons = document.createElement("div");
        stationButtons.id = "buttons";
        SelectedStation.appendChild(stationButtons);
        showResult();
}
//Delete the result when the user click on somewhere else
  user_input.onblur = function(){
         var buttons_before = document.getElementById("buttons");
         SelectedStation.removeChild(buttons_before);
}
//Create buttons that stands for the stations that the user is probably searching for
function showResult(){
         var result_index = searchForInput(user_input.value,station_list);
         for(var i=0;i<result_index.length;i++){
               var station_button = document.createElement("BUTTON");
               var index=result_index[i];
               var station_name = document.createTextNode(station_list[index]);
               station_button.appendChild(station_name);
               document.getElementById("buttons").appendChild(station_button);
          }
}
//Search for the stations that the user is probably searching for
function searchForInput(theInput, theList){
        if(theInput == ""){
    	      return [];
        }else{
              var search_input=theInput.toUpperCase();
	          var result_list = [];
	          for(var i=0;i<theList.length;i++){
	                 var index=theList[i].indexOf(search_input);
	                 if(index>=0){
	                      result_list.push(index);
	                 }
	           }
	           return result_list;
         }
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

// Hide the markers0.
        function hideMarkers() {
           for (let i = 0; i < markers0.length; i++) {
                  markers0[i].setMap(null);
           }
}
// Shows any markers0
        function showMarkers() {
           for (let i = 0; i < markers0.length; i++) {
                  markers0[i].setMap(map);
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


