import os
import pandas as pd
import requests

# Define dataset paths
MOVIE_DATASET_PATH = 'src/datasets/books_rs/movies_with_image_urls.csv'
BOOK_DATASET_PATH = 'src/datasets/books_rs/books_with_image_urls.csv'

# API URLs
TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
BOOK_API_URL = "http://openlibrary.org/search.json"

# API Keys
TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # Set this in your environment

# Load datasets into memory for faster access
def load_datasets():
    movies_df = pd.read_csv(MOVIE_DATASET_PATH) if os.path.exists(MOVIE_DATASET_PATH) else pd.DataFrame()
    books_df = pd.read_csv(BOOK_DATASET_PATH) if os.path.exists(BOOK_DATASET_PATH) else pd.DataFrame()
    return movies_df, books_df

movies_df, books_df = load_datasets()

def fetch_data(url, params):
    """Fetch data synchronously from an API."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Exception during fetch: {e}")
        return None

def get_content_from_dataset(title, dataset):
    """Retrieve content data from a dataset."""
    entry = dataset[dataset['Title'].str.lower() == title.lower()]
    if not entry.empty and 'Image Url' in entry.columns:
        return entry.iloc[0]['Image Url']
    return None

def fetch_movie_url(title):
    """Fetch movie image URL using TMDB API."""
    search_url = f"{TMDB_API_BASE_URL}/search/movie"
    params = {"query": title, "api_key": TMDB_API_KEY}
    search_response = fetch_data(search_url, params)

    if search_response and search_response.get('results'):
        movie_id = search_response['results'][0]['id']
        movie_url = f"{TMDB_API_BASE_URL}/movie/{movie_id}"
        details_params = {"api_key": TMDB_API_KEY, "append_to_response": "images"}
        details_response = fetch_data(movie_url, details_params)

        if details_response and 'images' in details_response:
            posters = details_response['images'].get('posters', [])
            if posters:
                file_path = posters[0].get('file_path', '')
                return f"https://image.tmdb.org/t/p/original{file_path}"
    return None

def fetch_book_url(title):
    """Fetch book cover image URL using OpenLibrary API."""
    params = {"title": title}
    response = fetch_data(BOOK_API_URL, params)
    if response and 'docs' in response and response['docs']:
        book = response['docs'][0]  # Assume the first result is the correct one
        if 'cover_i' in book:
            return f"http://covers.openlibrary.org/b/id/{book['cover_i']}-L.jpg"
    return None

def get_content_url(title, content_type):
    """Retrieve content URL either from the dataset or via API."""
    global movies_df, books_df

    if content_type == 'movie':
        url = get_content_from_dataset(title, movies_df)
        if url:
            return url

        # Fetch via API
        url = fetch_movie_url(title)
        if url:
            # Update dataset
            new_entry = pd.DataFrame([{"Title": title, "Image Url": url}])
            movies_df = pd.concat([movies_df, new_entry], ignore_index=True)
            movies_df.to_csv(MOVIE_DATASET_PATH, index=False)
            return url

    elif content_type == 'book':
        url = get_content_from_dataset(title, books_df)
        if url:
            return url

        # Fetch via API
        url = fetch_book_url(title)
        if url:
            # Update dataset
            new_entry = pd.DataFrame([{"Title": title, "Image Url": url}])
            books_df = pd.concat([books_df, new_entry], ignore_index=True)
            books_df.to_csv(BOOK_DATASET_PATH, index=False)
            return url

    return None

def get_batch_content_urls(titles, content_type):
    """Fetch content URLs for a batch of titles."""
    urls = [get_content_url(title, content_type) for title in titles]
    return urls

# Example usage
def fetch_urls_example():
    titles = ["Inception", "The Hobbit", "The Avengers"]  # Example titles
    content_type = "movie"  # or "book"

    urls = get_batch_content_urls(titles, content_type)
    for title, url in zip(titles, urls):
        print(f"{title}: {url}")

if __name__ == "__main__":
    fetch_urls_example()
