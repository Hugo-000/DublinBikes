from flask import Flask, render_template
#from jinja2 import Template
from sqlalchemy import create_engine
import pandas as pd
import dbinfo
import datetime as dt
import pytz

app = Flask(__name__)

#for accessing map.html
@app.route("/")
def map():
    return render_template("map.html")

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

if __name__ == "__main__":
    app.run(debug=True)