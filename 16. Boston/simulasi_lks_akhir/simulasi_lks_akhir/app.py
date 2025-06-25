import streamlit as st
import pandas as pd
import numpy as np
import joblib

class KMeans:
    def __init__(self, n_clusters, max_iters=300, random_state=42):
        self.n_clusters = n_clusters
        self.max_iters = max_iters
        self.random_state = random_state
        self.centroids = None
        self.inertia_ = None

    def inisialisasi(self, data):
        np.random.seed(self.random_state)
        random_index = np.random.permutation(data.shape[0])
        self.centroids = data[random_index[:self.n_clusters]]

    def cluster(self, data):
        distances = np.linalg.norm(data[:, np.newaxis] - self.centroids, axis=2)
        return np.argmin(distances, axis=1)

    def update(self, data, labels):
        self.centroids = np.array([data[labels == i].mean(axis=0) for i in range(self.n_clusters)])

    def fit(self, data):
        self.inisialisasi(data)
        for _ in range(self.max_iters):
            labels = self.cluster(data)
            new_centroids = np.array([data[labels == i].mean(axis=0) for i in range(self.n_clusters)])
            if np.all(self.centroids == new_centroids):
                break
            self.centroids = new_centroids
        self.inertia_ = np.sum([np.sum((data[labels == i] - self.centroids[i]) ** 2) for i in range(self.n_clusters)])
        return labels

    def silhouette_score(self, data, labels):
        unique_labels = np.unique(labels)
        if len(unique_labels) == 1:
            return 0

        silhouette_values = []
        for i in range(len(data)):
            same_cluster = data[labels == labels[i]]
            other_clusters = data[labels != labels[i]]

            a = np.mean(np.linalg.norm(same_cluster - data[i], axis=1))
            b = np.min([np.mean(np.linalg.norm(other_clusters[labels[labels != labels[i]] == label] - data[i], axis=1)) for label in unique_labels if label != labels[i]])

            silhouette_values.append((b - a) / max(a, b))
        return np.mean(silhouette_values)

class PCA:
    def __init__(self, n_components):
        self.n_components = n_components  # jumlah komponen utama
        self.mean = None  # nilai mean
        self.components = None  # vektor - vektor komponen utama
        self.explained_variance = None  # varians yang dijelaskan tiap komponen

    def normalisasi(self, data):
        if data.ndim == 1:
            data = data.reshape(1, -1)
        min_val = data.min(axis=0)  # nilai minimum tiap fitur
        max_val = data.max(axis=0)  # nilai maksimum tiap fitur
        range_val = max_val - min_val  # rentang nilai
        norm = (data - min_val) / range_val  # data yang dinormalisasi
        return norm

    def covariance_matrix(self, data):
        if data.shape[0] < 2:
            raise ValueError("Data harus memiliki setidaknya dua baris untuk menghitung matriks kovarians.")
        cov_matrix = np.cov(data, rowvar=False)
        return cov_matrix

    def eigen(self, cov_matrix):
        if not np.isfinite(cov_matrix).all():
            raise ValueError("Matriks kovarians mengandung nilai inf atau NaN.")
        eigval, eigvec = np.linalg.eig(cov_matrix)
        # eigval = nilai eigen dari matriks kovarian
        # eigvec = vektor eigen dari matriks kovarian
        sorted_indices = np.argsort(eigval)[::-1]  # nilai eigen yang diurutkan secara menurun
        sorted_eigval = eigval[sorted_indices]  # nilai eigen yang diurutkan
        sorted_eigvec = eigvec[:, sorted_indices]  # vektor eigen yang diurutkan
        return sorted_eigval, sorted_eigvec

    def fit(self, data):
        norm_data = self.normalisasi(data)
        cov_matrix = self.covariance_matrix(norm_data)
        eigval, eigvec = self.eigen(cov_matrix)
        self.components = eigvec[:, :self.n_components]
        self.explained_variance = eigval[:self.n_components] / np.sum(eigval)

    def transform(self, data):
        norm_data = self.normalisasi(data)
        return np.dot(norm_data, self.components)

    def fit_transform(self, data):
        self.fit(data)
        return self.transform(data)

kmeans = joblib.load("kmeans.pkl")
pca = joblib.load("pca.pkl")
df = pd.read_csv('ready.csv')

st.write('Pengelompokan Perumahan Boston dengan K-Means Clustering')

crim = st.number_input('Masukkan tingkat Kriminalitas perumahan anda', format='%.5f')
zn = st.number_input('Masukkan tingkat zona luas di perumahan anda', format='%.5f')
indus = st.number_input('Masukkan tingkat luas area industrial perumahan anda', format='%.5f')
chas = st.selectbox('Apakah perumahan anda didekat sungai Chastain?', options=['Iya', 'Tidak'])
nox = st.number_input('Masukkan tingkat Polusi udara di perumahan anda', format='%.5f')
rm = st.number_input('Masukkan rata-rata jumlah ruangan di satu rumah di perumahan anda', format='%.5f')
age = st.number_input('Masukkan rata-rata umur rumah di perumahan anda', format='%.5f')
dis = st.number_input('Masukkan jarak perumahan anda ke pusat pekerjaan boston', format='%.5f')
tax = st.number_input('Masukkan Tarif pajak properti per $10,000', format='%.5f')
ptratio = st.number_input('Masukkan rasio murid-guru di perumahan anda', format='%.5f')
b = st.number_input('Masukkan proporsi orang berkulit HYTAM di perumahan anda', format='%.5f')
lstat = st.number_input('Masukkan persentase populasi yang berkebutuhan di perumahan anda', format='%.5f')

if st.button('Enter'):
    chas = 1 if chas == 'Iya' else 0
    idx = int(len(df.index))
    df.loc[idx]  = [crim, zn, indus, chas, nox, rm, age, dis, tax, ptratio, b, lstat]
    
    
    # # Tambahkan satu baris data dummy jika DataFrame hanya memiliki satu baris
    # if df.shape[0] < 2:
    #     dummy_data = pd.DataFrame(np.random.rand(2, df.shape[1]), columns=df.columns)
    #     df = pd.concat([df, dummy_data], ignore_index=True)

    pca = PCA(n_components=7)
    df_pca = pca.fit_transform(df)
    kmeans = KMeans(n_clusters=3)
    labels = kmeans.fit(df_pca)
    df['Cluster'] = labels
    st.write(f'Perumahan anda termasuk kelompok: {df['Cluster'].loc[idx]}')