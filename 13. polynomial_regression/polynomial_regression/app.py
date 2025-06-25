import streamlit as st
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations_with_replacement

df = pd.read_csv('ice_cream selling data.csv')

if 'df' in globals():
    x = df['Temperature (°C)']
    y = df['Ice Cream Sales (units)']
else:
    st.write('dataset not found')

#split data
np.random.seed(0)
train_size = int(len(x) * 0.8)
idx = np.random.permutation(len(x))

x_train, x_test = x.iloc[idx[:train_size]], x.iloc[idx[train_size:]]
y_train, y_test = y.iloc[idx[:train_size]], y.iloc[idx[train_size:]]

#normalisasi
min_value = x_train.min(axis=0)
max_value = x_train.max(axis=0)
range_value = max_value - min_value
x_train = (x_train - min_value) / range_value
x_test = (x_test - min_value) / range_value

class PolynomialFeatures:
    def __init__(self, degree=2):
        self.degree = degree

    def fit_transform(self, X):
        n_samples, n_features = X.shape
        features = [np.ones(n_samples)]
        for d in range(1, self.degree + 1):
            for item in combinations_with_replacement(range(n_features), d):
                features.append(np.prod(X[:, item], axis=1))
        return np.vstack(features).T

class LinearRegression:
    def __init__(self):
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X, y):
        X_b = np.c_[np.ones((X.shape[0], 1)), X]  # add bias term
        theta_best = np.linalg.pinv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)
        self.intercept_ = theta_best[0]
        self.coef_ = theta_best[1:]

    def predict(self, X):
        return X.dot(self.coef_) + self.intercept_
    
class PolynomialRegression:
    def __init__(self, degree=2):
        self.degree = degree
        self.poly_features = PolynomialFeatures(degree=degree)
        self.linear_regression = LinearRegression()

    def fit(self, X, y):
        if X.ndim == 1:
            X = X.values.reshape(-1, 1)
        X_poly = self.poly_features.fit_transform(X)
        self.linear_regression.fit(X_poly, y)

    def predict(self, X):
        if X.ndim == 1:
            X = X.values.reshape(-1, 1)
        X_poly = self.poly_features.fit_transform(X)
        return self.linear_regression.predict(X_poly)

#pemodelan
model = PolynomialRegression(degree=4)
model.fit(x_train,y_train)

#input data
input = st.number_input('Masukkan suhu', value=5)
ready_input = np.array(float(input)).reshape(-1, 1)

#normalisasi input
def minmax(input):
    return (input - min_value) / range_value

ready_input = minmax(ready_input)

if st.button('Enter'):
    predict = int(model.predict(ready_input))
    if predict >= 0:
        st.write(f'Penjualan Es Krim: {predict} Unit')
    else:
        st.write(f'Tidak ada yang membeli es krim karna suhu dingin.')