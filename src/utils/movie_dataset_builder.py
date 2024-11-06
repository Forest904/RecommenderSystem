import requests
import pandas as pd
from tqdm import tqdm
import time

API_KEY = '82417ab9f1c7a6dd9b77d70a30713116'  # Replace with your TMDb API key
BASE_URL = 'https://api.themoviedb.org/3'

# Initialize an empty list to store movie data
movies_data = []

# We will loop through the pages of popular movies
for page in tqdm(range(1, 501)):  # 20 movies per page, 500 pages for ~10,000 movies
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
    response = requests.get(url)
    time.sleep(0.5)  # Sleep for 0.3 seconds to avoid rate limiting
    if response.status_code != 200:
        print(f"Failed to fetch page {page}")
        continue
    data = response.json()
    for movie in data['results']:
        movie_id = movie['id']
        title = movie['title']
        
        # Fetch detailed info for each movie
        detail_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        detail_response = requests.get(detail_url)
        if detail_response.status_code != 200:
            print(f"Failed to fetch details for movie ID {movie_id}")
            continue
        details = detail_response.json()
        
        # Director is part of credits, fetch them
        credits_url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US"
        credits_response = requests.get(credits_url)
        if credits_response.status_code != 200:
            print(f"Failed to fetch credits for movie ID {movie_id}")
            continue
        credits = credits_response.json()
        
        # Get director's name
        director = None
        for crew_member in credits['crew']:
            if crew_member['job'] == 'Director':
                director = crew_member['name']
                break
        
        # Get genres
        genres = [genre['name'] for genre in details.get('genres', [])]
        
        movies_data.append({
            'Title': title,
            'Director': director,
            'Genres': ', '.join(genres)
        })

# Create a DataFrame and save to CSV
df = pd.DataFrame(movies_data)
df.to_csv('top_10000_movies.csv', index=False)
print("Dataset saved to 'top_10000_movies.csv'")
