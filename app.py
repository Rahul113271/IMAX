import streamlit as st
import pickle
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def fetch_poster(movie_id):
     # Configure retry strategy
     retry_strategy = Retry(
         total=3,
         backoff_factor=1,
         status_forcelist=[500, 502, 503, 504]
     )
     adapter = HTTPAdapter(max_retries=retry_strategy)
     session = requests.Session()
     session.mount("https://", adapter)
    
     try:
         url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
         response = session.get(url, timeout=5)
         response.raise_for_status()
         data = response.json()
         return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
     except requests.exceptions.RequestException as e:
         print(f"Error fetching poster for movie {movie_id}: {str(e)}")
         return "https://via.placeholder.com/500x750?text=No+Poster"

movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))
movies_list=movies['title'].values

st.header("Movie Recommender System")

import streamlit.components.v1 as components

imageCarouselComponent = components.declare_component("image-carousel-component", path="frontend/public")


imageUrls = [
    fetch_poster(1632),
    fetch_poster(299536),
    fetch_poster(17455),
    fetch_poster(2830),
    fetch_poster(429422),
    fetch_poster(9722),
    fetch_poster(13972),
    fetch_poster(240),
    fetch_poster(155),
    fetch_poster(598),
    fetch_poster(914),
    fetch_poster(255709),
    fetch_poster(572154)
   
    ]


imageCarouselComponent(imageUrls=imageUrls, height=200)
selectvalue=st.selectbox("Select movie from dropdown", movies_list)

def recommend(movie):
    index=movies[movies['title']==movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector:vector[1])
    recommend_movie=[]
    recommend_poster=[]
    for i in distance[1:21]:
        movies_id=movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(fetch_poster(movies_id))
    return recommend_movie, recommend_poster



if st.button("Show Recommend"):
    movie_name, movie_poster = recommend(selectvalue)
    col1,col2,col3,col4,col5=st.columns(5)
    col6,col7,col8,col9,col10=st.columns(5)
    col11,col12,col13,col14,col15=st.columns(5)
    col16,col17,col18,col19,col20=st.columns(5)

    with col1:
        st.text(movie_name[0])
        st.image(movie_poster[0])
    with col2:
        st.text(movie_name[1])
        st.image(movie_poster[1])
    with col3:
        st.text(movie_name[2])
        st.image(movie_poster[2])
    with col4:
        st.text(movie_name[3])
        st.image(movie_poster[3])
    with col5:
        st.text(movie_name[4])
        st.image(movie_poster[4])
    with col6:
        st.text(movie_name[5])
        st.image(movie_poster[5])
    with col7:
        st.text(movie_name[6])
        st.image(movie_poster[6])
    with col8:
        st.text(movie_name[7])
        st.image(movie_poster[7])
    with col9:
        st.text(movie_name[8])
        st.image(movie_poster[8])
    with col10:
        st.text(movie_name[9])
        st.image(movie_poster[9])
    with col11:
        st.text(movie_name[10])
        st.image(movie_poster[10])
    with col12:
        st.text(movie_name[11])
        st.image(movie_poster[11])
    with col13:
        st.text(movie_name[12])
        st.image(movie_poster[12])
    with col14:
        st.text(movie_name[13])
        st.image(movie_poster[13])
    with col15:
        st.text(movie_name[14])
        st.image(movie_poster[14])
    with col16:
        st.text(movie_name[15])
        st.image(movie_poster[15])
    with col17:
        st.text(movie_name[16])
        st.image(movie_poster[16])
    with col18:
        st.text(movie_name[17])
        st.image(movie_poster[17])
    with col19:
        st.text(movie_name[18])
        st.image(movie_poster[18])
    with col20:
        st.text(movie_name[19])
        st.image(movie_poster[19])


