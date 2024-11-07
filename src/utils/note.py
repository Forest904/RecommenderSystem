#Useful libraries
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

#Importing datasets
#Books
books_file = 'C:/Users/lucap/Documents/Repositories/VSC/RecommenderSystem/src/datasets/books_rs/books.csv'
df_books = pd.read_csv(books_file)

#Movies
movies_file = 'C:/Users/lucap/Documents/Repositories/VSC/RecommenderSystem/src/datasets/books_rs/movies.csv'
df_movies = pd.read_csv(movies_file)

#Add a column to identify the type of content
df_books['content_type'] = 'book' 
df_movies['content_type'] = 'movie'

#Save separated ratings and content dataframes for books and movies
df_books_ratings = df_books[['Title', 'Vote Count', 'Vote Average']]
df_books_content = df_books.drop(['Vote Count', 'Vote Average'], axis=1, errors='ignore')

df_movies_ratings = df_movies[['Title', 'Vote Count', 'Vote Average']]
df_movies_content = df_movies.drop(['Vote Count', 'Vote Average'], axis=1, errors='ignore')

cross_content = pd.concat([df_books_content, df_movies_content], ignore_index=True)
cross_rating = pd.concat([df_books_ratings, df_movies_ratings], ignore_index=True)
#print("df_books_content dimensions:", df_books_content.shape)
#print("df_movies_content dimensions:", df_movies_content.shape)
#print("cross_content dimensions:", cross_content.shape)

title_type_df = cross_content[['Title', 'content_type']]

# Process 'categories' field into a list before creating 'tags'
def process_categories(categories_str):
    if pd.isnull(categories_str):
        return []
    
    # Check if the input is a string and parse it if needed
    if isinstance(categories_str, str):
        if categories_str.startswith('[') and categories_str.endswith(']'):
            import ast
            try:
                categories = ast.literal_eval(categories_str)
                if isinstance(categories, list):
                    return [str(cat).strip().lower() for cat in categories]
            except (ValueError, SyntaxError):
                pass
        # Use regex to split strings by common delimiters
        return [cat.strip().lower() for cat in re.split(r'[;,]', categories_str)]
    
    # If already a list, flatten it in one step
    if isinstance(categories_str, list):
        return [str(item).strip().lower() for sublist in categories_str for item in (sublist if isinstance(sublist, list) else [sublist])]
    
    return []

# Apply the optimized function
cross_content['categories_list'] = cross_content['Genres'].map(process_categories)


# Function to flatten any nested lists in 'categories_list'
# Use a single list comprehension to flatten categories
def flatten_categories(categories):
    return [str(item) for sublist in categories for item in (sublist if isinstance(sublist, list) else [sublist])]

# Apply the optimized function
cross_content['categories_list'] = cross_content['categories_list'].map(flatten_categories)

# Now create 'tags' column without dropping 'categories_list'
cross_content['tags'] = cross_content[['Author', 'Plot', 'content_type']].fillna('').agg('; '.join, axis=1)

# Download stop words if running for the first time!!!
#nltk.download('stopwords')

def preprocess_text(text):
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # 3. Remove stop words
    stop_words = set(stopwords.words('english'))
    words = text.split()
    words = [word for word in words if word not in stop_words]
    
    # 4. Stemming
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    
    # Join words back to a single string
    return ' '.join(words)

# Preprocess 'tags' and 'categories_list'
cross_content['tags'] = cross_content['tags'].apply(preprocess_text)
cross_content['categories_list'] = cross_content['categories_list'].apply(lambda x: [preprocess_text(cat) for cat in x])

# Vectorized combination of 'tags' and 'categories_list'
cross_content['combined_tags'] = (
    cross_content['tags'] + ' ' + cross_content['categories_list'].map(' '.join)
)

# Merge 'average_rating' into 'cross_content' for prediction
cross_content = cross_content.merge(cross_rating[['Title', 'Vote Average']], on='Title', how='left')

# Split the dataset into training and testing sets
X_cross_train, X_cross_test = train_test_split(cross_content, test_size=0.2, random_state=42)
train_indices = X_cross_train.index
test_indices = X_cross_test.index

tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0.0)
tfidf_matrix = tf.fit_transform(cross_content['tags'])

# Get TF-IDF vectors for training and test sets
train_tfidf_matrix = tfidf_matrix[train_indices]
test_tfidf_matrix = tfidf_matrix[test_indices]

cosine_sim_test_train = cosine_similarity(test_tfidf_matrix, train_tfidf_matrix)

