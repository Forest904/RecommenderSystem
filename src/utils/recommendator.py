import pandas as pd
import re
import numpy as np
import logging

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, precision_score, recall_score, f1_score, accuracy_score

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
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def compute_similarity(df_combined, X_train, X_test, tfidf_vectorizer, tfidf_matrix):
    # Compute cosine similarity using provided tfidf_matrix
    train_tfidf = tfidf_matrix[X_train.index]
    test_tfidf = tfidf_matrix[X_test.index]
    cosine_sim = cosine_similarity(test_tfidf, train_tfidf)
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

def get_recommendations(content_title, df_combined, tfidf_matrix, k=10):
    # Recommend top-k similar items
    try:
        idx = df_combined[df_combined['Title'] == content_title].index[0]
    except IndexError:
        logger.warning(f"'{content_title}' not found.")
        return []
    scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    sorted_idx = np.argsort(-scores)
    top_idx = sorted_idx[sorted_idx != idx][:k]
    return df_combined.iloc[top_idx][['Title', 'Type']].to_dict(orient='records')

def run_recommendation_and_evaluate(content_title, df_combined, tfidf_matrix, X_train, X_test, cosine_sim, threshold=5):
    # Get recommendations, predict ratings, evaluate performance
    recs = get_recommendations(content_title, df_combined, tfidf_matrix)
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
    # Initialize datasets, preprocess, and prepare TF-IDF
    df = load_datasets()
    lemmatizer = WordNetLemmatizer()
    pattern = re.compile(r'\b\w+\b')
    df = preprocess_content_data(df, stop_words, lemmatizer, pattern)
    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3))
    tfidf_matrix = vectorizer.fit_transform(df['tags'])
    return df, tfidf_matrix, vectorizer

if __name__ == "__main__":
    df_combined, tfidf_matrix, tfidf_vectorizer = initialize_recommender()
    X_train, X_test = train_test_split(df_combined, test_size=0.2, random_state=42)
    cosine_sim_test_train = compute_similarity(df_combined, X_train, X_test, tfidf_vectorizer, tfidf_matrix)
    content_title = "Despicable Me 4"
    run_recommendation_and_evaluate(content_title, df_combined, tfidf_matrix, X_train, X_test, cosine_sim_test_train, threshold=5)
