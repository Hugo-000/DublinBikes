import dbinfo
import APIinfo
import sqlalchemy as sqla
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
import requests
import datetime
import json
from telnetlib import DO
from _sqlite3 import IntegrityError

def parseData(obj):
    return{'number': obj['number'],
        'status' : obj['status'],
        'bike_stands': obj['bike_stands'],
        'available_bike_stands': obj['available_bike_stands'],
        'available_bikes': obj['available_bikes'],
        'last_update': datetime.datetime.fromtimestamp(int(obj['last_update']/1e3))
          }

r = requests.get(APIinfo.BIKE_URI, params={"apiKey": APIinfo.BIKE_APIKEY, "contract": APIinfo.BIKE_CONTRACT})
json_data = json.loads(r.text)


engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)

metadata = sqla.MetaData(bind=engine)
availability = sqla.Table('availability', metadata, autoload=True)

engine.execute(availability.insert(), *map(parseData, json_data))

#for station in json_data:
#    try:
#        engine.execute(availability.insert(), parseData(station))
#    except sqla.exc.IntegrityError as ie:
#        print(ie)