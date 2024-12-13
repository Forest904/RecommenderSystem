import random
import pandas as pd
from recommendator import run_recommendation_and_evaluate, initialize_recommender, split_train_test, compute_similarity

# Initialize the recommender system
df, tfidf_matrix, vectorizer = initialize_recommender()

# Split the data into training and testing sets
X_train, X_test = split_train_test(df)

# Compute cosine similarity between test and train sets
cosine_sim_test_train, _ = compute_similarity(df, X_train, X_test)

# Extract the titles
titles = df['Title'].unique()

# Randomly select titles
num_titles = 100  # Number of titles to sample
sampled_titles = random.sample(list(titles), num_titles)

# Evaluate metrics for each title
metrics_list = []
for title in sampled_titles:
    metrics = run_recommendation_and_evaluate(title, df, tfidf_matrix, X_train, X_test, cosine_sim_test_train)
    metrics_list.append(metrics)

# Calculate the average of metrics
average_metrics = pd.DataFrame(metrics_list).mean()
print("Evaluation metrics averages:")
print(f"Average Accuracy: {average_metrics[0]:.4f}")
print(f"Average Precision: {average_metrics[1]:.4f}")
print(f"Average F1 Score: {average_metrics[2]:.4f}")
print(f"Average Recall: {average_metrics[3]:.4f}")
print(f"Average Mean Squared Error: {average_metrics[4]:.4f}")
print(f"Average Root Mean Squared Error: {average_metrics[5]:.4f}")
