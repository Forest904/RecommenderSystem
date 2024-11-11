#BOOKS DATASET COVER BUILDER

from tqdm import tqdm
import pandas as pd
import requests

# Read the dataset from a CSV file
books = pd.read_csv('src/datasets/books_rs/books.csv')

# Keep only the first 10 rows to test the system
#books = books.head(10)

# Function to get book cover image URL for a given book title
def get_book_cover_url(title):
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

# Apply the function to the 'Title' column with a progress bar
tqdm.pandas(desc="Fetching Book Cover Images")
books['Image Url'] = books['Title'].progress_apply(get_book_cover_url)

# Keep only the 'Title' and 'Image Url' columns
books = books[['Title', 'Image Url']]

# Save the updated dataset to a new CSV file
books.to_csv('books_with_image_urls.csv', index=False)