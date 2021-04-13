from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import dbinfo
from sklearn.preprocessing import StandardScaler
import pickle
from sklearn.neighbors import KNeighborsClassifier

unwanted = [14, 20, 35, 46, 60, 70, 81]
wanted = [x for x in range(111, 118)]
stations = [ele for ele in wanted if ele not in unwanted]

for station in stations:

    engine = create_engine(
        "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT,
                                                       dbinfo.DB), echo=True)
    df = pd.read_sql("SELECT available_bikes, last_update FROM availability WHERE number = {};".format(station),
                     engine)
    df.to_json(orient='records')

    engine = create_engine(
        "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT,
                                                       dbinfo.DB), echo=True)
    weather_df = pd.read_sql("SELECT * FROM weather;",
                             engine)
    weather_df.to_json(orient='records')

    # intervals of 30 minutes
    threshold_ns = 30 * 60 * 1e9

    # compute "interval" to which each update belongs
    df['interval'] = pd.to_datetime(np.round(df.last_update.astype(np.int64) / threshold_ns) * threshold_ns)
    weather_df['interval'] = pd.to_datetime(np.round(weather_df.time.astype(np.int64) / threshold_ns) * threshold_ns)

    # join dataframes together based on interval (inner join)
    merged_df = pd.merge(df, weather_df, how='inner', on='interval')

    # create column for hour and weekday based off of the interval
    merged_df['hour'] = list(map(lambda v: v.hour, merged_df['interval']))
    merged_df['weekday'] = list(map(lambda v: v.weekday(), merged_df['interval']))

    # dropping all rows between hours of 12AM to 5AM when the stations are closed
    # keeping these rows may skew results.
    merged_df = merged_df[merged_df['hour'] > 4]

    # changing categorical variables from type object to type category
    merged_df['main'] = merged_df['main'].astype('category')
    merged_df['hour'] = merged_df['hour'].astype('category')
    merged_df['weekday'] = merged_df['weekday'].astype('category')

    # converting categorical data into dummy or indicator variables
    dummy_columns = ['main', 'hour', 'weekday']
    for col in dummy_columns:
        dummies = pd.get_dummies(merged_df[col], prefix=col)
        merged_df = pd.concat([merged_df, dummies], axis=1)

    # dropping unused columns
    dropped_columns = ['last_update', 'time', 'description', 'icon', 'interval', 'main', 'hour', 'weekday',
                       'visibility']
    merged_df = merged_df.drop(dropped_columns, axis=1)

    # creating variables ansd target feature
    x = merged_df.drop('available_bikes', axis=1)
    y = merged_df['available_bikes']

    # standardising the continuous features before evaluation
    X_stand = x.copy()
    scaled = {}
    # numerical features
    num_cols = ['temp', 'humidity', 'wind_speed']
    # apply standardization on numerical features
    for i in num_cols:
        # fit on training data column
        scale = StandardScaler().fit(X_stand[[i]])
        # transform the training data column
        X_stand[i] = scale.transform(X_stand[[i]])
        mean, std = scale.mean_, scale.var_
        scaled[i] = [mean, std]

    with open('scale_station_{}.pkl'.format(station), 'wb') as f:
        pickle.dump(scaled, f, pickle.HIGHEST_PROTOCOL)

    # test-train split
    X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.3, random_state=0)

    # final model using unscaled trainng data
    knnmodel = KNeighborsClassifier(n_neighbors=3)
    knnmodel.fit(X_train, Y_train)

    with open('Model_station_{}.pkl'.format(station), 'wb') as handle:
        pickle.dump(knnmodel, handle, pickle.HIGHEST_PROTOCOL)

