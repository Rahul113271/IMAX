"""
FastAPI backend for the Movie Recommender System.
Exposes recommendation logic as REST API endpoints.
"""
import pickle
import os
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor
import uvicorn

# --- Load Data ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
movies = pickle.load(open(os.path.join(BASE_DIR, "movies_list.pkl"), "rb"))
similarity = pickle.load(open(os.path.join(BASE_DIR, "similarity.pkl"), "rb"))

# --- App Setup ---
app = FastAPI(title="Movie Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- TMDB Helpers ---
TMDB_API_KEY = "c7ec19ffdd3279641fb606d19ceb9bb1"


def _tmdb_session():
    """Create a requests session with retry strategy."""
    retry_strategy = Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    return session


def fetch_poster(movie_id):
    """Fetch basic movie info from TMDB (poster, overview, rating, genres, tagline, runtime)."""
    movie_id = int(movie_id)  # ensure native int (not numpy.int64)
    session = _tmdb_session()
    
    import time
    for attempt in range(3):
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return {
                    "movie_id": movie_id,
                    "title": data.get("title", ""),
                    "poster": f"https://image.tmdb.org/t/p/w500{poster_path}",
                    "overview": data.get("overview", ""),
                    "vote_average": data.get("vote_average", 0),
                    "release_date": data.get("release_date", ""),
                    "genres": [g["name"] for g in data.get("genres", [])],
                    "tagline": data.get("tagline", ""),
                    "runtime": data.get("runtime", 0),
                }
            break
        except Exception as e:
            print(f"Error fetching poster for movie {movie_id} (Attempt {attempt+1}): {e}")
            time.sleep(1)

    return {
        "movie_id": movie_id,
        "title": "Unknown Title",
        "poster": "https://via.placeholder.com/500x750?text=No+Poster",
        "overview": "",
        "vote_average": 0,
        "release_date": "",
        "genres": [],
        "tagline": "",
        "runtime": 0,
    }


def fetch_movie_detail(movie_id):
    """Fetch detailed movie info from TMDB including cast and crew."""
    movie_id = int(movie_id)  # ensure native int
    session = _tmdb_session()
    result = {
        "movie_id": movie_id,
        "cast": [],
        "director": "",
        "backdrop": "",
    }

    try:
        # Movie details (for backdrop)
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        backdrop_path = data.get("backdrop_path")
        if backdrop_path:
            result["backdrop"] = f"https://image.tmdb.org/t/p/w1280{backdrop_path}"

        # Credits (cast & crew)
        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=en-US"
        credits_resp = session.get(credits_url, timeout=5)
        credits_resp.raise_for_status()
        credits = credits_resp.json()

        # Top 6 cast members
        for member in credits.get("cast", [])[:6]:
            profile = member.get("profile_path")
            result["cast"].append({
                "name": member.get("name", ""),
                "character": member.get("character", ""),
                "photo": f"https://image.tmdb.org/t/p/w185{profile}" if profile else "",
            })

        # Director
        for crew in credits.get("crew", []):
            if crew.get("job") == "Director":
                result["director"] = crew.get("name", "")
                break

    except Exception as e:
        print(f"Error fetching details for movie {movie_id}: {e}")

    return result


# Load full dataset for language filtering
import pandas as pd
full_dataset = pd.read_csv(os.path.join(BASE_DIR, "dataset_merged.csv"))

# Map industry names to language codes
INDUSTRY_LANG_MAP = {
    "kollywood": ["ta"],
    "tollywood": ["te"],
    "bollywood": ["hi"],
    "sandalwood": ["kn"],
    "mollywood": ["ml"],
}

# --- API Endpoints ---

@app.get("/api/movies")
def get_movies(industry: str = Query(None, description="Filter by industry (kollywood, tollywood, etc.)")):
    """Return list of movie titles, optionally filtered by industry/language."""
    if industry and industry.lower() in INDUSTRY_LANG_MAP:
        langs = INDUSTRY_LANG_MAP[industry.lower()]
        filtered = full_dataset[full_dataset["original_language"].isin(langs)]
        return {"movies": filtered["title"].tolist(), "industry": industry}
    return {"movies": movies["title"].tolist()}


@app.get("/api/industry")
def get_industry_movies(industry: str = Query(..., description="Industry name")):
    """Return top 20 movies (with full details) for a specific industry."""
    if industry == "Indian Top Grossing":
        # Hardcoded list of the Top 20 highest-grossing Indian movies of all time for 100% accuracy
        INDIAN_TOP_GROSSING = {
            857598: "Pushpa 2: The Rule",
            1291608: "Dhurandhar",
            801688: "Kalki 2898 AD",
            360814: "Dangal",
            350312: "Baahubali 2: The Conclusion",
            579974: "RRR",
            587412: "K.G.F: Chapter 2",
            872906: "Jawan",
            864692: "Pathaan",
            784689: "Animal",
            348892: "Bajrangi Bhaijaan",
            441889: "Secret Superstar",
            297222: "PK",
            770906: "Salaar: Part 1 - Ceasefire",
            377315: "Sultan",
            311804: "2.0",
            256040: "Baahubali: The Beginning",
            520216: "Sanju",
            432527: "Padmaavat",
            460605: "Tiger Zinda Hai"
        }
        movie_ids = list(INDIAN_TOP_GROSSING.keys())
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            all_results = list(executor.map(fetch_poster, movie_ids))
            
        movies_data = []
        for info in all_results:
            fetched_title = info.get("title")
            movies_data.append({
                **info,
                "title": fetched_title if fetched_title and fetched_title != "Unknown Title" else INDIAN_TOP_GROSSING.get(info.get("movie_id"), "Unknown Title"),
                "similarity": 100.0, 
                "shared_genres": info.get("genres", []),
            })
        return {"movies": movies_data, "industry": industry}

    if industry.lower() not in INDUSTRY_LANG_MAP:
        return {"error": "Unknown industry", "movies": []}
    
    langs = INDUSTRY_LANG_MAP[industry.lower()]
    # Filter dataset for this language, sort by vote count to get the best/most popular ones
    filtered = full_dataset[full_dataset["original_language"].isin(langs)].sort_values(by="vote_count", ascending=False)
    
    # Get top 20
    top20 = filtered.head(20)
    movie_ids = top20["id"].tolist()
    
    # Fetch all posters in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        all_results = list(executor.map(fetch_poster, movie_ids))
        
    movies_data = []
    for (_, row), info in zip(top20.iterrows(), all_results):
        vote_avg = info.get("vote_average")
        if not vote_avg:
            vote_avg = row.get("vote_average", 0)
            
        movies_data.append({
            **info,
            "title": str(row["title"]),
            "vote_average": vote_avg,
            "similarity": 100.0, # Dummy for UI compatibility
            "shared_genres": [g for g in str(row["genre"]).split(",") if g],
        })
        
    return {"movies": movies_data, "industry": industry}


@app.get("/api/recommend")
def get_recommendations(movie: str = Query(..., description="Movie title to get recommendations for")):
    """Return top 20 recommended movies with posters, metadata, and the source movie's info."""
    try:
        index = movies[movies["title"] == movie].index[0]
    except IndexError:
        return {"error": f"Movie '{movie}' not found", "recommendations": [], "source": None}

    # Get the top 20 similar movies (skip index 0 which is the movie itself)
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    top20 = distances[1:21]

    # Collect all movie IDs we need to fetch (source + 20 recommendations)
    source_movie_data = movies.iloc[index]
    source_id = int(source_movie_data.id)

    rec_movie_data = [(movies.iloc[i[0]], i[1]) for i in top20]
    rec_ids = [int(md.id) for md, _ in rec_movie_data]

    # Fetch ALL posters in parallel (source + 20 recs = 21 calls at once)
    all_ids = [source_id] + rec_ids
    with ThreadPoolExecutor(max_workers=5) as executor:
        all_results = list(executor.map(fetch_poster, all_ids))

    source_info = all_results[0]
    rec_infos = all_results[1:]

    source = {
        "title": str(source_movie_data.title),
        **source_info,
    }

    recommendations = []
    for (movie_data, sim_score), info in zip(rec_movie_data, rec_infos):
        shared_genres = [g for g in info.get("genres", []) if g in source_info.get("genres", [])]
        recommendations.append({
            **info,
            "title": str(movie_data.title),
            "similarity": round(float(sim_score) * 100, 1),
            "shared_genres": shared_genres,
        })

    return {"recommendations": recommendations, "source": source}


@app.get("/api/movie-detail")
def get_movie_detail(id: int = Query(..., description="TMDB movie ID")):
    """Return detailed movie info including cast, director, and backdrop."""
    return fetch_movie_detail(id)


@app.get("/api/carousel")
def get_carousel():
    """Return top IMDb-rated movies for the carousel via TMDB's top_rated endpoint."""
    session = _tmdb_session()
    items = []
    try:
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={TMDB_API_KEY}&language=en-US&page=1"
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        for movie in data.get("results", [])[:15]:
            poster_path = movie.get("poster_path")
            items.append({
                "poster": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Poster",
                "title": movie.get("title", ""),
                "vote_average": movie.get("vote_average", 0),
            })
    except Exception as e:
        print(f"Error fetching top rated movies: {e}")
    
    # Fallback: if API fails, return hardcoded top-rated movies instantly
    if not items:
        fallback_movies = [
            {"title": "The Shawshank Redemption", "poster": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg", "vote_average": 8.7},
            {"title": "The Godfather", "poster": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", "vote_average": 8.7},
            {"title": "The Dark Knight", "poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "vote_average": 8.5},
            {"title": "The Godfather Part II", "poster": "https://image.tmdb.org/t/p/w500/hek3koDUyRQk7FIhPXsa6mT2Zc3.jpg", "vote_average": 8.6},
            {"title": "12 Angry Men", "poster": "https://image.tmdb.org/t/p/w500/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg", "vote_average": 8.5},
            {"title": "Schindler's List", "poster": "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg", "vote_average": 8.6},
            {"title": "The Lord of the Rings: The Return of the King", "poster": "https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg", "vote_average": 8.5},
            {"title": "Pulp Fiction", "poster": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", "vote_average": 8.5},
            {"title": "The Lord of the Rings: The Fellowship of the Ring", "poster": "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbCicCG31CGa0.jpg", "vote_average": 8.4},
            {"title": "Forrest Gump", "poster": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "vote_average": 8.5}
        ]
        items = fallback_movies

    return {"posters": [item["poster"] for item in items], "items": items}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
