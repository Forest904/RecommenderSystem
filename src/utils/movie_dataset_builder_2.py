import requests
import pandas as pd
from tqdm import tqdm
import time

API_KEY = ''  # Replace with your TMDb API key
BASE_URL = 'https://api.themoviedb.org/3'

# Initialize an empty list to store movie data
movies_data = []

# Total number of movies to fetch
total_movies = 10000
movies_per_page = 20  # Number of movies per page returned by the API
total_pages = (total_movies // movies_per_page) + 1

for page in tqdm(range(1, total_pages + 1)):
    # Fetch popular movies
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page {page}: {response.status_code}")
        continue
    data = response.json()
    for movie in data['results']:
        movie_id = movie['id']
        title = movie['title']
        vote_average = movie.get('vote_average', 0)
        vote_count = movie.get('vote_count', 0)
        
        # Fetch detailed info for each movie
        detail_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        detail_response = requests.get(detail_url)
        if detail_response.status_code != 200:
            print(f"Failed to fetch details for movie ID {movie_id}: {detail_response.status_code}")
            continue
        details = detail_response.json()
        
        # Get genres
        genres = [genre['name'] for genre in details.get('genres', [])]
        
        # Get plot from 'overview' field
        plot = details.get('overview', None)
        
        # Fetch credits to get the director
        credits_url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US"
        credits_response = requests.get(credits_url)
        if credits_response.status_code != 200:
            print(f"Failed to fetch credits for movie ID {movie_id}: {credits_response.status_code}")
            continue
        credits = credits_response.json()
        
        # Get director's name
        director = None
        for crew_member in credits.get('crew', []):
            if crew_member['job'] == 'Director':
                director = crew_member['name']
                break
        
        movies_data.append({
            'Title': title,
            'Director': director,
            'Genres': ', '.join(genres),
            'Plot': plot,
            'Vote Average': vote_average,
            'Vote Count': vote_count
        })
        
        # Check if we've collected enough movies
        if len(movies_data) >= total_movies:
            break
    
    # Sleep briefly to comply with API rate limits
    time.sleep(0.25)  # Adjust the sleep time as necessary
    if len(movies_data) >= total_movies:
        break

# Create a DataFrame and save to CSV
df = pd.DataFrame(movies_data)

# Save to CSV with the attribution note
df.to_csv('top_10000_movies.csv', index=False)
print("Dataset saved to 'top_10000_movies.csv'")

