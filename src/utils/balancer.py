from utils.recommendator import get_recommendations, initialize_recommender

def balance_recommendations(recommendations, df_combined, min_recommendations):
    # Create a dictionary to map titles to their types
    title_to_type = df_combined.set_index('Title')['content_type'].to_dict()
    
    # Add type information to recommendations
    recommendations_with_type = [
        {'title': rec, 'type': title_to_type.get(rec, 'unknown')}
        for rec in recommendations
    ]
    
    books = [rec for rec in recommendations_with_type if rec['type'] == 'book']
    movies = [rec for rec in recommendations_with_type if rec['type'] == 'movie']
    
    min_length = min(len(books), len(movies), min_recommendations)
    
    balanced_recommendations = books[:min_length] + movies[:min_length]
    return [rec['title'] for rec in balanced_recommendations]

def get_balanced_recommendations(content_title, min_recommendations):
    # Initialize recommender data
    df_combined, tfidf_matrix = initialize_recommender()
    recommendations = get_recommendations(content_title, df_combined, tfidf_matrix, min_recommendations*20)
    return balance_recommendations(recommendations, df_combined, min_recommendations)
