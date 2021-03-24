from flask import Flask, render_template
#from jinja2 import Template
from sqlalchemy import create_engine
import pandas as pd
import dbinfo

app = Flask(__name__)

#Basic test template
@app.route("/")
def index():
    return render_template("test.html", name = 'test')

#for accessing map.html
@app.route("/map")
def map():
    return render_template("map.html")

#for accessing list.html
@app.route("/list")
def list():
    return render_template("list.html")

#Returns JSON data of stations table
@app.route("/stations")
def stations():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql("SELECT * FROM stations", engine)
    return df.to_json(orient='records')#render_template("test.html", results = 'piss')

#Returns JSON of most recent weather data
@app.route("/weather")
def weather():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql(
        "SELECT * FROM weather WHERE time IN (SELECT max(time) FROM weather);",
        engine)
    return df.to_json(orient='records')

# Returns JSON data of most recent  availability data
@app.route("/availability")
def availability():
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    df = pd.read_sql("SELECT * FROM availability WHERE (number, last_update) in (select number, max(last_update) from dbbikes.availability group by number);", 
        engine)
    return df.to_json(orient='records')
    
if __name__ == "__main__":
    app.run(debug=True)