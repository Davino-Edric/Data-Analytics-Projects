import streamlit as st
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA 

st.write('Boston Housing KNN Classifier')

chas = st.selectbox('Apakah di dekat sungai Charles?', ['Ya', 'Tidak'])
crim = st.number_input('Masukkan tingkat crim')
zn = st.number_input('Masukkan tingkat zn')
indus = st.number_input('Masukkan tingkat indus')
nox = st.number_input('Masukkan tingkat nox')
rm = st.number_input('Masukkan tingkat rm')
dis = st.number_input('Masukkan tingkat dis')
rad = st.number_input('Masukkan tingkat rad')
ptratio = st.number_input('Masukkan tingkat ptratio')
b = st.number_input('Masukkan tingkat b')
lstat = st.number_input('Masukkan tingkat lstat')

df = pd.Series([chas,crim,zn,indus,nox,rm,dis,rad,])
df = pd.DataFrame(df).T
