function get_current_weather(id) {
    fetch("/weather").then(response => response.json())
        .then(function(data) {
        console.log(data[0]);
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
console.log('huh');