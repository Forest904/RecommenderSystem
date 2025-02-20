from flask import request, jsonify
from utils.recommendator import get_balanced_recommendations, load_datasets
from database.db_handler import get_db
import pandas as pd

class RecommendationService:
    """
    Service layer for handling recommendation.
    """
    def __init__(self):
        self.df = load_datasets()

    def get_recommendations(self):
        try:
            data = request.json
            titles = data.get("titles", [])

            if not titles or not isinstance(titles, list):
                return jsonify({"error": "A list of content titles is required."}), 400

            recommendations = []
            for title in titles:
                recs = get_balanced_recommendations(title, 12)
                #print(f"Recommendations for {title}: {recs}")  # Debugging log
                recommended_contents = self.df[self.df['title'].isin(recs)].copy()
                recommended_contents = recommended_contents.where(pd.notnull(recommended_contents), None)
                recommendations.extend(recommended_contents.to_dict(orient='records'))

            #print("Final Recommendations:", recommendations)  # Debugging log
            return jsonify(recommendations)

        except Exception as e:
            #print("Error in get_recommendations:", str(e))  # Debugging log
            return jsonify({"error": str(e)}), 500
