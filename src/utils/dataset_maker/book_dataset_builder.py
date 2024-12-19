import asyncio
import aiohttp
import pandas as pd
import numpy as np
import random
import logging
from tqdm import tqdm
from scipy.stats import truncnorm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORIES = ["juvenile-fiction", "fantasy", "science-fiction", "adventure", "thriller"]
BASE_SEARCH_URL = "https://openlibrary.org/search.json"
BASE_WORKS_URL = "https://openlibrary.org"
GENERIC_QUERY = "bestseller"

MAX_RESULTS = 100
BATCH_SIZE = 1000
CONCURRENCY = 5

# Set up distributions for ratings
# Vote Average: truncated normal between [1,5], mean=3.7, std=0.5
rating_mean = 3.7
rating_std = 0.5
lower, upper = 1, 5
a, b = (lower - rating_mean) / rating_std, (upper - rating_mean) / rating_std
rating_dist = truncnorm(a, b, loc=rating_mean, scale=rating_std)

# Vote Count: lognormal distribution
# median ~20, wide variance
log_mean = np.log(20)  # median around 20
log_sigma = 1.0
def generate_vote_count():
    count = int(np.random.lognormal(mean=log_mean, sigma=log_sigma))
    # Ensure at least 1 rating
    return max(count, 1)

async def fetch_url(session, url):
    retries = 3
    backoff = 1.0
    for attempt in range(retries):
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.info(f"Non-200 response ({resp.status}) from {url}, retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                    backoff *= 2
        except aiohttp.ClientError as e:
            logger.info(f"Client error: {e}. Retrying in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff *= 2
    logger.info(f"Failed to fetch {url} after {retries} retries.")
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
    Parse a single doc and fetch the plot concurrently.
    """
    book_id = doc.get('key')
    title = doc.get('title')
    if not title:
        return None

    authors = doc.get('author_name', [])
    author_str = ', '.join(authors) if authors else None

    subjects = doc.get('subject', [])
    genres_str = ', '.join(subjects) if subjects else None

    # Generate statistically grounded Vote Average and Vote Count
    vote_average = rating_dist.rvs()
    vote_average = round(vote_average, 1)  # Round to one decimal
    vote_count = generate_vote_count()

    # Release date
    release_date = None
    if 'first_publish_year' in doc:
        release_date = str(doc['first_publish_year'])
    elif 'publish_date' in doc and doc['publish_date']:
        release_date = doc['publish_date'][0]

    cover_id = doc.get('cover_i')
    large_cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None

    # Fetch the plot
    plot = await fetch_plot(session, book_id)
    if plot is None:
        logger.info(f"No plot found for {book_id} (Title: {title}).")

    book_data = {
        'ID': book_id,
        'Title': title,
        'Author': author_str,
        'Genres': genres_str,
        'Plot': plot,
        'Vote Average': vote_average,
        'Vote Count': vote_count,
        'Release Date': release_date,
        'Large Cover URL': large_cover_url
    }
    return book_data

async def async_fetch_books(query, total_needed=100, fetched_ids=None, subject_mode=False):
    """
    Fetch books from Open Library. If subject_mode=True, treat 'query' as a subject.
    Otherwise, treat it as a general search query.
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
                    if subject_mode:
                        url = f"{BASE_SEARCH_URL}?subject={query}&limit={MAX_RESULTS}&offset={offset}"
                    else:
                        url = f"{BASE_SEARCH_URL}?q={query}&limit={MAX_RESULTS}&offset={offset}"
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

                    # Parse all docs in parallel
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

    logger.info("Fetching books from prioritized categories...")
    for i, category in enumerate(categories):
        need = books_per_category + (1 if i < remainder else 0)
        logger.info(f" - Fetching {need} books from category: {category}")
        category_books, fetched_ids = await async_fetch_books(category, total_needed=need, fetched_ids=fetched_ids, subject_mode=True)
        books_data.extend(category_books)

    return books_data[:total_books], fetched_ids

async def async_fetch_popular_books_by_relevance(total_books=500, query=GENERIC_QUERY, fetched_ids=None):
    logger.info(f"Fetching {total_books} books by relevance for query '{query}'...")
    books, fetched_ids = await async_fetch_books(query, total_needed=total_books, fetched_ids=fetched_ids, subject_mode=False)
    return books, fetched_ids

def save_to_csv(data, filename='popular_books.csv'):
    df = pd.DataFrame(data)
    # Remove items without Plot and drop 'ID' column
    df = df.dropna(subset=['Plot'])
    if 'ID' in df.columns:
        df = df.drop(columns=['ID'])
    df.to_csv(filename, index=False)
    logger.info(f"Saved {len(df)} books to {filename}")

async def main(total_books=10000):
    half = total_books // 2

    all_books = []
    fetched_ids = set()

    # Fetch from categories
    category_books, fetched_ids = await async_fetch_books_by_categories(CATEGORIES, total_books=half, fetched_ids=fetched_ids)
    all_books.extend(category_books)

    # Save intermediate results if large amount fetched
    if len(all_books) >= BATCH_SIZE:
        save_to_csv(all_books, filename='partial_categories_books.csv')

    # Fetch by a general query
    relevance_books, fetched_ids = await async_fetch_popular_books_by_relevance(total_books=half, query=GENERIC_QUERY, fetched_ids=fetched_ids)
    all_books.extend(relevance_books)

    # Trim to total if needed
    all_books = all_books[:total_books]

    # Final save
    save_to_csv(all_books, filename='popular_books.csv')

if __name__ == "__main__":
    asyncio.run(main(total_books=10000))
