import pandas as pd
from fuzzywuzzy import process
from multiprocessing import Pool, freeze_support
from functools import partial
from tqdm import tqdm

# Define the fuzzy matching function at module level so it can be pickled.
def get_rating_info(book_title, ratings_titles, df_ratings):
    # Attempt to find the best fuzzy match in the ratings dataset titles.
    best_match = process.extractOne(book_title, ratings_titles)
    if best_match is None:
        return [None, None]
    
    match_title, score = best_match
    threshold = 90  # Adjust threshold if necessary.
    if score >= threshold:
        # Get matching row(s) from the ratings dataset.
        match_rows = df_ratings[df_ratings['title_norm'] == match_title]
        if not match_rows.empty:
            avg_rating = match_rows.iloc[0]['average_rating']
            ratings_count = match_rows.iloc[0]['ratings_count']
            return [avg_rating, ratings_count]
    return [None, None]

if __name__ == '__main__':
    freeze_support()  # Needed for Windows

    # Load the datasets (adjust filenames as needed)
    df_books = pd.read_csv('src\\WIP\\BooksDataset100k.csv')
    df_ratings = pd.read_csv('src\\WIP\\Books_Data_Ratings.csv', on_bad_lines='skip')

    print("Initial number of records in BooksDataset100k:", len(df_books))
    print("Initial number of records in RatingsDataset:", len(df_ratings))

    # Preprocess titles for matching: convert to lowercase and strip spaces.
    df_books['book_title_norm'] = df_books['Title'].str.lower().str.strip()
    df_ratings['title_norm'] = df_ratings['title'].str.lower().str.strip()

    # Create a list of normalized titles from the ratings dataset for fuzzy matching.
    ratings_titles = df_ratings['title_norm'].tolist()

    # Use partial to pass extra parameters to get_rating_info
    func = partial(get_rating_info, ratings_titles=ratings_titles, df_ratings=df_ratings)

    # Use multiprocessing Pool.imap wrapped with tqdm to show a progress bar.
    book_titles = df_books['book_title_norm'].tolist()
    with Pool() as pool:
        results = list(tqdm(pool.imap(func, book_titles),
                            total=len(book_titles),
                            desc="Processing Books"))

    # Convert the results into a DataFrame and merge with the original DataFrame.
    results_df = pd.DataFrame(results, columns=['vote_average', 'vote_count'])
    df_books = pd.concat([df_books, results_df], axis=1)

    # Combine the 'Publish Date (Year)' and 'Publish Date (Month)' columns into a single 'release_date' column.
    df_books['release_date'] = (
        df_books['Publish Date (Year)'].astype(str) + '-' +
        df_books['Publish Date (Month)'].astype(str).str.zfill(2)
    )

    # Create the final DataFrame with the required columns.
    final_df = df_books[['Title', 'Authors', 'Category', 'Description', 
                          'vote_average', 'vote_count', 'release_date']].copy()

    # Rename columns to match the final schema.
    final_df.rename(columns={
        'Title': 'title',
        'Authors': 'author',
        'Category': 'genres',
        'Description': 'plot'
    }, inplace=True)

    # Check for null values in the final DataFrame.
    print("\nNull values in each column before cleaning:")
    print(final_df.isnull().sum())

    # Drop rows that have any null values so that the final CSV is clean.
    final_df.dropna(inplace=True)
    print("\nNumber of records after cleaning (dropping nulls):", len(final_df))

    # Save the final merged and cleaned dataset to a CSV file.
    final_df.to_csv('final_books_dataset.csv', index=False)
    print("\nFinal CSV created with {} records.".format(len(final_df)))
