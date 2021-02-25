import dbinfo
import APIinfo
import sqlalchemy as sqla
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
import requests
import json

def stations_fix_keys(station):
    station['latitude'] = station['position']['lat']
    station['longitude'] = station['position']['lng']
    return station

r = requests.get(APIinfo.BIKE_URI, params={"apiKey": APIinfo.BIKE_APIKEY, "contract": APIinfo.BIKE_CONTRACT})
json_data = json.loads(r.text)

engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
metadata = sqla.MetaData(bind=engine)
stations = sqla.Table('stations', metadata, autoload=True)

#engine.execute(stations.insert(), *map(stations_fix_keys, json_data))

