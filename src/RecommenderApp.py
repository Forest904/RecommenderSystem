from flask import Flask, render_template, request
from utils.recommendator import initialize_recommender
from utils.contents_fetcher import get_movie_image_url, get_book_cover_url, get_genre, get_author, get_plot
from utils.balancer import get_balanced_recommendations
import pandas as pd

# Initialize recommender data
df_combined, tfidf_matrix = initialize_recommender()

#Number of recommendations to show per type
NUM_RECOMMENDATIONS = 6

class RecommenderApp:
    def __init__(self):
        self.app = Flask(__name__)

        # Define the index route
        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            if request.method == 'POST':
                content_title = request.form['title']
                recommendations = get_balanced_recommendations(content_title, NUM_RECOMMENDATIONS)
                
                if not recommendations:
                    error_message = f"Content titled '{content_title}' not found."
                    return render_template('index.html', error=error_message)
                
                # Get additional information about recommendations
                recommended_contents = df_combined[df_combined['Title'].isin(recommendations)]

                # Get image URLs based on content type
                def get_image_url(row):
                    if row['content_type'] == 'movie':
                        return get_movie_image_url(row['Title'])
                    elif row['content_type'] == 'book':
                        return get_book_cover_url(row['Title'])
                    else:
                        return None

                #Add a get author function for both books and movies
                def get_a(title):
                    return get_author(title, df_combined)

                #Add a get genre function for both books and movies
                def get_g(title):
                    return get_genre(title)
                
                #Add a get plot function for both books and movies
                def get_p(title):
                    return get_plot(title)

                recommended_contents = recommended_contents.copy()
                recommended_contents['image_url'] = recommended_contents.apply(get_image_url, axis=1)
                recommended_contents['author'] = recommended_contents['Title'].apply(get_a)
                recommended_contents['genre'] = recommended_contents['Title'].apply(get_g)
                recommended_contents['plot'] = recommended_contents['Title'].apply(get_p)
                
                # Convert DataFrame to a list of dictionaries for easy templating
                movies_list = recommended_contents[recommended_contents['content_type'] == 'movie'].to_dict(orient='records')
                books_list = recommended_contents[recommended_contents['content_type'] == 'book'].to_dict(orient='records')
                
                return render_template(
                    'home.html', 
                    movie_recommendations=movies_list, 
                    book_recommendations=books_list,
                    content_title=content_title
                )
            else:
                return render_template('home.html')

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app = RecommenderApp()
    app.run()
