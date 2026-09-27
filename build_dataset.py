import os
import pickle
import requests
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem.porter import PorterStemmer
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Download punkt just in case
nltk.download('punkt', quiet=True)

TMDB_API_KEY = "c7ec19ffdd3279641fb606d19ceb9bb1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_session():
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    return session

def build_dataset():
    session = get_session()
    
    print("Fetching genres mapping...")
    genres_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    genres_response = session.get(genres_url).json()
    genre_map = {g['id']: g['name'] for g in genres_response.get('genres', [])}
    
    movies_data = []
    
    # We will fetch the top 200 pages (4000 movies) sorted by vote_count
    # This ensures we get the most well-known movies of all time up to the present day
    pages_to_fetch = 200
    
    print(f"Fetching top {pages_to_fetch * 20} most voted movies from TMDB...")
    
    for page in range(1, pages_to_fetch + 1):
        if page % 10 == 0:
            print(f"Fetching page {page}/{pages_to_fetch}...")
            
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=en-US&sort_by=vote_count.desc&page={page}"
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"Error on page {page}: {response.text}")
            continue
            
        data = response.json()
        
        for movie in data.get('results', []):
            movie_id = movie.get('id')
            title = movie.get('title')
            overview = movie.get('overview', '')
            genre_ids = movie.get('genre_ids', [])
            
            # Map genre IDs to names
            genres = [genre_map.get(gid, "") for gid in genre_ids]
            
            # Combine overview and genres into tags
            # We lowercase everything and remove commas
            genres_str = " ".join([g.replace(" ", "") for g in genres]).lower()
            overview_str = overview.lower()
            
            tags = f"{overview_str} {genres_str}"
            
            movies_data.append({
                'id': movie_id,
                'title': title,
                'tags': tags
            })
            
    print(f"Successfully fetched {len(movies_data)} movies!")
    
    df = pd.DataFrame(movies_data)
    
    # Drop any rows without tags
    df = df.dropna(subset=['tags'])
    
    print("Applying NLP Stemming...")
    ps = PorterStemmer()
    
    def stem(text):
        y = []
        for i in text.split():
            y.append(ps.stem(i))
        return " ".join(y)
        
    df['tags'] = df['tags'].apply(stem)
    
    print("Computing Cosine Similarity (this takes a moment)...")
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(df['tags']).toarray()
    
    similarity = cosine_similarity(vectors)
    
    print("Saving movies_list.pkl and similarity.pkl...")
    pickle.dump(df, open(os.path.join(BASE_DIR, 'movies_list.pkl'), 'wb'))
    pickle.dump(similarity, open(os.path.join(BASE_DIR, 'similarity.pkl'), 'wb'))
    
    print("Dataset generation complete!")

if __name__ == "__main__":
    build_dataset()
