import pandas as pd
import re
import numpy as np
import logging
import os
import pickle

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, precision_score, recall_score, f1_score, accuracy_score

from sentence_transformers import SentenceTransformer

# Ensure NLTK data is downloaded
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = 'cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def load_datasets():
    # Load and combine books and movies data
    df_books = pd.read_csv('src/datasets/books_rs/books.csv')
    df_movies = pd.read_csv('src/datasets/books_rs/movies.csv')
    df_books['Type'] = 'book'
    df_movies['Type'] = 'movie'
    df_combined = pd.concat([df_books, df_movies], ignore_index=True)
    df_combined = df_combined[['Title', 'Author', 'Plot', 'Genres', 'Vote Average', 'Type']]
    return df_combined

def get_wordnet_pos(word):
    # Map POS tag to first character lemmatize() accepts
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {'J': wordnet.ADJ, 'N': wordnet.NOUN,
                'V': wordnet.VERB, 'R': wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

def preprocess_text(text, stop_words, lemmatizer, word_pattern):
    # Lowercase, tokenize, remove stopwords, lemmatize
    words = word_pattern.findall(text.lower())
    words = [w for w in words if w not in stop_words]
    words = [lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in words]
    return ' '.join(words)

def preprocess_content_data(df_combined, stop_words, lemmatizer, word_pattern):
    # Create and preprocess 'tags' from multiple fields
    df_combined['tags'] = df_combined[['Author', 'Plot', 'Type', 'Genres']].fillna('').agg(' '.join, axis=1)
    df_combined['tags'] = df_combined['tags'].apply(lambda x: preprocess_text(x, stop_words, lemmatizer, word_pattern))
    return df_combined

def compute_similarity(X_train, X_test, embeddings):
    # Compute cosine similarity using embeddings
    train_emb = embeddings[X_train.index]
    test_emb = embeddings[X_test.index]
    cosine_sim = cosine_similarity(test_emb, train_emb)
    return cosine_sim

def predict_ratings(cosine_sim, X_train, X_test, k=10):
    # Predict test ratings from top-k similar items in train
    train_ratings = X_train['Vote Average'].values
    top_k_idx = np.argsort(-cosine_sim, axis=1)[:, :k]
    top_k_sim = np.take_along_axis(cosine_sim, top_k_idx, axis=1)
    top_k_rat = train_ratings[top_k_idx]
    sums = np.sum(top_k_sim, axis=1)
    weighted_avg = np.where(
        sums == 0,
        np.mean(top_k_rat, axis=1),  # fallback to average if no similarity
        np.sum(top_k_sim * top_k_rat, axis=1) / sums
    )
    actual = X_test['Vote Average'].values
    valid = ~np.isnan(actual)
    return actual[valid], weighted_avg[valid]

def evaluate_classification(actual, predicted, threshold=5):
    # Convert ratings to binary and compute classification metrics
    a_bin = (actual > threshold).astype(int)
    p_bin = (predicted > threshold).astype(int)
    return (accuracy_score(a_bin, p_bin),
            precision_score(a_bin, p_bin, zero_division=0),
            recall_score(a_bin, p_bin, zero_division=0),
            f1_score(a_bin, p_bin, zero_division=0))

def evaluate_regression(actual, predicted):
    # Compute MSE and RMSE
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    return mse, rmse

def evaluate_model(actual, predicted, threshold=5):
    # Evaluate both classification and regression performance
    acc, prec, recall, f1 = evaluate_classification(actual, predicted, threshold)
    mse, rmse = evaluate_regression(actual, predicted)
    return acc, prec, recall, f1, mse, rmse

def get_recommendations(content_title, df_combined, embeddings, k=10):
    # Recommend top-k similar items
    try:
        idx = df_combined[df_combined['Title'] == content_title].index[0]
    except IndexError:
        logger.warning(f"'{content_title}' not found.")
        return []
    scores = cosine_similarity(embeddings[idx].reshape(1, -1), embeddings).flatten()
    sorted_idx = np.argsort(-scores)
    top_idx = sorted_idx[sorted_idx != idx][:k]
    return df_combined.iloc[top_idx][['Title', 'Type']].to_dict(orient='records')

def run_recommendation_and_evaluate(content_title, df_combined, embeddings, X_train, X_test, cosine_sim, threshold=5):
    # Get recommendations, predict ratings, evaluate performance
    recs = get_recommendations(content_title, df_combined, embeddings)
    for r in recs:
        logger.info(f"{r['Title']} ({r['Type'].capitalize()})")
    actual, predicted = predict_ratings(cosine_sim, X_train, X_test)
    acc, prec, recall, f1, mse, rmse = evaluate_model(actual, predicted, threshold)
    logger.info("Evaluation Metrics:")
    logger.info(f"  Accuracy: {acc:.4f}")
    logger.info(f"  Precision: {prec:.4f}")
    logger.info(f"  Recall: {recall:.4f}")
    logger.info(f"  F1 Score: {f1:.4f}")
    logger.info(f"  Mean Squared Error: {mse:.4f}")
    logger.info(f"  Root Mean Squared Error: {rmse:.4f}")
    return [acc, prec, recall, f1, mse, rmse]

def initialize_recommender():
    """
    Initialize datasets, preprocess, and prepare embeddings from BERT model.
    Use caching to load from disk if available.
    """
    df_cache_path = os.path.join(CACHE_DIR, 'df_preprocessed.pkl')
    emb_cache_path = os.path.join(CACHE_DIR, 'embeddings.npy')

    if os.path.exists(df_cache_path) and os.path.exists(emb_cache_path):
        # Load cached data
        logger.info("Loading preprocessed DataFrame and embeddings from cache.")
        with open(df_cache_path, 'rb') as f:
            df = pickle.load(f)
        embeddings = np.load(emb_cache_path)
    else:
        # Compute and save
        logger.info("Cache not found. Loading and preprocessing data.")
        df = load_datasets()
        lemmatizer = WordNetLemmatizer()
        pattern = re.compile(r'\b\w+\b')
        df = preprocess_content_data(df, stop_words, lemmatizer, pattern)

        logger.info("Generating embeddings with SentenceTransformer.")
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Modify model if desired
        embeddings = model.encode(df['tags'].tolist(), show_progress_bar=True)

        # Save to cache
        with open(df_cache_path, 'wb') as f:
            pickle.dump(df, f)
        np.save(emb_cache_path, embeddings)

    return df, embeddings

def balance_recommendations(recommendations, min_recommendations):
    # Separate recommendations into books and movies
    books = [rec for rec in recommendations if rec.get('Type') == 'book']
    movies = [rec for rec in recommendations if rec.get('Type') == 'movie']
    
    # Determine the balanced minimum length
    min_length = min(len(books), len(movies), min_recommendations)
    
    # Combine an equal number of books and movies
    balanced_recommendations = books[:min_length] + movies[:min_length]
    return [rec['Title'] for rec in balanced_recommendations]

def get_balanced_recommendations(content_title, min_recommendations, df, embeddings):
    # Get recommendations as a list of dictionaries
    recommendations = get_recommendations(content_title, df, embeddings, min_recommendations * 200)
    
    # Balance the recommendations
    return balance_recommendations(recommendations, min_recommendations)

if __name__ == "__main__":
    df_combined, embeddings = initialize_recommender()
    X_train, X_test = train_test_split(df_combined, test_size=0.2, random_state=42)
    cosine_sim_test_train = compute_similarity(X_train, X_test, embeddings)
    content_title = "Despicable Me 4"
    run_recommendation_and_evaluate(content_title, df_combined, embeddings, X_train, X_test, cosine_sim_test_train, threshold=5)
