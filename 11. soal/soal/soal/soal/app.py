import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

pca_df = pd.read_csv('pca_df.csv')

st.title('Sistem Rekomendasi film!')
if 'pca_df' in globals():
    film_titles = pca_df['title'].tolist()
else:
    print('film not found')
    
selected = st.selectbox('Pilih film yang anda suka:', film_titles)

def get_recom(input):
    if input in pca_df['title'].values:
        selected_mv_cluster = pca_df.loc[pca_df['title'] == input, 'Cluster'].values[0]
        recom_df = pca_df[pca_df['Cluster'] == selected_mv_cluster].sort_index()
        recom_movies = recom_df.head(11)['title'].tolist()
        recom_movies.remove(input)
        if input in recom_movies:
            recom_movies.remove(input)
        return recom_movies, selected_mv_cluster, recom_df
    else:
        return [], None
    
if st.button('Enter'):
    recom, selected_mv_cluster, recom_df = get_recom(selected)
    if recom:
        st.success('Film yang direkomendasikan untuk anda:')
        st.write(', '.join(recom))
        
    else:
        st.warning('Film tidak ditemukan')
        
    # Visualization