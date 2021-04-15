File descriptions
============
app.py
The flask component of the application

test.py
The unit-test file for the flask component of the application

get_jcdecaux.py
A web-scraper that scrapes data from the JCdecaux API every
5 minutes and adds it to the RDS. Will not scrape
between 1:00am and 4:30am. Measures are in place to prevent
duplicate entries.

stations_to_db.py
A web scraper that collects static station data from the
JCDecaux API and adds it to the RDS.

get_weather.py
A web scraper that uses the OpenWeatherMap API to collect
the current weather for Dublin and store in the RDS every
30 minutes.

get_predictions.py
A web scraper that, every 24 hours, gets a forecast
for the next 7 days from the openweatherMap API and
replaces the previous forecast in the RDS

APIInfo.py
A series of constants to be used when accessing the JCDecaux
or OpenWeatherMap API.

dbinfo.py
A series of constants to be used to access the RDS database.

prediction_model.py
The prediction model used to predict the bikes available in
a dublin bike station at a later date.

Predictive_Model_Testing.ipynb
Jupyter notebook used for testing and evaluating various possible 
predictive models.

templates/map.html
The only html template used in this application. Is the main
and only page of the app.

static/scripts.js
The Javascript component of the main page of the application.
Was intended to be split into more modular components for
ease of reading but that did not get to happen.

static/style.css
The css file for map.html
