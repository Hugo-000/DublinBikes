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
        
            refresh_predictions(json.loads(response.text))
        
            time.sleep(24*60*60)
        except:
            print(traceback.format_exc())

#Parses weather prediction obtained from API request
def parsePrediction(obj):
    return {'time' : datetime.fromtimestamp(int(obj['dt'])),
            'sunrise': datetime.fromtimestamp(int(obj['sunrise'])),
            'sunset': datetime.fromtimestamp(int(obj['sunset'])),
            'temp_day' : obj['temp']['day'],
            'temp_night': obj['temp']['night'],
            'temp_eve' : obj['temp']['eve'],
            'temp_morn': obj['temp']['morn'],
            'humidity' : obj['humidity'],
            'wind_speed' : obj['wind_speed'],
            'main' : obj['weather'][0]['main'],
            'description' : obj['weather'][0]['description'],
            'icon': obj['weather'][0]['icon'],
        }

#updates weather_predictions
def refresh_predictions(json_data):
    metadata = sqla.MetaData(bind=engine)
    daily_predictions = sqla.Table('daily_predictions', metadata, autoload=True)

    engine.execute("delete from daily_predictions")
    for prediction in json_data['daily']:
        engine.execute(daily_predictions.insert(), parsePrediction(prediction))

main()