import pandas as pd
import numpy as np
from sklearn import preprocessing, model_selection, svm
from sklearn import linear_model
from sklearn.linear_model import LinearRegression

def housePred(zip_code, sq_ft):
    df = pd.read_csv('Sacramentorealestatetransactions.csv')
    df.drop(['street', 'city', 'state', 'sale_date', 'beds', 'baths', 'latitude', 'longitude', 'type'], axis = 1, inplace = True)

    X = np.array(df.drop(['price'], 1))
    y = np.array(df['price'])

    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size = 0.2, random_state = 4)

    reg = linear_model.LinearRegression()
    reg.fit(X_train, y_train)
    accuracy = reg.score(X_test, y_test)
    dataset = np.array([zip_code, sq_ft])
    dataset = dataset.reshape(-1, 2)
    prediction = reg.predict(dataset)
    pred = prediction - 100000
    print(pred)

housePred(95621, 1000)
