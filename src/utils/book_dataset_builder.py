import requests
import pandas as pd
from tqdm import tqdm
import time  # For adding delays

BASE_URL = 'https://openlibrary.org'

# Initialize an empty list to store book data
books_data = []

# Since Open Library doesn't provide a direct endpoint for the top 10,000 books,
# we'll use multiple popular subjects to gather a large dataset.
subjects = ['bestsellers', 'fiction', 'nonfiction', 'fantasy', 'science_fiction',
            'mystery', 'thriller', 'romance', 'historical', 'biography']

for subject in tqdm(subjects, desc='Processing subjects'):
    subject_url = f"{BASE_URL}/subjects/{subject}.json?limit=1000"
    response = requests.get(subject_url)
    time.sleep(0.3)  # Adding a delay to respect API rate limits
    if response.status_code != 200:
        print(f"Failed to fetch books for subject: {subject}")
        continue
    data = response.json()
    works = data.get('works', [])
    for work in works:
        title = work.get('title')
        
        # Get authors
        authors = [author['name'] for author in work.get('authors', [])]
        
        # Get subjects (genres)
        genres = work.get('subject', [])
        
        books_data.append({
            'Title': title,
            'Author': ', '.join(authors),
            'Genres': ', '.join(genres)
        })
        # Optional: Break if we've collected enough books
        if len(books_data) >= 10000:
            break
    if len(books_data) >= 10000:
        break

# Remove duplicates
df = pd.DataFrame(books_data).drop_duplicates(subset=['Title', 'Author'])

# Ensure we have at most 10,000 entries
df = df.head(10000)

# Save to CSV
df.to_csv('top_books.csv', index=False)
print("Dataset saved to 'top_books.csv'")
