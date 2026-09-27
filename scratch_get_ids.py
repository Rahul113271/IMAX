import pandas as pd
import os

BASE_DIR = r"d:\Downloads\Movie_Recommender_System-main\Movie_Recommender_System-main"
df = pd.read_csv(os.path.join(BASE_DIR, "dataset_merged.csv"))

titles = [
    'Dangal', 'Baahubali 2: The Conclusion', 'RRR', 'K.G.F: Chapter 2', 
    'Jawan', 'Pathaan', 'Animal', 'Bajrangi Bhaijaan', 'Secret Superstar', 
    'PK', 'Kalki 2898 AD', 'Salaar: Part 1 - Ceasefire', 'Sultan', '2.0', 
    'Baahubali: The Beginning', 'Sanju', 'Padmaavat', 'Tiger Zinda Hai', 
    'Dhoom 3', 'Leo'
]

ids = []
for t in titles:
    match = df[df['title'].str.lower() == t.lower()]
    if not match.empty:
        ids.append(str(match.iloc[0]['id']))
        print(f"'{t}': {match.iloc[0]['id']},")
    else:
        print(f"'{t}': NOT_FOUND,")

print(f"\nFinal list: [{', '.join(ids)}]")
