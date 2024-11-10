import pandas as pd  # For data manipulation and analysis
import re  # For regular expressions used in text processing
import ast  # For safely evaluating strings containing Python literals
import numpy as np  # For numerical operations
from nltk.corpus import stopwords  # For removing common stop words in text data
from nltk.stem import PorterStemmer  # For stemming words to their root form
from sklearn.feature_extraction.text import TfidfVectorizer  # For converting text to TF-IDF features
from sklearn.metrics.pairwise import cosine_similarity  # For computing cosine similarity between vectors
from sklearn.model_selection import train_test_split  # For splitting data into training and testing sets
from sklearn.metrics import (
    mean_squared_error,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
)  # For evaluating the performance of the model

# Ensure that NLTK stopwords are downloaded
import nltk
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))


"""
Function: load_datasets()
-------------------------
Loads the books and movies datasets from CSV files, adds a 'content_type' column to distinguish between books and movies, and combines them into a single DataFrame.

Returns:
    df_combined (DataFrame): The combined DataFrame containing both books and movies data.
"""
def load_datasets():
    df_books = pd.read_csv('src/datasets/books_rs/books.csv')
    df_movies = pd.read_csv('src/datasets/books_rs/movies.csv')
    
    df_books['content_type'] = 'book'
    df_movies['content_type'] = 'movie'
    
    # Combine books and movies into one DataFrame
    df_combined = pd.concat([df_books, df_movies], ignore_index=True)
    
    # Keep only the necessary columns
    df_combined = df_combined[['Title', 'Author', 'Plot', 'Genres', 'Vote Average', 'content_type']]
    
    return df_combined

"""
Function: process_categories(categories_str)
--------------------------------------------
Processes the 'Genres' or 'Categories' column by converting the string representation of a list into an actual list of categories.

Parameters:
    categories_str (str): The string representation of categories or genres.

Returns:
    list: A list of processed category strings.
"""
def process_categories(categories_str):
    if pd.isnull(categories_str):
        return []
    try:
        # Safely evaluate the string to a Python literal (e.g., list)
        categories = ast.literal_eval(categories_str)
        if isinstance(categories, list):
            return [str(cat).strip().lower() for cat in categories]
    except (ValueError, SyntaxError):
        pass
    # Fallback: split the string by common delimiters
    return [cat.strip().lower() for cat in re.split(r'[;,]', categories_str)]

"""
Function: preprocess_text(text, stop_words, stemmer, word_pattern)
------------------------------------------------------------------
Preprocesses the input text by converting it to lowercase, removing stop words, stemming, and joining back into a string.

Parameters:
    text (str): The text to preprocess.
    stop_words (set): A set of stop words to remove.
    stemmer (PorterStemmer): An instance of PorterStemmer for word stemming.
    word_pattern (Pattern): A compiled regex pattern to match words.

Returns:
    str: The preprocessed text.
"""
def preprocess_text(text, stop_words, stemmer, word_pattern):
    # Find all words in the text
    words = word_pattern.findall(text.lower())
    # Stem words and remove stop words
    words = [stemmer.stem(word) for word in words if word not in stop_words]
    return ' '.join(words)

"""
Function: preprocess_content_data(df_combined, stop_words, stemmer, word_pattern)
---------------------------------------------------------------------------------
Preprocesses the combined DataFrame by generating tags, processing categories, and creating combined features for model training.

Parameters:
    df_combined (DataFrame): The combined DataFrame of books and movies.
    stop_words (set): A set of stop words to remove.
    stemmer (PorterStemmer): An instance of PorterStemmer for word stemming.
    word_pattern (Pattern): A compiled regex pattern to match words.

Returns:
    df_combined (DataFrame): The updated DataFrame with preprocessed text features.
"""
def preprocess_content_data(df_combined, stop_words, stemmer, word_pattern):
    # Process 'Genres' or 'Categories' into a list of categories
    df_combined['categories_list'] = df_combined['Genres'].apply(process_categories)
    # Generate tags by combining 'Author', 'Plot', and 'content_type'
    df_combined['tags'] = df_combined[['Author', 'Plot', 'content_type']].fillna('').agg(' '.join, axis=1)
    # Preprocess the 'tags' text
    df_combined['tags'] = df_combined['tags'].apply(lambda x: preprocess_text(x, stop_words, stemmer, word_pattern))
    # Preprocess the 'categories_list' text
    df_combined['categories_list'] = df_combined['categories_list'].apply(lambda x: ' '.join(preprocess_text(' '.join(x), stop_words, stemmer, word_pattern)))
    # Combine 'tags' and 'categories_list' into a single feature
    df_combined['combined_tags'] = df_combined['tags'] + ' ' + df_combined['categories_list']
    return df_combined

