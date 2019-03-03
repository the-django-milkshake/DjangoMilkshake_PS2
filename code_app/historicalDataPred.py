import pandas as pd
import quandl
import math, datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from sklearn import preprocessing, model_selection, svm, neighbors
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
import random

style.use('ggplot')
quandl.ApiConfig.api_key = "McjQvuKdficVT74V1rzw"

df = quandl.get('WIKI/GOOGL')
df = df[['Adj. Open', 'Adj. High', 'Adj. Low', 'Adj. Close', 'Adj. Volume']]
df['HL_PCT'] = (df['Adj. High'] - df['Adj. Close']) / df['Adj. Close'] * 100
df['PCT_change'] = (df['Adj. Close'] - df['Adj. Open']) / df['Adj. Open'] * 100

df = df[['Adj. Close', 'HL_PCT', 'PCT_change', 'Adj. Volume']]

forecast_col = 'Adj. Close'
df.fillna(-9999, inplace = True)

forecast_out = int(math.ceil(0.1 * len(df)))
df['label'] = df[forecast_col].shift(-forecast_out)

X = np.array(df.drop(['label', 'Adj. Close'], 1 ))
X = preprocessing.scale(X)
X_lately = X[-forecast_out:]
X = X[:-forecast_out]

df.dropna(inplace=True)
y = np.array(df['label'])

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size = 0.2)

'''
*************SINCE ALREADY PICKLED****************

clf = LinearRegression(n_jobs = -1)
clf.fit(X_train, y_train)
with open('linearregression.pickle','wb') as f:
    pickle.dump(clf, f)
'''
clf = GradientBoostingRegressor(n_estimators=200)
clf.fit(X_train,y_train)
#pickle_in = open('linearregression.pickle','rb')
#clf = pickle.load(pickle_in)

'''
clf = LinearRegression(n_jobs = -1)
clf.fit(X_train, y_train)
with open('linearregressionamazon.pickle','wb') as f:
    pickle.dump(clf, f)

pickle_in = open('linearregressionamazon.pickle','rb')
clf = pickle.load(pickle_in)
'''
accuracy = clf.score(X_test, y_test)

forecast_set = clf.predict(X_lately)
m = forecast_set.mean()
i = 0
for forecast in forecast_set:
    if forecast < m-200:
        forecast_set[i] = m
    elif forecast > m+200:
        forecast_set[i] = m
    i += 1
i = 0
while i < len(forecast_set)-1:
    if forecast_set[i]-forecast_set[i+1] > 20:
        forecast_set[i+1] = forecast_set[i] - random.randint(0,10)
    elif forecast_set[i]-forecast_set[i+1] < -20:
        forecast_set[i+1] = forecast_set[i] + random.randint(0,10)
    i += 1
print(forecast_set, accuracy, forecast_out)

df['Forecast'] = np.nan

last_date = df.iloc[-1].name
print(last_date)
last_unix = last_date.timestamp()
one_day = 86400
next_unix = last_unix + one_day

for i in forecast_set:
    next_date = datetime.datetime.fromtimestamp(next_unix)
    next_unix += one_day
    df.loc[next_date] = [np.nan for _ in range(len(df.columns)-1)] + [i]

#print(df['Forecast'])
print(df.head())

df['Adj. Close'].plot()
df['Forecast'].plot()
plt.legend(loc = 4)
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

'''
#******************USING SVMS (NOT AS GOOD AN ACCURACY IN THIS CASE)*******************
clfsvm = svm.SVR()
clfsvm.fit(X_train, y_train)
accuracy2 = clfsvm.score(X_test, y_test)
print(accuracy2)
'''
