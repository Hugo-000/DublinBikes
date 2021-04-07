from flask import Flask, render_template, jsonify
#from jinja2 import Template
from sqlalchemy import create_engine
import pandas as pd
import dbinfo
import datetime as dt
import pytz
import pickle
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

#for accessing map.html
@app.route("/")
def map():
    return render_template("map.html")

@app.route("/prediction")
def predictive_map():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql("SELECT max(time) FROM daily_predictions;", engine)
    now = dt.datetime.now(tz=pytz.timezone('Europe/Dublin'))
    maxTime =  df.to_dict(orient='records')
    
    return render_template("prediction.html", maxTime = maxTime[0]['max(time)'], minTime = now)


#Returns JSON data of stations table
@app.route("/get_stations")
def stations():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql("SELECT * FROM stations", engine)
    return df.to_json(orient='records')#render_template("test.html", results = 'piss')

#Returns JSON of most recent weather data
@app.route("/get_weather")
def weather():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql(
        "SELECT * FROM weather WHERE time IN (SELECT max(time) FROM weather);",
        engine)
    return df.to_json(orient='records')

# Returns JSON data of most recent  availability data
@app.route("/get_availability")
def availability():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql("SELECT * FROM availability WHERE (number, last_update) in (select number, max(last_update) from dbbikes.availability group by number);", 
        engine)
    return df.to_json(orient='records')

#Gives One Week worth of data on a specific station
@app.route("/get_availability/<int:station_id>")
def week_availability(station_id):
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    now = dt.datetime.now(tz=pytz.timezone('Europe/Dublin'))
    df = pd.read_sql("SELECT * FROM availability WHERE number = {} and last_update >= date_add('{}', interval -7 DAY) order by last_update desc;".format(station_id, now), engine)
    return df.to_json(orient='records')

@app.route("/get_prediction/<int:station_id>/<string:time>")
def prediction(station_id, time):
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    time = dt.datetime.strptime(time, "%Y-%m-%dT%H:%M")
    df = pd.read_sql("SELECT * FROM daily_predictions WHERE date(time) = '{}'".format(time.date()), engine)
    weather = df.to_dict(orient='records')
    
    input = [weather[0]['temp_day'], weather[0]['humidity'], weather[0]['wind_speed']]
    
    weather_type = [0] * 7
    if weather[0]['main'] == "Clear": weather_type[0] = 1
    elif weather[0]['main'] == "Clouds": weather_type[1] = 1
    elif weather[0]['main'] == "Drizzle": weather_type[2] = 1
    elif weather[0]['main'] == "Fog": weather_type[3] = 1
    elif weather[0]['main'] == "Mist": weather_type[4] = 1
    elif weather[0]['main'] == "Rain": weather_type[5] = 1
    elif weather[0]['main'] == "Snow": weather_type[6] = 1
    else: raise Exception("Weather of type {} Not accounted for".format(weather[0]['main']))
    
    hour = [0] * 19
    hour[time.hour-5] = 1;
    
    day = [0] * 7
    day[time.weekday()] = 1
    
    input.extend(weather_type)
    input.extend(hour)
    input.extend(day)
    
    
    
    with open('Model_station2.pkl', 'rb') as handle:
        model = pickle.load(handle)
    
    result = model.predict([input])
    
    return jsonify(result[0]) # placeholder
if __name__ == "__main__":
    app.run(debug=True)
