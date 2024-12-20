from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.recommendator import get_balanced_recommendations, load_datasets
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load saved datasets
df = load_datasets()

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

        recommendations = get_balanced_recommendations(content_title, 12)

        if not recommendations:
            return jsonify({"error": f"No recommendations found for '{content_title}'."}), 404

        recommended_contents = df[df['title'].isin(recommendations)].copy()

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
