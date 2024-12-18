from flask import Flask, render_template, request
from utils.recommendator import initialize_recommender, get_balanced_recommendations
from utils.contents_fetcher import get_content_url
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Number of recommendations to show per type
NUM_RECOMMENDATIONS = 12

# Initialize recommender data only once to avoid redundant computations
df, embeddings = initialize_recommender()

class RecommenderApp:
    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            if request.method == 'POST':
                # Retrieve and validate the content title submitted by the user
                content_title = request.form.get('title', '').strip()
                if not content_title:
                    error_message = "Content title cannot be empty."
                    logger.warning("Empty content title submitted.")
                    return render_template('index.html', error=error_message)

                # Log the received content title
                logger.info(f"Received content title: {content_title}")

                # Generate recommendations based on the input title
                recommendations = get_balanced_recommendations(
                    content_title, NUM_RECOMMENDATIONS, df, embeddings
                )

                # Handle the case where no recommendations are found
                if not recommendations:
                    error_message = f"Content titled '{content_title}' not found."
                    logger.warning(f"No recommendations found for title: {content_title}")
                    return render_template('index.html', error=error_message)

                # Filter the recommended items from the dataset
                recommended_contents = df[df['Title'].isin(recommendations)].copy()

                async def enrich_recommendations():
                    tasks = []

                    # Add image URL fetching tasks with error handling
                    for _, row in recommended_contents.iterrows():
                        tasks.append(get_content_url(row['Title'], row['Type']))

                    # Await the concurrent completion of all tasks, with exceptions handled
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Process results and log errors if any
                    enriched_urls = []
                    for idx, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(f"Error fetching data for title '{recommended_contents.iloc[idx]['Title']}': {result}")
                            enriched_urls.append(None)
                        else:
                            enriched_urls.append(result)

                    # Add the fetched image URLs to the dataset
                    recommended_contents['image_url'] = enriched_urls

                # Run the asynchronous enrichment process
                asyncio.run(enrich_recommendations())

                # Separate the recommendations into movies and books for the template
                movies_list = recommended_contents[recommended_contents['Type'] == 'movie'].to_dict(orient='records')
                books_list = recommended_contents[recommended_contents['Type'] == 'book'].to_dict(orient='records')

                # Render the results on the home page
                return render_template(
                    'home.html',
                    movie_recommendations=movies_list,
                    book_recommendations=books_list,
                    content_title=content_title
                )
            else:
                # Handle GET requests by rendering the empty home page
                return render_template('home.html')

    def run(self):
        # Start the Flask application in debug mode
        self.app.run(debug=True)

if __name__ == '__main__':
    # Create and run an instance of the RecommenderApp
    app = RecommenderApp()
    app.run()
