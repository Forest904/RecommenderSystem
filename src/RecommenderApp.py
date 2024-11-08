from flask import Flask, render_template, request
from utils.recommendations_fetcher import get_recommendations, cross_content, title_type_df
from utils.images_fetcher import get_movie_image_url, get_book_cover_url

# TO-DO Load the data instead of fetching it from api
#df_movies_images_url = pd.read_csv('src/repository/movie_images.csv')
#df_books_images_url = pd.read_csv()

class RecommenderApp:
    def __init__(self):
        self.app = Flask(__name__)

        # Define the index route
        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            if request.method == 'POST':
                content_title = request.form['title']
                recommendations = get_recommendations(content_title, k=10)
                
                if not recommendations:
                    error_message = f"Content titled '{content_title}' not found."
                    return render_template('index.html', error=error_message)
                
                # Get additional information about recommendations
                recommended_contents = cross_content[cross_content['Title'].isin(recommendations)]

                # Get image URLs based on content type
                def get_image_url(row):
                    if row['content_type'] == 'movie':
                        return get_movie_image_url(row['Title'])
                    elif row['content_type'] == 'book':
                        return get_book_cover_url(row['Title'])
                    else:
                        return None

                recommended_contents['image_url'] = recommended_contents.apply(get_image_url, axis=1)
                
                # Convert DataFrame to a list of dictionaries for easy templating
                recommendations_list = recommended_contents.to_dict(orient='records')
                
                return render_template(
                    'index.html', 
                    recommendations=recommendations_list, 
                    content_title=content_title
                )
            else:
                return render_template('index.html')

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app = RecommenderApp()
    app.run()