"""
Function: split_train_test(df_combined)
---------------------------------------
Splits the combined DataFrame into training and testing sets.

Parameters:
    df_combined (DataFrame): The preprocessed combined DataFrame.

Returns:
    X_train (DataFrame): Training set.
    X_test (DataFrame): Testing set.
"""
def split_train_test(df_combined):
    # Split the data into training and testing sets
    return train_test_split(df_combined, test_size=0.2, random_state=42)

"""
Function: compute_similarity(df_combined, X_train, X_test)
---------------------------------------------------------
Computes the cosine similarity between the TF-IDF vectors of the test set and the training set.

Parameters:
    df_combined (DataFrame): The combined DataFrame.
    X_train (DataFrame): Training set.
    X_test (DataFrame): Testing set.

Returns:
    cosine_sim_test_train (ndarray): Cosine similarity matrix between test and train TF-IDF vectors.
    tfidf_matrix (sparse matrix): The full TF-IDF matrix for all combined data.
"""
def compute_similarity(df_combined, X_train, X_test):
    # Initialize the TF-IDF Vectorizer
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3))
    # Fit and transform the 'combined_tags' to create the TF-IDF matrix
    tfidf_matrix = tf.fit_transform(df_combined['combined_tags'])
    # Extract the TF-IDF vectors for training and testing sets
    train_tfidf_matrix = tfidf_matrix[X_train.index]
    test_tfidf_matrix = tfidf_matrix[X_test.index]
    # Compute cosine similarity between test and train TF-IDF vectors
    cosine_sim_test_train = cosine_similarity(test_tfidf_matrix, train_tfidf_matrix)
    return cosine_sim_test_train, tfidf_matrix

"""
Function: predict_ratings(cosine_sim_test_train, X_train, X_test, k=10)
-----------------------------------------------------------------------
Predicts the ratings for the test set based on the similarity to the training set.

Parameters:
    cosine_sim_test_train (ndarray): Cosine similarity matrix between test and train TF-IDF vectors.
    X_train (DataFrame): Training set.
    X_test (DataFrame): Testing set.
    k (int): The number of top similar items to consider for prediction.

Returns:
    actual_ratings (ndarray): The actual ratings from the test set.
    predicted_ratings (ndarray): The predicted ratings based on similarity.
"""
def predict_ratings(cosine_sim_test_train, X_train, X_test, k=10):
    # Get the actual ratings from the training set
    train_ratings = X_train['Vote Average'].values
    # Sort in descending order and select the top-k indices
    top_k_indices = np.argsort(-cosine_sim_test_train, axis=1)[:, :k]
    # Get the similarities and ratings of top-k items
    top_k_similarities = np.take_along_axis(cosine_sim_test_train, top_k_indices, axis=1)
    top_k_ratings = train_ratings[top_k_indices]
    # Compute the weighted average of the top-k ratings
    numerators = np.sum(top_k_similarities * top_k_ratings, axis=1)
    denominators = np.sum(top_k_similarities, axis=1)
    predicted_ratings = np.divide(numerators, denominators, out=np.zeros_like(numerators), where=denominators != 0)
    # Handle cases where denominators are zero by taking the mean of top-k ratings
    mean_top_k_ratings = np.mean(top_k_ratings, axis=1)
    predicted_ratings = np.where(denominators != 0, predicted_ratings, mean_top_k_ratings)
    # Get the actual ratings from the test set
    actual_ratings = X_test['Vote Average'].values
    # Filter out any NaN values in the actual ratings
    valid_indices = ~np.isnan(actual_ratings)
    return actual_ratings[valid_indices], predicted_ratings[valid_indices]

"""
Function: evaluate_model(actual_ratings, predicted_ratings, threshold=5)
------------------------------------------------------------------------
Evaluates the performance of the model using various metrics like accuracy, precision, recall, F1 score, MSE, and RMSE.

Parameters:
    actual_ratings (ndarray): The actual ratings from the test set.
    predicted_ratings (ndarray): The predicted ratings.
    threshold (float): The threshold to convert ratings into binary classes for classification metrics.

Returns:
    Tuple containing accuracy, precision, F1 score, recall, MSE, and RMSE.
"""
def evaluate_model(actual_ratings, predicted_ratings, threshold=5):
    # Convert ratings to binary classes based on the threshold
    actual_binary = (actual_ratings > threshold).astype(int)
    predicted_binary = (predicted_ratings > threshold).astype(int)
    # Calculate evaluation metrics
    precision = precision_score(actual_binary, predicted_binary)
    recall = recall_score(actual_binary, predicted_binary)
    f1 = f1_score(actual_binary, predicted_binary)
    accuracy = accuracy_score(actual_binary, predicted_binary)
    mse = mean_squared_error(actual_ratings, predicted_ratings)
    rmse = np.sqrt(mse)
    return accuracy, precision, f1, recall, mse, rmse

