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

def parseWeather(obj):
    return {'time' : datetime.fromtimestamp(int(obj['dt']/1e3)),
            'temp' : obj['temp'],
            'humidity' : obj ['humidity'],
            'description' : obj['weather'][0]['main']
        }

def store_weather(json_data):
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    metadata = sqla.MetaData(bind=engine)
    weather = sqla.Table('weather', metadata, autoload=True)

    engine.execute(weather.insert(), parseWeather(json_data['current']))



url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (DUBLIN_LATITUDE, DUBLIN_LONGITUDE, WEATHER_APIKEY)

while True:
    try:
        response = requests.get(url)
        
        store_weather(json_data)
        
        time.sleep(2*60*60)
    except:
        
        print(traceback.format_exc())