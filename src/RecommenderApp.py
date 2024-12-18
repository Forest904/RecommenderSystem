from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.recommendator import initialize_recommender, get_balanced_recommendations
from utils.contents_fetcher import get_content_url
import asyncio
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize recommender data
df, embeddings = initialize_recommender()

# Create the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        content_title = data.get('title', '').strip()

        if not content_title:
            return jsonify({"error": "Content title cannot be empty."}), 400

        recommendations = get_balanced_recommendations(
            content_title, 12, df, embeddings
        )

        if not recommendations:
            return jsonify({"error": f"No recommendations found for '{content_title}'."}), 404

        recommended_contents = df[df['Title'].isin(recommendations)].copy()

        async def enrich_recommendations():
            tasks = [
                get_content_url(row['Title'], row['Type'])
                for _, row in recommended_contents.iterrows()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Replace exceptions with None for image_url
            results = [r if not isinstance(r, Exception) else None for r in results]
            return results

        # Enrich the recommendations with image URLs
        results = asyncio.run(enrich_recommendations())
        recommended_contents['image_url'] = results

        # Convert NaNs to None so JSON is valid
        recommended_contents = recommended_contents.where(pd.notnull(recommended_contents), None)

        # Return recommendations as JSON
        return jsonify(recommended_contents.to_dict(orient='records'))
    except Exception as e:
        logger.exception("Error in /recommendations endpoint")
        # Return a JSON error with 500 status code
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
