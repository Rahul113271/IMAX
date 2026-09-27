"""
Regenerate movies_list.pkl and similarity.pkl from dataset.csv.
This replicates the logic from Main.ipynb.
"""
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading dataset...")
movies = pd.read_csv('dataset.csv')

# Feature selection
movies = movies[['id', 'title', 'overview', 'genre']]

# Create tags column
movies['tags'] = movies['overview'] + movies['genre']

# Remove genre and overview
new_data = movies.drop(columns=['overview', 'genre'])

print(f"Dataset shape: {new_data.shape}")

# Vectorize using CountVectorizer
print("Vectorizing tags...")
cv = CountVectorizer(max_features=10000, stop_words='english')
vector = cv.fit_transform(new_data['tags'].values.astype('U')).toarray()
print(f"Vector shape: {vector.shape}")

# Compute cosine similarity
print("Computing cosine similarity (this may take a moment)...")
similarity = cosine_similarity(vector)
print(f"Similarity matrix shape: {similarity.shape}")

# Save pickle files
print("Saving movies_list.pkl...")
pickle.dump(new_data, open('movies_list.pkl', 'wb'))

print("Saving similarity.pkl...")
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("Done! Both pickle files have been generated.")
