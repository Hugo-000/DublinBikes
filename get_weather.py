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

url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (APIinfo.DUBLIN_LATITUDE, APIinfo.DUBLIN_LONGITUDE, APIinfo.WEATHER_APIKEY)
engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)

def main():
    while True:
        try:
            response = requests.get(url)
        
            store_weather(json.loads(response.text))
        
            time.sleep(30*60)
        except:
            print(traceback.format_exc())

#Parses weather obtained from API request
def parseWeather(obj):
    return {'time' : datetime.fromtimestamp(int(obj['dt'])),
            'temp' : obj['temp'],
            'humidity' : obj['humidity'],
            'wind_speed' : obj['wind_speed'],
            'main' : obj['weather'][0]['main'],
            'description' : obj['weather'][0]['description'],
            'visibility' : obj['visibility']
        }

#stores data in weather database
def store_weather(json_data):
    metadata = sqla.MetaData(bind=engine)
    weather = sqla.Table('weather', metadata, autoload=True)

    engine.execute(weather.insert(), parseWeather(json_data['current']))

main()