import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('dataset_merged.csv')

# Telugu movies
te = df[df['original_language']=='te']
print(f'Telugu movies: {len(te)}')
print()
print(te[['id','title','vote_average','vote_count','release_date']].sort_values('vote_count', ascending=False).to_string())

# Also check other Indian languages
print('\n--- Indian Language Breakdown ---')
indian_langs = {'te': 'Telugu', 'hi': 'Hindi', 'ta': 'Tamil', 'ml': 'Malayalam', 'kn': 'Kannada', 'bn': 'Bengali', 'mr': 'Marathi', 'pa': 'Punjabi'}
for code, name in indian_langs.items():
    count = len(df[df['original_language']==code])
    print(f'{name} ({code}): {count} movies')
