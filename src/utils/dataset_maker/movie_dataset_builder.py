import os
import time
import requests
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# API Configurations
API_KEY = os.getenv('TMDB_API_KEY', '82417ab9f1c7a6dd9b77d70a30713116')
BASE_URL = 'https://api.themoviedb.org/3'
HEADERS = {'User-Agent': 'MovieFetcher/1.0'}

if not API_KEY:
    raise ValueError("Please set the TMDB_API_KEY environment variable.")

def make_request(url, retries=5):
    """Make a GET request with retries and exponential backoff."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS)
            print(f"[DEBUG] Request: {url} | Status: {response.status_code} | Attempt: {attempt+1}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt
                print(f"Rate limited. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error {response.status_code}: {url}")
                break
        except Exception as e:
            print(f"Request failed: {e}")
            time.sleep(2)
    return None

def fetch_movie_data(page):
    """Fetch popular movies for a specific page."""
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
    return make_request(url)

def fetch_movie_details(movie_id):
    """Fetch movie details and credits using append_to_response."""
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits,images"
    return make_request(url)

def get_large_cover_url(images):
    """Get the largest available poster URL from images."""
    if not images or 'posters' not in images:
        return None
    posters = images['posters']
    if posters:
        largest_poster = sorted(posters, key=lambda x: x.get('width', 0), reverse=True)[0]
        file_path = largest_poster.get('file_path', '')
        if file_path:
            return f"https://image.tmdb.org/t/p/original{file_path}"
    return None

def process_movies(total_movies=100):
    """Fetch and process movie data efficiently."""
    movies_data = []
    total_pages = (total_movies // 20) + 1  
    fetched_ids = set()

    print("Fetching movie data...")
    # Fetch the list of movies concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(tqdm(executor.map(fetch_movie_data, range(1, total_pages + 1)), total=total_pages))

    # Extract all movie IDs
    movie_ids = []
    for data in results:
        if not data:
            continue
        for movie in data.get('results', []):
            movie_id = movie['id']
            if movie_id not in fetched_ids:
                fetched_ids.add(movie_id)
                movie_ids.append(movie_id)

    print("Fetching movie details...")
    movies_details = []
    # Use concurrency for fetching details too
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_id = {executor.submit(fetch_movie_details, mid): mid for mid in movie_ids}
        for future in tqdm(as_completed(future_to_id), total=len(movie_ids)):
            details = future.result()
            if details:
                movies_details.append(details)

    # Process fetched movie details
    print("Processing movie details...")
    for details in tqdm(movies_details):
        genres = ', '.join(genre['name'] for genre in details.get('genres', []))
        director = next((crew['name'] for crew in details.get('credits', {}).get('crew', [])
                         if crew['job'] == 'Director'), None)
        large_cover_url = get_large_cover_url(details.get('images', {}))

        movies_data.append({
            'Title': details.get('title', ''),
            'Director': director,
            'Genres': genres,
            'Plot': details.get('overview', ''),
            'Vote Average': details.get('vote_average', 0),
            'Vote Count': details.get('vote_count', 0),
            'Release Date': details.get('release_date', ''),
            'Large Cover URL': large_cover_url
        })

    return movies_data

def save_to_csv(data, filename='popular_movies.csv'):
    """Save the movie data to a CSV file after cleaning null rows."""
    df = pd.DataFrame(data)
    df = df.dropna()
    df.to_csv(filename, index=False)
    print(f"Dataset saved to '{filename}'")

def main():
    """Main function to fetch, process, and save movie data."""
    try:
        movies = process_movies()
        save_to_csv(movies)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
