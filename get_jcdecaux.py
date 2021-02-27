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

#Parses data received. fixes n/a timestamps
def parseData(obj):
    try:
        date = datetime.fromtimestamp(int(obj['last_update']/1e3))
    except:
        date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return{'number': obj['number'],
        'status' : obj['status'],
        'bike_stands': obj['bike_stands'],
        'available_bike_stands': obj['available_bike_stands'],
        'available_bikes': obj['available_bikes'],
        'last_update': date
          }

#store json_data in database
def store_to_db(json_data):
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    metadata = sqla.MetaData(bind=engine)
    availability = sqla.Table('availability', metadata, autoload=True)

    for station in json_data:
        try:
            engine.execute(availability.insert(), parseData(station))
        except sqla.exc.IntegrityError:
            pass
        
while True:
    try:
        response = requests.get(APIinfo.BIKE_URI, params={"apiKey": APIinfo.BIKE_APIKEY, "contract": APIinfo.BIKE_CONTRACT})
        
        store_to_db(json.loads(response.text))
        
        time.sleep(5*60)
    except:
        
        print(traceback.format_exc())
        