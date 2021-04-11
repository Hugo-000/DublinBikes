from flask import Flask, render_template, jsonify
#from jinja2 import Template
from sqlalchemy import create_engine
import pandas as pd
import dbinfo
import datetime as dt
import pytz
from functools import lru_cache
import pickle

app = Flask(__name__)

#for accessing map.html
@app.route("/")
def map():
    engine = create_engine(
        "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT,
                                                       dbinfo.DB), echo=True)
    df = pd.read_sql("SELECT max(time) FROM daily_predictions;", engine)
    now = dt.datetime.now(tz=pytz.timezone('Europe/Dublin'))
    maxTime = df.to_dict(orient='records')

    return render_template("map.html", maxTime=maxTime[0]['max(time)'], minTime=now)

#Returns JSON data of stations table
@app.route("/get_stations")
@lru_cache()
def stations():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql("SELECT * FROM stations", engine)
    return df.to_json(orient='records')#render_template("test.html", results = 'piss')

#Returns JSON of most recent weather data
@app.route("/get_weather")
@lru_cache()
def weather():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql(
        "SELECT * FROM weather WHERE time IN (SELECT max(time) FROM weather);",
        engine)
    return df.to_json(orient='records')

# Returns JSON data of most recent  availability data
@app.route("/get_availability")
@lru_cache()
def availability():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql("SELECT * FROM availability WHERE (number, last_update) in (select number, max(last_update) from dbbikes.availability group by number);", 
        engine)
    return df.to_json(orient='records')

#Gives One Week worth of data on a specific station
@app.route("/get_availability/<int:station_id>")
@lru_cache()
def week_availability(station_id):
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    now = dt.datetime.now(tz=pytz.timezone('Europe/Dublin'))
    df = pd.read_sql("SELECT last_update, available_bikes, available_bike_stands FROM availability WHERE number = {} and last_update >= date_add('{}', interval -5 DAY) order by last_update desc;".format(station_id, now), engine)
    resampled_df = df.set_index('last_update').resample('H').mean()
    resampled_df['last_update'] = resampled_df.index
    return resampled_df.to_json(orient='records')




@app.route("/get_prediction/<int:station_id>/<string:time>")
def prediction(station_id, time):
    engine = create_engine(
        "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT,
                                                       dbinfo.DB), echo=True)
    time = dt.datetime.strptime(time, "%Y-%m-%dT%H:%M")
    df = pd.read_sql("SELECT temp_day,humidity,wind_speed,main FROM daily_predictions WHERE date(time) = '{}'".format(time.date()), engine)
    weather = df.to_dict(orient='records')

    with open('Pickle_Files_Knn/scale_station_{}.pkl'.format(station_id), 'rb') as handle:
        scaled = pickle.load(handle)

    input = [(weather[0]['temp_day'] - scaled['temp'][0]) / scaled['temp'][1],
             (weather[0]['humidity'] - scaled['humidity'][0]) / scaled['humidity'][1],
             (weather[0]['wind_speed'] - scaled['wind_speed'][0]) / scaled['wind_speed'][1]]

    weather_type = [0] * 7
    if weather[0]['main'] == "Clear":
        weather_type[0] = 1
    elif weather[0]['main'] == "Clouds":
        weather_type[1] = 1
    elif weather[0]['main'] == "Drizzle":
        weather_type[2] = 1
    elif weather[0]['main'] == "Fog":
        weather_type[3] = 1
    elif weather[0]['main'] == "Mist":
        weather_type[4] = 1
    elif weather[0]['main'] == "Rain":
        weather_type[5] = 1
    elif weather[0]['main'] == "Snow":
        weather_type[6] = 1
    else:
        raise Exception("Weather of type {} Not accounted for".format(weather[0]['main']))

    hour = [0] * 19
    hour[time.hour - 5] = 1;

    day = [0] * 7
    day[time.weekday()] = 1

    input.extend(weather_type)
    input.extend(hour)
    input.extend(day)

    with open('Pickle_Files_Knn/Model_station_{}.pkl'.format(station_id), 'rb') as handle:
        model = pickle.load(handle)

    result = model.predict([input])
    result = int(result)

    return jsonify(result)  # placeholder


if __name__ == "__main__":
    app.run(host= "0.0.0.0", debug=True)
