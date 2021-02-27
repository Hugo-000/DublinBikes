import dbinfo
import APIinfo
import sqlalchemy as sqla
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
import requests
from datetime import datetime
import json
import time
import traceback

#Parses weather obtained from API request
def parseWeather(obj):
    return {'time' : datetime.fromtimestamp(int(obj['dt'])),
            'temp' : obj['temp'],
            'humidity' : obj ['humidity'],
            'description' : obj['weather'][0]['main']
        }

#stores data in weather database
def store_weather(json_data):
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    metadata = sqla.MetaData(bind=engine)
    weather = sqla.Table('weather', metadata, autoload=True)

    engine.execute(weather.insert(), parseWeather(json_data['current']))

#Begin program
url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (APIinfo.DUBLIN_LATITUDE, APIinfo.DUBLIN_LONGITUDE, APIinfo.WEATHER_APIKEY)

while True:
    try:
        response = requests.get(url)
        
        store_weather(json.loads(response.text))
        
        time.sleep(2*60*60)
    except:
        
        print(traceback.format_exc())