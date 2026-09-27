import pandas as pd

df = pd.read_csv('tmdb_movies_2021_2025.csv')
print(f'Total rows: {len(df)}')
print(f'Columns: {list(df.columns)}')
print(f'Vote count stats:')
print(df['vote_count'].describe())

good = df[df['vote_count'] >= 100]
print(f'\nMovies with 100+ votes: {len(good)}')

print('\nSample titles with 100+ votes:')
print(good[['tmdb_id','title','genres','vote_average','vote_count']].sort_values('vote_count', ascending=False).head(20).to_string())

# Check existing dataset
existing = pd.read_csv('dataset.csv')
print(f'\nExisting dataset rows: {len(existing)}')
print(f'Existing columns: {list(existing.columns)}')

# Check overlap
overlap = set(existing['id']).intersection(set(good['tmdb_id']))
print(f'Overlapping IDs: {len(overlap)}')
