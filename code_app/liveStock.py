import pandas as pd
import math, datetime
import numpy as np
from sklearn import preprocessing, model_selection, svm
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib import style
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
import random
import requests
import json, csv, os
import time
from django.conf import settings

#symbols = ['Amazon.com Inc.']
def getDF(company_name):
    style.use('ggplot')

    df = pd.read_csv(os.path.join(settings.BASE_DIR, 'code_app/sp500tickersandnames.csv'))
    # company_name = input("Enter: ")
    i = 0

    for name in df['Names']:
        if name == company_name:
            n = df['Tickers'][i]
            break
        i += 1

    #for symbol in symbols:
    filename=os.path.join(settings.BASE_DIR,'code_app/{}csv.csv'.format(n))
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    else:
        API_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&datatype=csv&apikey=CAEP52JD28UXF203".format(n)
        response = requests.get(API_URL)
        dfx = response.text
        f = open(filename, 'w')
        f.write(dfx)
        f.close()
        df = pd.read_csv(filename)


    df = df[['timestamp', 'open', 'high', 'low', 'close', 'adjusted_close', 'volume']]
    # df['date'] = df['timestamp']
    df.set_index('timestamp', inplace=True)
    df = df.iloc[::-1]

    df['HL_PCT'] = (df['high'] - df['adjusted_close']) / df['adjusted_close'] * 100
    df['PCT_change'] = (df['adjusted_close'] - df['open']) / df['open'] * 100

    df = df[['adjusted_close', 'HL_PCT', 'PCT_change', 'volume']]

    forecast_col = 'adjusted_close'
    df.fillna(-9999, inplace = True)

    forecast_out = int(math.ceil(0.1 * len(df)))
    df['label'] = df[forecast_col].shift(-forecast_out)

    X = np.array(df.drop(['label', 'adjusted_close'], 1 ))
    X = preprocessing.scale(X)
    X_lately = X[-forecast_out:]
    X = X[:-forecast_out]

    df.dropna(inplace=True)
    y = np.array(df['label'])

    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size = 0.2)
    clf = GradientBoostingRegressor(n_estimators=200)
    clf.fit(X_train,y_train)
    accuracy = clf.score(X_test, y_test)

    forecast_set = clf.predict(X_lately)

    df['Forecast'] = np.nan

    #last_date = df.iloc[-1].name
    last_date = "2019-03-01"
    last_unix = time.mktime(datetime.datetime.strptime(last_date, "%Y-%m-%d").timetuple())
    #last_unix = last_date.timestamp()
    one_day = 86400
    next_unix = last_unix + one_day


    for i in forecast_set:
        next_date = datetime.datetime.fromtimestamp(next_unix)
        next_unix += one_day
        df.loc[next_date] = [np.nan for _ in range(len(df.columns)-1)] + [i]

    return df
    # return df['adjusted_close'], df['Forecast']