# Convert indices to numpy arrays for indexing
train_indices_array = train_indices.to_numpy()
test_indices_array = test_indices.to_numpy()

k = 10  # Number of similar contents to recommend

# Initialize counters
total_TP = 0
total_FP = 0
total_FN = 0
total_TN = 0

# Initialize lists to store actual and predicted ratings
actual_ratings = []
predicted_ratings = []

num_train_items = len(train_indices)
num_test_items = len(test_indices)

# Note: Total TN is typically not used in recommender systems due to the vast number of non-relevant items

for i, test_idx in enumerate(test_indices_array):
    # Get the test item
    test_item = cross_content.loc[test_idx]
    test_title = test_item['Title']
    test_actual_rating = test_item['Vote Average']
    test_categories = set(flatten_categories(test_item['categories_list']))

    # Skip items with no categories or missing ratings
    if not test_categories or pd.isnull(test_actual_rating):
        continue

    # Get the similarity scores to training items
    sim_scores = cosine_sim_test_train[i]

    # Get the top k indices in training set
    sim_scores_indices = sim_scores.argsort()[::-1]
    top_k_indices_in_train = sim_scores_indices[:k]
    top_k_train_indices = train_indices_array[top_k_indices_in_train]

    # Get similarities and ratings of the top k items
    top_k_similarities = sim_scores[top_k_indices_in_train]
    top_k_ratings = cross_content.loc[top_k_train_indices]['Vote Average'].values

    # Handle the case where similarities sum to zero
    if top_k_similarities.sum() == 0:
        predicted_rating = top_k_ratings.mean()
    else:
        # Weighted average of ratings
        predicted_rating = (top_k_similarities @ top_k_ratings) / top_k_similarities.sum()

    # Append to lists
    actual_ratings.append(test_actual_rating)
    predicted_ratings.append(predicted_rating)

    # For evaluation metrics based on categories
    # Get recommended items and their categories
    recommended_items = cross_content.loc[top_k_train_indices]
    recommended_categories = recommended_items['categories_list'].tolist()
    recommended_categories_flat = [set(flatten_categories(cats)) for cats in recommended_categories]

threshold = 5
actual_binary = [1 if rating > threshold else 0 for rating in actual_ratings]
predicted_binary = [1 if rating > threshold else 0 for rating in predicted_ratings]

# Compute metrics
precision = precision_score(actual_binary, predicted_binary)
recall = recall_score(actual_binary, predicted_binary)
f1 = f1_score(actual_binary, predicted_binary)
accuracy = accuracy_score(actual_binary, predicted_binary)

# Compute Mean Squared Error
mse = mean_squared_error(actual_ratings, predicted_ratings)
# Compute Root Mean Squared Error
rmse = mse ** 0.5

# Function to get recommendations for a content title
def get_recommendations(content_title, k):
    # Get the index of the content with the given title
    try:
        content_index = cross_content[cross_content['Title'] == content_title].index[0]
    except IndexError:
        print(f"Content titled '{content_title}' not found.")
        return []

    # Get the similarity scores for the content_index
    # Compute cosine similarity between the content and all contents
    sim_scores = cosine_similarity(tfidf_matrix[content_index], tfidf_matrix).flatten()

    # Sort the similarity scores in descending order
    sim_scores_indices = sim_scores.argsort()[::-1]

    # Get the indices of the top k+1 similar contents (excluding the content itself)
    top_indices = [i for i in sim_scores_indices if i != content_index][:k]

    # Get the titles of the recommended contents
    recommended_titles = cross_content.iloc[top_indices]['Title'].tolist()

    return recommended_titles


content_title = "The Avengers"
recommendations = get_recommendations(content_title, k)

def print_content_type(titles):
    for title in titles:
        content_type_row = title_type_df[title_type_df['Title'] == title]
        if not content_type_row.empty:
            content_type = content_type_row['content_type'].values[0]
            if content_type == 'book':
                print(f"{title} (Book)")
            elif content_type == 'movie':
                print(f"{title} (Movie)")
            else:
                print(f"{title} (Unknown Content Type)")
        else:
            print(f"{title} (Content Type Not Found)")


sorted_recommendations = cross_rating[cross_rating['Title'].isin(recommendations)].sort_values(['Vote Average', 'Vote Count'], ascending=[False, False])['Title'].tolist()
print_content_type(sorted_recommendations)

#Valuation of the recommender system
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"F1 Score: {f1:.4f}")
print(f"Recall: {recall:.4f}")
print(f"Mean Squared Error: {mse:.4f}")
print(f"Root Mean Squared Error: {rmse:.4f}")