"""
Function: get_recommendations(content_title, df_combined, tfidf_matrix, k=10)
------------------------------------------------------------------------------
Generates a list of top-k recommendations similar to the given content title.

Parameters:
    content_title (str): The title of the content for which to find recommendations.
    df_combined (DataFrame): The combined DataFrame of books and movies.
    tfidf_matrix (sparse matrix): The full TF-IDF matrix for all combined data.
    k (int): The number of recommendations to return.

Returns:
    list: A list of recommended content titles.
"""
def get_recommendations(content_title, df_combined, tfidf_matrix, k=10):
    try:
        # Find the index of the content with the given title
        content_index = df_combined[df_combined['Title'] == content_title].index[0]
    except IndexError:
        print(f"Content titled '{content_title}' not found.")
        return []
    # Compute cosine similarity between the content and all others
    sim_scores = cosine_similarity(tfidf_matrix[content_index], tfidf_matrix).flatten()
    # Get indices of contents sorted by similarity scores
    sim_scores_indices = np.argsort(-sim_scores)
    # Exclude the content itself and get top-k recommendations
    top_indices = sim_scores_indices[sim_scores_indices != content_index][:k]
    recommended_titles = df_combined.iloc[top_indices]['Title'].tolist()
    return recommended_titles

"""
Function: print_content_type(titles, df_combined)
-------------------------------------------------
Prints the content type (book or movie) for each title in the list.

Parameters:
    titles (list): A list of content titles.
    df_combined (DataFrame): The combined DataFrame of books and movies.
"""
def print_content_type(titles, df_combined):
    for title in titles:
        # Retrieve the row corresponding to the title
        content_type_row = df_combined[df_combined['Title'] == title]
        if not content_type_row.empty:
            content_type = content_type_row['content_type'].values[0]
            print(f"{title} ({content_type.capitalize()})")
        else:
            print(f"{title} (Content Type Not Found)")

"""
Function: run_recommendation_and_evaluate(content_title, df_combined, tfidf_matrix, X_train, X_test, cosine_sim_test_train)
---------------------------------------------------------------------------------------------------------------------------
Runs the recommendation system for a given content title and evaluates the model's performance.

Parameters:
    content_title (str): The title of the content for which to find recommendations.
    df_combined (DataFrame): The combined DataFrame of books and movies.
    tfidf_matrix (sparse matrix): The full TF-IDF matrix for all combined data.
    X_train (DataFrame): Training set.
    X_test (DataFrame): Testing set.
    cosine_sim_test_train (ndarray): Cosine similarity matrix between test and train TF-IDF vectors.

Returns:
    list: A list containing evaluation metrics.
"""
def run_recommendation_and_evaluate(content_title, df_combined, tfidf_matrix, X_train, X_test, cosine_sim_test_train):
    # Get recommendations for the given content title
    recommendations = get_recommendations(content_title, df_combined, tfidf_matrix)
    # Predict ratings based on similarity
    actual_ratings, predicted_ratings = predict_ratings(cosine_sim_test_train, X_train, X_test)
    # Evaluate the model's performance
    accuracy, precision, f1, recall, mse, rmse = evaluate_model(actual_ratings, predicted_ratings)
    return [accuracy, precision, f1, recall, mse, rmse]

def initialize_recommender():
    df_combined = load_datasets()
    # Initialize stemmer, and word pattern for text preprocessing
    stemmer = PorterStemmer()
    word_pattern = re.compile(r'\b\w+\b')
    df_combined = preprocess_content_data(df_combined, stop_words, stemmer, word_pattern)
    tfidf_vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3))
    tfidf_matrix = tfidf_vectorizer.fit_transform(df_combined['combined_tags'])
    return df_combined, tfidf_matrix


# Main execution block
if __name__ == "__main__":
    # Load the combined dataset
    df_combined = load_datasets()
    
    # Initialize stemmer, and word pattern for text preprocessing
    stemmer = PorterStemmer()
    word_pattern = re.compile(r'\b\w+\b')
    
    # Preprocess the content data
    df_combined = preprocess_content_data(df_combined, stop_words, stemmer, word_pattern)
    
    # Split the data into training and testing sets
    X_train, X_test = split_train_test(df_combined)
    
    # Compute cosine similarity between test and train sets
    cosine_sim_test_train, tfidf_matrix = compute_similarity(df_combined, X_train, X_test)
    
    # Example content title for which to get recommendations
    content_title = "Despicable Me 4"
    
    # Run recommendation and evaluate the model
    evaluation_metrics = run_recommendation_and_evaluate(content_title, df_combined, tfidf_matrix, X_train, X_test, cosine_sim_test_train)
    
    # Print evaluation metrics
    print(f"Evaluation Metrics: {evaluation_metrics}")
    
    # Get and print recommendations
    recommendations = get_recommendations(content_title, df_combined, tfidf_matrix, k=10)
    print_content_type(recommendations, df_combined)
    
    # Unpack evaluation metrics for printing
    accuracy, precision, f1, recall, mse, rmse = evaluation_metrics
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"Root Mean Squared Error: {rmse:.4f}")
