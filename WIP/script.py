import asyncio
import aiohttp
import pandas as pd
from tqdm import tqdm
from collections import defaultdict

# -------------------------------
# Function to fetch book details
# -------------------------------
async def fetch_book_details(session, title, author, semaphore):
    """
    Queries the Google Books API for a book using its title and author.
    Returns a dictionary with the desired attributes.
    
    Note: The book_url is taken from volumeInfo.infoLink, which is a link to the book's info page.
    """
    async with semaphore:  # control concurrency
        # Build the query using title and author
        query = f"intitle:{title}+inauthor:{author}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        try:
            async with session.get(url) as response:
                data = await response.json()
                if data.get("totalItems", 0) > 0:
                    # Use the first matching result
                    item = data["items"][0]
                    volume = item.get("volumeInfo", {})

                    title_out    = volume.get("title", title)
                    authors      = volume.get("authors", [author])
                    author_out   = authors[0] if authors else author
                    genres       = volume.get("categories", [])
                    plot         = volume.get("description", "")
                    vote_average = volume.get("averageRating", None)
                    vote_count   = volume.get("ratingsCount", None)
                    release_date = volume.get("publishedDate", "")
                    
                    # For cover, try to get a "large" image; if not available, fallback to "thumbnail".
                    image_links     = volume.get("imageLinks", {})
                    large_cover_url = image_links.get("large", image_links.get("thumbnail", ""))
                    # Set book_url to infoLink (the book page), not an image URL.
                    book_url        = volume.get("infoLink", "")
                else:
                    # No match found: use defaults.
                    title_out = title
                    author_out = author
                    genres = []
                    plot = ""
                    vote_average = None
                    vote_count = None
                    release_date = ""
                    large_cover_url = ""
                    book_url = ""
                return {
                    "title": title_out,
                    "author": author_out,
                    "genres": genres,
                    "plot": plot,
                    "vote_average": vote_average,
                    "vote_count": vote_count,
                    "release_date": release_date,
                    "large_cover_url": large_cover_url,
                    "book_url": book_url
                }
        except Exception as e:
            # On error, return default values.
            return {
                "title": title,
                "author": author,
                "genres": [],
                "plot": "",
                "vote_average": None,
                "vote_count": None,
                "release_date": "",
                "large_cover_url": "",
                "book_url": ""
            }

# -------------------------------
# Function to process all books
# -------------------------------
async def process_books(df, concurrency=200):
    """
    Processes each book in the DataFrame asynchronously.
    The concurrency parameter controls how many simultaneous API calls are made.
    """
    semaphore = asyncio.Semaphore(concurrency)
    tasks = []
    
    async with aiohttp.ClientSession() as session:
        for _, row in df.iterrows():
            tasks.append(fetch_book_details(session, row["Title"], row["Authors"], semaphore))
        
        results = []
        # Use tqdm to display progress as tasks complete.
        for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Processing Books"):
            result = await task
            results.append(result)
            
    return results

# -------------------------------
# Functions for cleaning results
# -------------------------------
def get_missing_attributes(row):
    """
    For a given row (as a dict), returns a list of keys that are considered "empty".
    Empty is defined as:
      - None,
      - A string that is empty (or whitespace only),
      - A list with zero elements.
    """
    missing = []
    for key, value in row.items():
        if value is None:
            missing.append(key)
        elif isinstance(value, str) and value.strip() == "":
            missing.append(key)
        elif isinstance(value, list) and len(value) == 0:
            missing.append(key)
    return missing

def clean_dataframe(df):
    """
    Removes any rows from df that have any empty attribute.
    Also, counts the missing occurrences for each attribute among the removed rows.
    Returns the cleaned DataFrame and a dictionary with counts of missing attributes.
    """
    missing_counts = defaultdict(int)
    rows_to_keep = []
    removed_rows = 0

    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        missing = get_missing_attributes(row_dict)
        if missing:
            removed_rows += 1
            for attr in missing:
                missing_counts[attr] += 1
        else:
            rows_to_keep.append(idx)

    cleaned_df = df.loc[rows_to_keep].reset_index(drop=True)
    return cleaned_df, removed_rows, missing_counts

# -------------------------------
# Main function
# -------------------------------
def main():
    # Load the original dataset (adjust the path/filename as needed).
    df = pd.read_csv("WIP\BooksDataset100k.csv")
    
    # Process the books asynchronously.
    results = asyncio.run(process_books(df))
    
    # Create a new DataFrame from the API results.
    new_df = pd.DataFrame(results)
    
    # Clean the DataFrame: remove rows with any empty attribute.
    cleaned_df, removed_rows, missing_counts = clean_dataframe(new_df)
    print(f"\nCleaning dataset: removed {removed_rows} rows with empty attributes.")
    print("Breakdown of missing attributes among deleted rows:")
    for attr, count in missing_counts.items():
        print(f"  {attr}: {count} rows missing")
    
    # Save the final, cleaned dataset.
    cleaned_df.to_csv("books_expanded.csv", index=False)
    print("\nFinished writing books_expanded.csv")

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    main()
