# 🎬 Movie Recommender System

A content-based movie recommendation system powered by **cosine similarity** and the **TMDB API**. The project features two front-end interfaces — a classic **Streamlit** app and a modern **React + Vite** web app — backed by a **FastAPI** REST API.

---

## ✨ Features

- **Content-Based Recommendations** — Uses `CountVectorizer` and cosine similarity on movie overviews & genres to suggest the 20 most similar movies.
- **TMDB Integration** — Fetches live posters, ratings, cast, directors, backdrops, and more from [The Movie Database](https://www.themoviedb.org/).
- **Industry Filters** — Browse top movies by Indian film industry (Bollywood, Tollywood, Kollywood, Sandalwood, Mollywood) and Indian Top Grossing.
- **Movie Detail Modal** — View cast, director, genres, runtime, tagline, and backdrop for any recommendation.
- **Image Carousel** — Top-rated movies displayed in an auto-scrolling carousel on the hero section.
- **Autocomplete Search** — Searchable dropdown with live filtering across the full movie catalog.
- **Interactive 3D Background** — Particle-based background with mouse-tracking and click-burst effects (React Three Fiber).

---

## 📁 Project Structure

```
├── api/
│   └── server.py              # FastAPI backend (REST endpoints)
├── frontend/                   # Streamlit custom carousel component
│   └── public/
├── web/                        # React + Vite frontend (modern UI)
│   ├── src/
│   │   ├── App.jsx             # Main application shell
│   │   └── components/         # SearchBar, Carousel, MovieCard, MovieModal, etc.
│   ├── package.json
│   └── vite.config.js
├── app.py                      # Streamlit app (classic UI)
├── Main.ipynb                  # Jupyter notebook (EDA & model training)
├── generate_pkl.py             # Regenerate pickle files from dataset.csv
├── build_dataset.py            # Build dataset from TMDB Discover API
├── integrate_new_data.py       # Merge new 2021-2025 movies into dataset
├── analyze_data.py             # Quick dataset stats & overlap check
├── dataset.csv                 # Original movie dataset
├── dataset_merged.csv          # Merged dataset (original + 2021-2025)
├── tmdb_movies_2021_2025.csv   # Supplementary TMDB data (2021-2025)
├── movies_list.pkl             # Serialized movie DataFrame
└── similarity.pkl              # Precomputed cosine-similarity matrix
```

---

## 🛠️ Prerequisites

- **Python 3.8+**
- **Node.js 18+** and **npm** (for the React web app)
- **pip** (Python package manager)

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Rahul113271/IMAX.git
cd IMAX
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install streamlit pandas scikit-learn requests fastapi uvicorn nltk urllib3
```

### 4. Install Web Frontend Dependencies

```bash
cd web
npm install
cd ..
```

### 5. Generate Similarity Matrix

```bash
python generate_pkl.py
```
> Generates `similarity.pkl` and `movies_list.pkl` from `dataset.csv` for similarity calculation.


---

## ▶️ Running the Application

### Option A — Modern Web App (React + FastAPI)

This is the recommended way to run the application. You need **two terminals**:

**Terminal 1 — Start the FastAPI backend:**

```bash
cd api
python server.py
```

> The API server starts at `http://localhost:8000`.

**Terminal 2 — Start the Vite dev server:**

```bash
cd web
npm run dev
```

> The web app opens at `http://localhost:5173` (with API calls proxied to the backend).

---

### Option B — Streamlit App (Classic UI)

```bash
python -m streamlit run app.py
```

> Opens in your browser at `http://localhost:8501`.

---

## 🔄 Regenerating the Dataset & Model

If you need to rebuild the pickle files from scratch:

### From the Existing CSV

```bash
python generate_pkl.py
```

This reads `dataset.csv`, vectorizes movie tags, computes the similarity matrix, and saves `movies_list.pkl` and `similarity.pkl`.

### From TMDB API (Fresh Build)

```bash
python build_dataset.py
```

Fetches the top 4,000 most-voted movies directly from TMDB's Discover API and generates both pickle files.

### Integrating New Data (2021-2025)

```bash
python integrate_new_data.py
```

Merges `tmdb_movies_2021_2025.csv` into the existing dataset, deduplicates, and regenerates the pickle files.

> **Note:** After regenerating the model, restart the API server to load the updated data.

---

## 🧠 How It Works

1. **Data Preparation** — Movie overviews and genres are combined into a single `tags` column.
2. **Vectorization** — `CountVectorizer` (bag-of-words, up to 10,000 features) converts tags into numerical vectors.
3. **Similarity Computation** — Cosine similarity is computed between all movie vectors, producing an N×N similarity matrix.
4. **Recommendation** — When a user selects a movie, the system retrieves the 20 most similar movies by sorting the corresponding row of the similarity matrix.
5. **Poster & Metadata** — The TMDB API supplies posters, ratings, cast, and additional details in real time.

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/movies` | GET | List all movie titles (optional `?industry=` filter) |
| `/api/recommend?movie=<title>` | GET | Get 20 recommendations for a movie |
| `/api/industry?industry=<name>` | GET | Top 20 movies for an industry |
| `/api/movie-detail?id=<tmdb_id>` | GET | Detailed info (cast, director, backdrop) |
| `/api/carousel` | GET | Top-rated movies for the homepage carousel |

---

## 📸 Screenshots

![WhatsApp Image 2024-12-25 at 10 41 43_377a9e83](https://github.com/user-attachments/assets/f7799022-d2e9-47cf-a3cf-3bde5fe8f7eb)

![WhatsApp Image 2024-12-25 at 10 42 30_c0eccdac](https://github.com/user-attachments/assets/568a7762-aabd-49f0-8fb0-62c0f6d25ad1)

![WhatsApp Image 2024-12-25 at 10 43 03_6a0ccf47](https://github.com/user-attachments/assets/d4d752ee-3dc0-469a-a022-8cbe3dec18ef)

![WhatsApp Image 2024-12-25 at 10 43 56_d093672d](https://github.com/user-attachments/assets/39f632d0-2e32-4b2e-afc5-a3369c46aac9)

![WhatsApp Image 2024-12-25 at 10 44 28_33ba0fa5](https://github.com/user-attachments/assets/419c9476-21c0-40af-a34a-0dc259a8973e)

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| ML / NLP | scikit-learn, pandas, NLTK |
| Backend API | FastAPI, Uvicorn |
| Classic Frontend | Streamlit |
| Modern Frontend | React 19, Vite 8, React Three Fiber |
| Movie Data | TMDB API v3 |
| Serialization | Python pickle |

---

## 📄 License

This project is for educational purposes.
