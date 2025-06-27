import pickle
import streamlit as st
import requests
import pandas as pd

# Load movie dictionary and convert to DataFrame
with open('new_asDict.pkl', 'rb') as f:
    data_dict = pickle.load(f)

movies = pd.DataFrame(data_dict)

# Load similarity matrix
from scipy.sparse import load_npz

similarity = load_npz("similarity_sparse.npz")


# Function to fetch movie poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        return "https://via.placeholder.com/300x450?text=No+Image"

    data = response.json()
    poster_path = data.get('poster_path')
    if not poster_path:
        return "https://via.placeholder.com/300x450?text=No+Image"

    return "https://image.tmdb.org/t/p/w500/" + poster_path

# Function to recommend similar movies
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# Streamlit UI
st.header('🎬 Movie Recommender System')

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    if not recommended_movie_names:
        st.warning("No recommendations found. Please check the movie title.")
    else:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i], use_column_width='always')
