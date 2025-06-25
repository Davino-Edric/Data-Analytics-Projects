import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import joblib
import streamlit as st

model = joblib.load('boston_housing_model.pkl')
pca = joblib.laod('pca.pkl')

st.write('Boston Housing prediction model:')

crim= st.selectbox('Apakah tingkat kriminalitas di perumahan anda tinggi?', options=['Low', 'High'])
zn= st.selectbox('Apakah tingkat zona luas di perumahan anda tinggi?', options=['Low', 'High'])
dis= st.selectbox('Apakah tingkat kedekatan perumahan anda ke pusat HRD boston tinggi?', options=['Low', 'High'])
indus = st.number_input('Masukkan nilai indus')
nox = st.number_input('Masukkan nilai NOX')
rn = st.number_input('Masukkan nilai RM')
age = st.number_input('Masukkan nilai AGE')
tax = st.number_input('Masukkan nilai TAX')
ptratio = st.number_input('Masukkan nilai PTRATIO')
lstat= st.number_input('Masukkan nilai LSTAT')

if st.button('Enter'):
    st.write(crim)
    st.write(zn)
    st.write(dis)
    st.write(indus)
    st.write(nox)
    st.write(rn)
    st.write(age)
    st.write(tax)
    st.write(ptratio)
    st.write(lstat)