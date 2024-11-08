import pandas as pd
import re
import ast
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
)

# Load datasets
df_books = pd.read_csv('src/datasets/books_rs/books.csv')
df_movies = pd.read_csv('src/datasets/books_rs/movies.csv')



# Add content_type
df_books['content_type'] = 'book'
df_movies['content_type'] = 'movie'

# Separate ratings and content dataframes
rating_cols = ['Title', 'Vote Count', 'Vote Average']
df_books_ratings = df_books[rating_cols]
df_movies_ratings = df_movies[rating_cols]
df_books_content = df_books.drop(['Vote Count', 'Vote Average'], axis=1)
df_movies_content = df_movies.drop(['Vote Count', 'Vote Average'], axis=1)

# Combine content and ratings dataframes
cross_content = pd.concat([df_books_content, df_movies_content], ignore_index=True)
cross_rating = pd.concat([df_books_ratings, df_movies_ratings], ignore_index=True)

title_type_df = cross_content[['Title', 'content_type']]

# Process 'Genres' into 'categories_list'
def process_categories(categories_str):
    if pd.isnull(categories_str):
        return []
    try:
        # Try to parse the string as a list
        categories = ast.literal_eval(categories_str)
        if isinstance(categories, list):
            return [str(cat).strip().lower() for cat in categories]
    except (ValueError, SyntaxError):
        pass
    # Split by common delimiters if not a list
    return [cat.strip().lower() for cat in re.split(r'[;,]', categories_str)]

cross_content['categories_list'] = cross_content['Genres'].apply(process_categories)

# Initialize stop words and stemmer once
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
word_pattern = re.compile(r'\b\w+\b')

def preprocess_text(text):
    # Lowercase and extract words
    words = word_pattern.findall(text.lower())
    # Remove stop words and stem
    words = [stemmer.stem(word) for word in words if word not in stop_words]
    return ' '.join(words)

# Preprocess 'tags' and 'categories_list'
cross_content['tags'] = cross_content[['Author', 'Plot', 'content_type']].fillna('').agg(' '.join, axis=1)
cross_content['tags'] = cross_content['tags'].apply(preprocess_text)
cross_content['categories_list'] = cross_content['categories_list'].apply(
    lambda x: ' '.join(preprocess_text(' '.join(x)))
)

# Combine 'tags' and 'categories_list' into 'combined_tags'
cross_content['combined_tags'] = cross_content['tags'] + ' ' + cross_content['categories_list']

# Merge 'Vote Average' into 'cross_content'
cross_content = cross_content.merge(cross_rating[['Title', 'Vote Average']], on='Title', how='left')

# Split the dataset into training and testing sets
X_cross_train, X_cross_test = train_test_split(cross_content, test_size=0.2, random_state=42)

# Create TF-IDF matrix on 'combined_tags'
tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3))
tfidf_matrix = tf.fit_transform(cross_content['combined_tags'])

# Get TF-IDF vectors for training and test sets
train_tfidf_matrix = tfidf_matrix[X_cross_train.index]
test_tfidf_matrix = tfidf_matrix[X_cross_test.index]

# Compute cosine similarity between test and train sets
cosine_sim_test_train = cosine_similarity(test_tfidf_matrix, train_tfidf_matrix)

# Get the ratings from the training set
train_ratings = X_cross_train['Vote Average'].values

k = 10  # Number of similar contents to consider

# Get indices of top k similar train items for each test item
top_k_indices = np.argsort(-cosine_sim_test_train, axis=1)[:, :k]

# Get top k similarities and ratings
top_k_similarities = np.take_along_axis(cosine_sim_test_train, top_k_indices, axis=1)
top_k_ratings = train_ratings[top_k_indices]

# Compute predicted ratings
numerators = np.sum(top_k_similarities * top_k_ratings, axis=1)
denominators = np.sum(top_k_similarities, axis=1)

# Handle zero denominators
predicted_ratings = np.divide(numerators, denominators, out=np.zeros_like(numerators), where=denominators != 0)
# Replace zero denominators with mean of top_k_ratings
mean_top_k_ratings = np.mean(top_k_ratings, axis=1)
predicted_ratings = np.where(denominators != 0, predicted_ratings, mean_top_k_ratings)

# Get actual ratings
actual_ratings = X_cross_test['Vote Average'].values

# Exclude items where actual rating is NaN
valid_indices = ~np.isnan(actual_ratings)
actual_ratings = actual_ratings[valid_indices]
predicted_ratings = predicted_ratings[valid_indices]

# Compute evaluation metrics
threshold = 5
actual_binary = (actual_ratings > threshold).astype(int)
predicted_binary = (predicted_ratings > threshold).astype(int)

precision = precision_score(actual_binary, predicted_binary)
recall = recall_score(actual_binary, predicted_binary)
f1 = f1_score(actual_binary, predicted_binary)
accuracy = accuracy_score(actual_binary, predicted_binary)

mse = mean_squared_error(actual_ratings, predicted_ratings)
rmse = np.sqrt(mse)

# Function to get recommendations for a content title
def get_recommendations(content_title, k=10):
    try:
        content_index = cross_content[cross_content['Title'] == content_title].index[0]
    except IndexError:
        print(f"Content titled '{content_title}' not found.")
        return []
    sim_scores = cosine_similarity(tfidf_matrix[content_index], tfidf_matrix).flatten()
    sim_scores_indices = np.argsort(-sim_scores)
    # Exclude the content itself
    top_indices = sim_scores_indices[sim_scores_indices != content_index][:k]
    recommended_titles = cross_content.iloc[top_indices]['Title'].tolist()
    return recommended_titles

def print_content_type(titles):
    for title in titles:
        content_type_row = title_type_df[title_type_df['Title'] == title]
        if not content_type_row.empty:
            content_type = content_type_row['content_type'].values[0]
            print(f"{title} ({content_type.capitalize()})")
        else:
            print(f"{title} (Content Type Not Found)")

"""
content_title = "Despicable Me 4"
recommendations = get_recommendations(content_title, k)

# Sort recommendations by 'Vote Average' and 'Vote Count'
sorted_recommendations = cross_rating[cross_rating['Title'].isin(recommendations)] \
    .sort_values(['Vote Average', 'Vote Count'], ascending=[False, False])['Title'].tolist()

print_content_type(sorted_recommendations)

# Evaluation metrics
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"F1 Score: {f1:.4f}")
print(f"Recall: {recall:.4f}")
print(f"Mean Squared Error: {mse:.4f}")
print(f"Root Mean Squared Error: {rmse:.4f}")

"""