var prediction=document.getElementById("prediction-time");
function displayPrediction(station) {
    date = document.getElementById("date").value
    time = document.getElementById("time").value
    var prediction_before=document.getElementById("predictionInfo");
    prediction.removeChild(prediction_before);
    fetch("/get_prediction/"+station.number+"/"+String(date) +"T" + time).then (response => {
        return response.json();
    }).then(prediction => {
        var predictionInfo = document.createTextNode('<h3>'  + time + '</h3><h3>Estimated Bikes: ' + prediction + "</h3>");
        predictionInfo.id="predictionInfo";
        prediction.appendChild(predictionInfo);
    });
}