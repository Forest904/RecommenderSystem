
#MOVIES DATASET IMAGES BUILDER 

import pandas as pd
from imdb import IMDb
from tqdm import tqdm

# Read the dataset from a CSV file
movies = pd.read_csv('src/datasets/books_rs/movies.csv')

# Keep only the first 10 rows to test the system
#movies = movies.head(10)

# Initialize the IMDb object
ia = IMDb()

# Function to get IMDb image URL for a given movie title
def get_imdb_image_url(title):
    try:
        # Search for the movie by title
        search_results = ia.search_movie(title)
        if search_results:
            # Assume the first result is the correct one
            movie = search_results[0]
            # Update the movie object to get full details
            ia.update(movie)
            # Check if 'full-size cover url' is available
            if 'full-size cover url' in movie.keys():
                return movie['full-size cover url']
            # Fallback to 'cover url' if 'full-size cover url' is not available
            elif 'cover url' in movie.keys():
                return movie['cover url']
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error fetching Image URL for '{title}': {e}")
        return None

# Apply the function to the 'Title' column with a progress bar
tqdm.pandas(desc="Fetching Image URLs")
movies['Image Url'] = movies['Title'].progress_apply(get_imdb_image_url)

# Keep only the 'Title' and 'Image Url' columns
movies = movies[['Title', 'Image Url']]

# Save the updated dataset to a new CSV file
movies.to_csv('movies_with_image.csv', index=False)



