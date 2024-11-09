import random
import pandas as pd
import re  # For regular expressions used in text processing

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer  # For stemming words to their root form
from recommendator import run_recommendation_and_evaluate, preprocess_content_data, split_train_test, load_datasets, compute_similarity, stop_words

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

# Extract the titles
titles = df_combined['Title'].unique()

# Randomly select titles
num_titles = 100  # Number of titles to sample
sampled_titles = random.sample(list(titles), num_titles)

# Evaluate metrics for each title
metrics_list = []
for title in sampled_titles:
    metrics = run_recommendation_and_evaluate(title, df_combined, tfidf_matrix, X_train, X_test, cosine_sim_test_train)
    metrics_list.append(metrics)

# Calculate the average of metrics
average_metrics = pd.DataFrame(metrics_list).mean()
print("valuation metrics averages:")
print(f"Average Accuracy: {average_metrics[0]:.4f}")
print(f"Average Precision: {average_metrics[1]:.4f}")
print(f"Average F1 Score: {average_metrics[2]:.4f}")
print(f"Average Recall: {average_metrics[3]:.4f}")
print(f"Average Mean Squared Error: {average_metrics[4]:.4f}")
print(f"Average Root Mean Squared Error: {average_metrics[5]:.4f}")