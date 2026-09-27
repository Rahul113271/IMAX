import requests
import time

TMDB_API_KEY = 'c7ec19ffdd3279641fb606d19ceb9bb1'
for attempt in range(5):
    try:
        res = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query=Pushpa').json()
        if res.get('results'):
            for m in res['results']:
                if 'rule' in m['title'].lower() or '2' in m['title']:
                    print(f"Pushpa 2 ID: {m['id']}")
                    exit(0)
            print(f"Pushpa general ID: {res['results'][0]['id']}")
            break
    except Exception as e:
        time.sleep(1)
