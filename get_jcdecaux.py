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

engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)

def main():
    while True:
        try:
            now = datetime.now(tz=pytz.timezone('Europe/Dublin')).time()
            if now >= dt.time(4,30) or now <= dt.time(0,30):#Don't scrape when closed
                #get data
                response = requests.get(APIinfo.BIKE_URI, params={"apiKey": APIinfo.BIKE_APIKEY, "contract": APIinfo.BIKE_CONTRACT})
                #store data
                store_to_db(json.loads(response.text))
        
            #wait
            time.sleep(5*60)
        except:
        
            print(traceback.format_exc())
        

#Parses data received. fixes n/a timestamps
def parseData(obj):
    try:
        date = datetime.fromtimestamp(int(obj['last_update']/1e3))
    except: #If last_update timestamp invalid, replace with current time.
        return None
    return{'number': obj['number'],
        'status' : obj['status'],
        'bike_stands': obj['bike_stands'],
        'available_bike_stands': obj['available_bike_stands'],
        'available_bikes': obj['available_bikes'],
        'last_update': date
          }

#store bike data in database
def store_to_db(json_data):
    metadata = sqla.MetaData(bind=engine)
    availability = sqla.Table('availability', metadata, autoload=True)

    for station in json_data:
        station_data = parseData(station)
        if station_data != None:
            try:
                engine.execute(availability.insert(), station_data)
            except sqla.exc.IntegrityError as ie:
                pass
        
main()
        