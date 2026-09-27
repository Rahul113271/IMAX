import requests
import time

TMDB_API_KEY = 'c7ec19ffdd3279641fb606d19ceb9bb1'
titles = ['Pushpa 2', 'Dhurandhar', 'Kalki 2898 AD']

for t in titles:
    for attempt in range(3):
        try:
            res = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={t}').json()
            if res.get('results'):
                print(f"{t}: {res['results'][0]['id']}")
            else:
                print(f"{t}: NOT FOUND")
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {t}: {e}")
            time.sleep(2)
