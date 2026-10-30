import streamlit as st 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

df = pd.read_csv('df_ready.csv')

if 'df' in globals():
    x = df['Original Price']
    y = df['Discrepancy']
else:
    st.write('Dataset not loaded')
    
input_raw = st.number_input('Masukkan Original Price', value=0)

class SimpleLinearRegression:
    def __init__(self):
        self.slope = None
        self.intercept = None

    def fit(self, x, y):
        n = len(x)
        numerator = n * np.sum(x * y) - np.sum(x) * np.sum(y)
        denominator = n * np.sum(x**2) - np.sum(x)**2
        self.slope = numerator / denominator
        self.intercept = (np.sum(y) - self.slope * np.sum(x)) / n

    def predict(self, x):
        y_pred = self.intercept + self.slope * x
        return y_pred

def minmaxfit(input):
    minim = input.min()
    maxim = input.max()
    norm = (input - minim) / (maxim - minim)
    return norm, minim,maxim

def minmax(input):
    return (input - input.min()) / (input.max() - input.min())

x_norm, maxim, minim = minmaxfit(x)
y_norm, _, __ = minmaxfit(y)

model = SimpleLinearRegression()
model.fit(x_norm,y_norm)

if st.button('Enter'):
    input = np.array(input_raw)
    ready_input = (input - minim) / (maxim - minim)
    diff_pred = model.predict(ready_input)
    new_price = input_raw - (diff_pred * 50)
    st.write(f'Harga Original Produk: ', int(input_raw))
    st.write(f'Perbedaan Harga Original dan Asli: {(diff_pred)}%')
    st.write(f'Harga Selling setelah diskon: ', int(new_price))