import imdb
import requests
import pandas as pd

#Check the data before fetching it from api
df_movies_images_url = pd.read_csv('src/datasets/books_rs/movies_with_image_urls.csv')
df_books_images_url = pd.read_csv('src/datasets/books_rs/books_with_image_urls.csv')

# Function to get movie image URL for a given movie title
def get_movie_image_url(title):
    # Check if the URL is already in the dataset
    movie_entry = df_movies_images_url[df_movies_images_url['Title'].str.lower() == title.lower()]
    if not movie_entry.empty and 'Image Url' in movie_entry.columns:
        image_url = movie_entry['Image Url'].iloc[0]
        if pd.notna(image_url):
            return image_url
    
    # Create an instance of the IMDb class
    ia = imdb.IMDb()

    # Search for the movie by title
    search_results = ia.search_movie(title)

    if not search_results:
        print("Movie not found!")
        return

    # Fetch the first movie in the search results
    movie = search_results[0]
    ia.update(movie)

    # Get the movie's image URL
    image_url = movie.get('full-size cover url')

    if image_url:
        return image_url
    else:
        print(f"No image found for '{title}'.")

# Function to get book cover image URL for a given book title
def get_book_cover_url(title):
    # Check if the URL is already in the dataset
    book_entry = df_books_images_url[df_books_images_url['Title'].str.lower() == title.lower()]
    if not book_entry.empty and 'Image Url' in book_entry.columns:
        image_url = book_entry['Image Url'].iloc[0]
        if pd.notna(image_url):
            return image_url

    try:
        # Search for the book by title using Open Library Search API
        params = {'title': title}
        response = requests.get('http://openlibrary.org/search.json', params=params)
        if response.status_code == 200:
            data = response.json()
            if data['docs']:
                # Assume the first result is the correct one
                book = data['docs'][0]
                # Get the cover id if available
                if 'cover_i' in book:
                    cover_id = book['cover_i']
                    # Construct the cover image URL
                    image_url = f'http://covers.openlibrary.org/b/id/{cover_id}-L.jpg'  # '-L' for large size
                    return image_url
                else:
                    return None
            else:
                return None
        else:
            print(f"Error fetching data for '{title}': Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching cover image for '{title}': {e}")
        return None
