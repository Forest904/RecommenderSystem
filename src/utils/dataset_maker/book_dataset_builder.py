import asyncio
import aiohttp
import pandas as pd
import numpy as np
import logging
from tqdm import tqdm
from scipy.stats import truncnorm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORIES = [
    "Juvenile Fiction",
    "Fantasy",
    "Science Fiction",
    "Adventure",
    "Thriller",
    "Romance",
    "Mystery",
    "Horror",
    "Biography",
    "History",
    "Poetry",
    "Classics",
    "Children's Literature",
    "Young Adult",
    "Nonfiction",
    "Science",
    "Self-Help",
    "Cooking",
    "Art",
    "Travel",
    "Sports",
    "Comics",
    "Graphic Novels",
    "Manga",
    "Music",
    "Religion",
    "Philosophy",
    "Psychology",
    "Business",
    "Economics",
    "Technology",
    "Crafts",
    "Hobbies",
    "Health",
]

BASE_SEARCH_URL = "https://openlibrary.org/search.json"
BASE_WORKS_URL = "https://openlibrary.org"

MAX_RESULTS = 100
BATCH_SIZE = 100
CONCURRENCY = 5

# Set up distributions for ratings
# Vote Average: truncated normal between [1,5] (mean=3.7, std=0.5)
rating_mean = 3.7
rating_std = 0.5
lower, upper = 1, 5
a, b = (lower - rating_mean) / rating_std, (upper - rating_mean) / rating_std
rating_dist = truncnorm(a, b, loc=rating_mean, scale=rating_std)

# Vote Count: lognormal distribution (median around 20)
log_mean = np.log(20)
log_sigma = 1.0
def generate_vote_count():
    count = int(np.random.lognormal(mean=log_mean, sigma=log_sigma))
    return max(count, 1)

async def fetch_url(session, url):
    max_retries = 3
    backoff = 1.0
    for attempt in range(max_retries):
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.info(
                        f"Non-200 response ({resp.status}) from {url}, retrying in {backoff:.1f}s (attempt {attempt+1}/{max_retries})..."
                    )
                    await asyncio.sleep(backoff)
                    backoff *= 2  # exponential backoff
        except aiohttp.ClientError as e:
            logger.info(
                f"Client error: {e}. Retrying in {backoff:.1f}s (attempt {attempt+1}/{max_retries})..."
            )
            await asyncio.sleep(backoff)
            backoff *= 2
    logger.info(f"Failed to fetch {url} after {max_retries} retries.")
    return None

async def fetch_plot(session, work_key):
    """
    Fetch the plot (description) for a given work from the Open Library works endpoint.
    """
    url = f"{BASE_WORKS_URL}{work_key}.json"
    data = await fetch_url(session, url)
    if data is None:
        return None
    desc = data.get('description')
    if isinstance(desc, dict):
        return desc.get('value')
    elif isinstance(desc, str):
        return desc
    return None

async def parse_book_item(session, doc):
    """
    Parse a single document from the search results and fetch its plot.
    """
    book_id = doc.get('key')
    title = doc.get('title')
    if not title:
        return None

    authors = doc.get('author_name', [])
    author_str = ', '.join(authors) if authors else None

    subjects = doc.get('subject', [])
    genres_str = ', '.join(subjects) if subjects else None

    vote_average = rating_dist.rvs()
    vote_average = round(vote_average, 1)
    vote_count = generate_vote_count()

    release_date = None
    if 'first_publish_year' in doc:
        release_date = str(doc['first_publish_year'])
    elif 'publish_date' in doc and doc['publish_date']:
        release_date = doc['publish_date'][0]

    plot = await fetch_plot(session, book_id)
    if plot is None:
        logger.info(f"No plot found for {book_id} (Title: {title}).")

    # Build the book page link (instead of an image cover)
    book_link = f"{BASE_WORKS_URL}{book_id}"

    book_data = {
        'ID': book_id,
        'Title': title,
        'Author': author_str,
        'Genres': genres_str,
        'Plot': plot,
        'Vote Average': vote_average,
        'Vote Count': vote_count,
        'Release Date': release_date,
        'Book Link': book_link
    }
    return book_data

async def async_fetch_books(query, total_needed=100, fetched_ids=None, subject_mode=False):
    """
    Fetch books from Open Library using the given subject query.
    """
    if fetched_ids is None:
        fetched_ids = set()

    books_data = []
    pages = (total_needed // MAX_RESULTS) + (1 if total_needed % MAX_RESULTS else 0)

    async with aiohttp.ClientSession() as session:
        pbar = tqdm(total=total_needed, desc=f"Fetching {query}", unit='book')
        try:
            start_page = 0
            while len(books_data) < total_needed and start_page < pages:
                end_page = min(start_page + CONCURRENCY, pages)
                tasks = []
                for page_i in range(start_page, end_page):
                    offset = page_i * MAX_RESULTS
                    # Using the category as subject
                    url = f"{BASE_SEARCH_URL}?subject={query}&limit={MAX_RESULTS}&offset={offset}"
                    tasks.append(fetch_url(session, url))
                results = await asyncio.gather(*tasks)
                any_items_found = False
                for data in results:
                    if data is None:
                        continue
                    docs = data.get('docs', [])
                    if not docs:
                        continue
                    any_items_found = True
                    parse_tasks = [parse_book_item(session, doc) for doc in docs if doc.get('key') not in fetched_ids]
                    parsed_results = await asyncio.gather(*parse_tasks)
                    for res in parsed_results:
                        if res and res['ID'] not in fetched_ids:
                            fetched_ids.add(res['ID'])
                            books_data.append(res)
                            pbar.update(1)
                            if len(books_data) >= total_needed:
                                break
                    if len(books_data) >= total_needed:
                        break
                if not any_items_found:
                    break
                start_page = end_page
                await asyncio.sleep(0.1)
        finally:
            pbar.close()
    return books_data, fetched_ids

async def async_fetch_books_by_categories(categories, total_books=500, fetched_ids=None):
    if fetched_ids is None:
        fetched_ids = set()
    books_data = []
    books_per_category = total_books // len(categories)
    remainder = total_books % len(categories)

    logger.info("Fetching books by categories...")
    for i, category in enumerate(categories):
        need = books_per_category + (1 if i < remainder else 0)
        logger.info(f" - Fetching {need} books from category: {category}")
        category_books, fetched_ids = await async_fetch_books(category, total_needed=need, fetched_ids=fetched_ids, subject_mode=True)
        books_data.extend(category_books)
    return books_data[:total_books], fetched_ids

def save_to_csv(data, filename='popular_books.csv'):
    df = pd.DataFrame(data)
    initial_count = len(df)
    df = df.dropna(subset=['Plot'])
    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        logger.info(f"Deleted {dropped_count} books due to missing plot section.")
    if 'ID' in df.columns:
        df = df.drop(columns=['ID'])
    df.to_csv(filename, index=False)
    logger.info(f"Saved {len(df)} books to {filename}")

async def main(total_books=1000):
    fetched_ids = set()
    # Fetch books only by categories
    category_books, fetched_ids = await async_fetch_books_by_categories(CATEGORIES, total_books=total_books, fetched_ids=fetched_ids)
    save_to_csv(category_books, filename='popular_books.csv')

if __name__ == "__main__":
    asyncio.run(main(total_books=1000))
