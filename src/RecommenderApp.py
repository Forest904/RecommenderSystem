from flask import Flask, render_template, request
from utils.recommendator import initialize_recommender, get_balanced_recommendations
from utils.contents_fetcher import get_movie_image_url, get_book_cover_url, get_plot


#Number of recommendations to show per type
NUM_RECOMMENDATIONS = 6

# Initialize recommender data only once
df, embeddings = initialize_recommender()

class RecommenderApp:
    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            if request.method == 'POST':
                content_title = request.form['title']
                
                # Pass preloaded df and embeddings
                recommendations = get_balanced_recommendations(
                    content_title, NUM_RECOMMENDATIONS, df, embeddings
                )
                
                if not recommendations:
                    error_message = f"Content titled '{content_title}' not found."
                    return render_template('index.html', error=error_message)

                # Prepare additional information
                recommended_contents = df[df['Title'].isin(recommendations)].copy()
                
                def get_image_url(row):
                    if row['Type'] == 'movie':
                        return get_movie_image_url(row['Title'])
                    elif row['Type'] == 'book':
                        return get_book_cover_url(row['Title'])
                    return None

                def get_p(title):
                    return get_plot(title)

                # Add image URLs and plots
                recommended_contents['image_url'] = recommended_contents.apply(get_image_url, axis=1)
                recommended_contents['plot'] = recommended_contents['Title'].apply(get_p)

                # Convert to dictionaries for templates
                movies_list = recommended_contents[recommended_contents['Type'] == 'movie'].to_dict(orient='records')
                books_list = recommended_contents[recommended_contents['Type'] == 'book'].to_dict(orient='records')
                
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
