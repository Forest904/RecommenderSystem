from flask import request, jsonify
from utils.recommendator import get_balanced_recommendations, load_datasets
from database.db_handler import get_db
import pandas as pd

class RecommendationService:
    """
    Service layer for handling recommendation, account, and library operations.
    """
    def __init__(self):
        self.df = load_datasets()

    def get_recommendations(self):
        try:
            data = request.json
            title = data.get("title", "").strip()

            if not title:
                return jsonify({"error": "Content title cannot be empty."}), 400

            # Fetch balanced recommendations
            recommendations = get_balanced_recommendations(title, 12)
            recommended_contents = self.df[self.df['title'].isin(recommendations)].copy()
            # Convert NaNs to None so JSON is valid
            recommended_contents = recommended_contents.where(pd.notnull(recommended_contents), None)

            # Return recommendations as JSON
            return jsonify(recommended_contents.to_dict(orient='records'))

        except Exception as e:
            return jsonify({"error": str(e)}), 500

