import os
import pandas as pd
import aiohttp
import asyncio

# Define dataset paths
MOVIE_DATASET_PATH = 'src/datasets/books_rs/movies_with_image_urls.csv'
BOOK_DATASET_PATH = 'src/datasets/books_rs/books_with_image_urls.csv'

# API URLs
TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
BOOK_API_URL = "http://openlibrary.org/search.json"

# API Keys
TMDB_API_KEY = os.getenv("eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4MjQxN2FiOWYxYzdhNmRkOWI3N2Q3MGEzMDcxMzExNiIsIm5iZiI6MTczMDkxMzQxMi4yMDQsInN1YiI6IjY3MmJhNDg0MjZiNjA1YmMxOWU1YWU0MyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.BQVyuNeQLC_EbQS4KRZ5neZJBGvHTNuWW1MO756VONw")  # Set this in your environment

# Load datasets into memory for faster access
def load_datasets():
    movies_df = pd.read_csv(MOVIE_DATASET_PATH) if os.path.exists(MOVIE_DATASET_PATH) else pd.DataFrame()
    books_df = pd.read_csv(BOOK_DATASET_PATH) if os.path.exists(BOOK_DATASET_PATH) else pd.DataFrame()
    return movies_df, books_df

movies_df, books_df = load_datasets()

async def fetch_data(session, url, params):
    """Fetch data asynchronously from an API."""
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error {response.status} for URL: {url} with params: {params}")
                return None
    except Exception as e:
        print(f"Exception during fetch: {e}")
        return None

def get_content_from_dataset(title, dataset):
    """Retrieve content data from a dataset."""
    entry = dataset[dataset['Title'].str.lower() == title.lower()]
    if not entry.empty and 'Image Url' in entry.columns:
        return entry.iloc[0]['Image Url']
    return None

async def fetch_movie_url(session, title):
    """Fetch movie image URL using TMDB API."""
    search_url = f"{TMDB_API_BASE_URL}/search/movie"
    params = {"query": title, "api_key": TMDB_API_KEY}
    search_response = await fetch_data(session, search_url, params)

    if search_response and search_response.get('results'):
        movie_id = search_response['results'][0]['id']
        movie_url = f"{TMDB_API_BASE_URL}/movie/{movie_id}"
        details_params = {"api_key": TMDB_API_KEY, "append_to_response": "images"}
        details_response = await fetch_data(session, movie_url, details_params)

        if details_response and 'images' in details_response:
            posters = details_response['images'].get('posters', [])
            if posters:
                file_path = posters[0].get('file_path', '')
                return f"https://image.tmdb.org/t/p/original{file_path}"
    return None

async def fetch_book_url(session, title):
    """Fetch book cover image URL using OpenLibrary API."""
    params = {"title": title}
    response = await fetch_data(session, BOOK_API_URL, params)
    if response and 'docs' in response and response['docs']:
        book = response['docs'][0]  # Assume the first result is the correct one
        if 'cover_i' in book:
            return f"http://covers.openlibrary.org/b/id/{book['cover_i']}-L.jpg"
    return None

async def get_content_url(title, content_type):
    """Retrieve content URL either from the dataset or via API."""
    global movies_df, books_df

    if content_type == 'movie':
        url = get_content_from_dataset(title, movies_df)
        if url:
            return url

        # Fetch via API
        async with aiohttp.ClientSession() as session:
            url = await fetch_movie_url(session, title)
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
        async with aiohttp.ClientSession() as session:
            url = await fetch_book_url(session, title)
            if url:
                # Update dataset
                new_entry = pd.DataFrame([{"Title": title, "Image Url": url}])
                books_df = pd.concat([books_df, new_entry], ignore_index=True)
                books_df.to_csv(BOOK_DATASET_PATH, index=False)
                return url

    return None

async def get_batch_content_urls(titles, content_type):
    """Fetch content URLs for a batch of titles concurrently."""
    tasks = [get_content_url(title, content_type) for title in titles]
    return await asyncio.gather(*tasks)

# Example usage
def fetch_urls_example():
    titles = ["Inception", "The Hobbit", "The Avengers"]  # Example titles
    content_type = "movie"  # or "book"

    urls = asyncio.run(get_batch_content_urls(titles, content_type))
    for title, url in zip(titles, urls):
        print(f"{title}: {url}")

if __name__ == "__main__":
    fetch_urls_example()
