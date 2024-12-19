import requests
import pandas as pd
from tqdm import tqdm

CATEGORIES = ["juvenile-fiction", "fantasy", "science-fiction", "adventure", "thriller"]
API_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
GENERIC_QUERY = "bestseller"  # A generic query to fetch popular books by relevance

def fetch_books(query, total_needed=100, max_results=40, order_by='relevance'):
    """
    Fetch books from the Google Books API given a query, until we have 'total_needed' books.
    This is a generic fetching function that doesn't assume categories.
    """
    books_data = []
    start_index = 0
    
    while len(books_data) < total_needed:
        url = (f"{API_BASE_URL}?q={query}"
               f"&startIndex={start_index}&maxResults={max_results}"
               f"&orderBy={order_by}")
        
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Error: {resp.status_code}")
            break
        
        data = resp.json()
        items = data.get('items', [])
        if not items:
            # No more results
            break
        
        for item in items:
            info = item.get('volumeInfo', {})
            title = info.get('title')
            if not title:
                continue
            
            authors = info.get('authors', [])
            director = ', '.join(authors) if authors else None  
            genres = info.get('categories', [])
            genres_str = ', '.join(genres) if genres else None
            plot = info.get('description', '')
            vote_average = info.get('averageRating', None)
            vote_count = info.get('ratingsCount', None)
            release_date = info.get('publishedDate', '')

            image_links = info.get('imageLinks', {})
            # Attempt to pick a relatively large image
            large_cover_url = (image_links.get('extraLarge') or image_links.get('large') or 
                               image_links.get('medium') or image_links.get('small') or 
                               image_links.get('thumbnail'))
            
            books_data.append({
                'Title': title,
                'Author': director,   # Keeping the same field name for comparability
                'Genres': genres_str,
                'Plot': plot,
                'Vote Average': vote_average,
                'Vote Count': vote_count,
                'Release Date': release_date,
                'Large Cover URL': large_cover_url
            })

            if len(books_data) >= total_needed:
                break
        start_index += max_results
    
    return books_data

def fetch_books_by_categories(categories, total_books=500):
    """
    Fetches books from a set of categories and combines them into a single dataset.
    Distributes total_books across categories.
    """
    books_data = []
    books_per_category = total_books // len(categories)
    remainder = total_books % len(categories)

    print("Fetching books from prioritized categories...")
    for i, category in enumerate(categories):
        need = books_per_category + (1 if i < remainder else 0)
        print(f" - Fetching {need} books from category: {category}")
        query = f"subject:{category}"
        category_books = fetch_books(query, total_needed=need, order_by='relevance')
        books_data.extend(category_books)
    
    return books_data[:total_books]

def fetch_popular_books_by_relevance(total_books=500, query=GENERIC_QUERY):
    """
    Fetches books from a generic query sorted by relevance.
    """
    print(f"Fetching {total_books} books by relevance for query '{query}'...")
    return fetch_books(query, total_needed=total_books, order_by='relevance')

def save_to_csv(data, filename='popular_books.csv'):
    df = pd.DataFrame(data)
    # Drop rows missing critical fields if necessary
    df = df.dropna()
    df.to_csv(filename, index=False)
    print(f"Saved dataset to {filename}")

def main(total_books):
    half = total_books // 2
    # Half from the priority categories
    category_books = fetch_books_by_categories(CATEGORIES, total_books=half)

    # Half by just relevance
    relevance_books = fetch_popular_books_by_relevance(total_books=half)

    # Combine them
    combined_books = category_books + relevance_books

    # If total_books is odd, we might be off by one. Just ensure we don't exceed.
    combined_books = combined_books[:total_books]

    save_to_csv(combined_books, filename='popular_books.csv')

if __name__ == "__main__":
    # Adjust the total number of books as needed
    main(total_books=10000)
