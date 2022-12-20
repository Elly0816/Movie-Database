import requests
from pprint import pprint


def search(title):
    API_KEY = '0365943eacf29ed6cf09778ecf431708'
    # headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"api_key": API_KEY,
              "query": title,
              "language": 'en-US'}
    response = requests.get('https://api.themoviedb.org/3/search/movie', params=params)
    response.raise_for_status()
    movies = response.json()['results'][0]['id']
    pprint(movies)
    return movies


def find(title):
    id = search(title)
    url = f"https://api.themoviedb.org/3/movie/{id}"
    API_KEY = '0365943eacf29ed6cf09778ecf431708'
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    result = response.json()
    pprint(result)


find('Django')