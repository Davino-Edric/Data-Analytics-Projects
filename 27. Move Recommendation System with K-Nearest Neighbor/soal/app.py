import streamlit as st
import pandas as pd

df_fixed = pd.read_csv('df_scaled')

st.title('Sistem Rekomendasi film!')

df_scaled = pd.read_csv('df_scaled.csv')
if 'df_scaled' in globals():
    film_titles = df_scaled['title'].tolist()
else:
    print('film not found')
    
selected = st.selectbox('Pilih film yang anda suka:', film_titles)

def get_recom(input):
    if input in df_scaled['title'].values:
        movie_cluster = df_scaled.loc[df_scaled['title'] == input, 'genre'].values[0]
        recom_movies = df_scaled[df_scaled['genre'] == movie_cluster]['title'].tolist()
        recom_movies.remove(input)
        return recom_movies
    else:
        return []
    
if st.button('Enter'):
    recom = get_recom(selected)
    if recom:
        st.success('Film yang direkomendasikan untuk anda:')
        st.write(', '.join(recom))
        
    else:
        st.warning('Film tidak ditemukan')