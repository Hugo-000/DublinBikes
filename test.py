from app import app
import unittest
import json
import datetime as dt

STATION_COUNT= 109

class FlaskTestCase(unittest.TestCase):

    #Ensure Map page loads
    def test_map_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    #Ensure get_stations loads    
    def test_get_station_loads(self):
        tester = app.test_client(self)
        response = tester.get('/get_stations', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    #Ensure get_stations loads all of the stations in the database  
    def test_get_station_count(self):
        tester = app.test_client(self)
        response = tester.get('/get_stations', content_type='html/text')
        data = json.loads(response.data)
        self.assertEqual(len(data), STATION_COUNT)

    #Ensure get_station data is in the correct format
    def test_get_station_format(self):
        tester = app.test_client(self)
        response = tester.get('/get_stations', content_type='html/text')
        data = json.loads(response.data)
        test = True
        expected_keys = ['number', 'name', 'address', 'latitude', 'longitude', 'banking', 'bonus']
        expected_types = ["<class 'int'>", "<class 'str'>", "<class 'str'>", "<class 'float'>", "<class 'float'>", "<class 'int'>", "<class 'str'>"]
        for row in data:
            types = [str(type(val)) for val in row.values()]

            if (list(row.keys()) != expected_keys) or (types != expected_types):
                test = False
                break

        self.assertTrue(test)


    #Ensure get_weather loads    
    def test_get_weather_loads(self):
        tester = app.test_client(self)
        response = tester.get('/get_weather', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    #Ensure get_weather data is in the correct format
    def test_get_weather_format(self):
        tester = app.test_client(self)
        response = tester.get('/get_weather', content_type='html/text')
        data = json.loads(response.data)
        test = True
        expected_keys = ['time', 'temp', 'humidity', 'main', 'description', 'wind_speed', 'visibility', 'icon']
        expected_types = ["<class 'int'>", "<class 'float'>", "<class 'int'>", "<class 'str'>", "<class 'str'>", "<class 'float'>", "<class 'int'>", "<class 'str'>"]
        types = [str(type(val)) for val in data[0].values()]

        if (list(data[0].keys()) != expected_keys) or (types != expected_types):
            test = False

        self.assertTrue(test)

    #Ensure get_availability loads    
    def test_get_availability_loads(self):
        tester = app.test_client(self)
        response = tester.get('/get_availability', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    #Ensure get_availability provides data for all stations   
    def test_get_availability_count(self):
        tester = app.test_client(self)
        response = tester.get('/get_availability', content_type='html/text')
        data = json.loads(response.data)
        self.assertEqual(len(data), STATION_COUNT)

    def test_get_availability_format(self):
        tester = app.test_client(self)
        response = tester.get('/get_availability', content_type='html/text')
        data = json.loads(response.data)
        test = True
        expected_keys = ['number', 'status', 'bike_stands', 'available_bike_stands', 'available_bikes', 'last_update', 'mechanical_bikes', 'electrical_bikes', 'electrical_internal_battery_bikes', 'electrical_removable_battery_bikes']
        expected_types = ["<class 'int'>", "<class 'str'>", "<class 'int'>", "<class 'int'>", "<class 'int'>", "<class 'int'>", "<class 'int'>", "<class 'int'>", "<class 'int'>", "<class 'int'>"]
        for row in data:
            types = [str(type(val)) for val in row.values()]

            if (list(row.keys()) != expected_keys) or (types != expected_types):
                test = False
                break

        self.assertTrue(test)

    #Ensure get_availability loads for specific stations    
    def test_get_availability_station_no_loads(self):
        tester = app.test_client(self)
        response = tester.get('/get_availability/2', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    #Ensure get_availability data is valid for specific stations   
    def test_get_availability_station_no_format(self):
        tester = app.test_client(self)
        response = tester.get('/get_availability/2', content_type='html/text')
        data = json.loads(response.data)
        test = True
        expected_keys = ['available_bikes', 'available_bike_stands', 'last_update']
        expected_types = ["<class 'float'>", "<class 'float'>", "<class 'int'>"]
        for row in data:
            types = [str(type(val)) for val in row.values()]

            if (list(row.keys()) != expected_keys): #or (types != expected_types):
                test = False
                break

        self.assertTrue(test)

    #Ensure get_prediction loads for specific stations and time
    def test_get_prediction_loads(self):
        tester = app.test_client(self)
        tomorrow = dt.date.today()
        tomorrow += dt.timedelta(days=1)
        response = tester.get('/get_prediction/2/{}T06:00'.format(tomorrow.strftime('%Y-%m-%d')), content_type='html/text')
        self.assertEqual(response.status_code, 200)

    #Ensure get_prediction data is in a valid format
    def test_get_prediction_format(self):
        tester = app.test_client(self)
        tomorrow = dt.date.today()
        tomorrow += dt.timedelta(days=1)
        response = tester.get('/get_prediction/2/{}T06:00'.format(tomorrow.strftime('%Y-%m-%d')), content_type='html/text')
        data = json.loads(response.data)
        expected_types = ["<class 'int'>", "<class 'str'>", "<class 'float'>"]
        types = [str(type(val)) for val in data]
        self.assertEqual(types, expected_types)
     
    #Test if correct error message shown when a station that doesn't exist is requested   
    def test_get_prediction_wrong1(self):
        tester = app.test_client(self)
        tomorrow = dt.date.today()
        tomorrow += dt.timedelta(days=1)
        response = tester.get('/get_prediction/1/{}T06:00'.format(tomorrow.strftime('%Y-%m-%d')), content_type='html/text')
        data = json.loads(response.data)
        self.assertEqual(data[0], 'Error: Predictive Model not Found')
    
    #Test if correct error message shown when a time we don't have data for is requested
    def test_get_prediction_wrong2(self):
        tester = app.test_client(self)
        day = dt.date.today()
        day -= dt.timedelta(days=3)
        response = tester.get('/get_prediction/2/{}T06:00'.format(day.strftime('%Y-%m-%d')), content_type='html/text')
        data = json.loads(response.data)
        self.assertEqual(data[0], 'Error: Weather Data Not Found')
    
if __name__ == '__main__':
    unittest.main() 