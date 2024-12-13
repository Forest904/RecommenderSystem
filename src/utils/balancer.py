from utils.recommendator import get_recommendations, initialize_recommender

def balance_recommendations(recommendations, min_recommendations):
    # Separate recommendations into books and movies
    books = [rec for rec in recommendations if rec.get('Type') == 'book']
    movies = [rec for rec in recommendations if rec.get('Type') == 'movie']
    
    # Determine the balanced minimum length
    min_length = min(len(books), len(movies), min_recommendations)
    
    # Combine an equal number of books and movies
    balanced_recommendations = books[:min_length] + movies[:min_length]
    return [rec['Title'] for rec in balanced_recommendations]

def get_balanced_recommendations(content_title, min_recommendations):
    # Initialize recommender data
    df, tfidf_matrix, vectorizer = initialize_recommender()
    
    # Get recommendations as a list of dictionaries
    recommendations = get_recommendations(content_title, df, tfidf_matrix, min_recommendations * 200)
    
    # Balance the recommendations
    return balance_recommendations(recommendations, min_recommendations)

