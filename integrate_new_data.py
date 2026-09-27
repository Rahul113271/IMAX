"""
Integrate tmdb_movies_2021_2025.csv into the existing dataset.csv,
then regenerate movies_list.pkl and similarity.pkl.
"""
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ──────────────────────────────────────────────
# 1. Load both datasets
# ──────────────────────────────────────────────
print("Loading existing dataset...")
existing = pd.read_csv('dataset.csv')
print(f"  Existing: {len(existing)} movies")

print("Loading new 2021-2025 dataset...")
new_raw = pd.read_csv('tmdb_movies_2021_2025.csv')
print(f"  New (raw): {len(new_raw)} movies")

# ──────────────────────────────────────────────
# 2. Filter new dataset for quality movies (50+ votes)
# ──────────────────────────────────────────────
new_filtered = new_raw[new_raw['vote_count'] >= 50].copy()
print(f"  New (filtered 50+ votes): {len(new_filtered)} movies")

# ──────────────────────────────────────────────
# 3. Harmonize column names & format
# ──────────────────────────────────────────────
# New CSV: tmdb_id, title, original_title, release_date, genres (pipe-separated),
#          vote_average, vote_count, popularity, original_language, overview, poster_url
# Existing: id, title, genre (comma-separated), original_language, overview,
#           popularity, release_date, vote_average, vote_count

new_harmonized = pd.DataFrame({
    'id': new_filtered['tmdb_id'],
    'title': new_filtered['title'],
    'genre': new_filtered['genres'].fillna('').str.replace('|', ',', regex=False),
    'original_language': new_filtered['original_language'],
    'overview': new_filtered['overview'],
    'popularity': new_filtered['popularity'],
    'release_date': new_filtered['release_date'],
    'vote_average': new_filtered['vote_average'],
    'vote_count': new_filtered['vote_count'],
})

# ──────────────────────────────────────────────
# 4. Merge & deduplicate (keep existing entry if overlap)
# ──────────────────────────────────────────────
# Remove overlapping IDs from the new data (existing data takes priority)
existing_ids = set(existing['id'])
new_unique = new_harmonized[~new_harmonized['id'].isin(existing_ids)]
print(f"  New unique (not in existing): {len(new_unique)} movies")

merged = pd.concat([existing, new_unique], ignore_index=True)
print(f"  Merged total: {len(merged)} movies")

# ──────────────────────────────────────────────
# 5. Save the merged dataset.csv
# ──────────────────────────────────────────────
merged.to_csv('dataset_merged.csv', index=False)
print(f"Saved dataset_merged.csv with {len(merged)} movies")

# ──────────────────────────────────────────────
# 6. Regenerate pickle files
# ──────────────────────────────────────────────
print("\nPreparing data for ML model...")
movies = merged[['id', 'title', 'overview', 'genre']].copy()

# Fill NaN values to avoid errors
movies['overview'] = movies['overview'].fillna('')
movies['genre'] = movies['genre'].fillna('')

# Create tags column (same logic as original Main.ipynb)
movies['tags'] = movies['overview'] + ' ' + movies['genre']
new_data = movies.drop(columns=['overview', 'genre'])

print(f"Dataset shape: {new_data.shape}")

# Vectorize using CountVectorizer
print("Vectorizing tags...")
cv = CountVectorizer(max_features=10000, stop_words='english')
vector = cv.fit_transform(new_data['tags'].values.astype('U')).toarray()
print(f"Vector shape: {vector.shape}")

# Compute cosine similarity
print("Computing cosine similarity (this may take a while with more movies)...")
similarity = cosine_similarity(vector)
print(f"Similarity matrix shape: {similarity.shape}")

# Save pickle files
print("Saving movies_list.pkl...")
pickle.dump(new_data, open('movies_list.pkl', 'wb'))

print("Saving similarity.pkl...")
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("\n✅ Done! Integration complete.")
print(f"   Total movies in system: {len(new_data)}")
print(f"   Similarity matrix: {similarity.shape[0]}x{similarity.shape[1]}")
print("\n   Restart the API server to use the updated model.")
