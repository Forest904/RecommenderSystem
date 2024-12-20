from flask import request, jsonify
from utils.recommendator import get_balanced_recommendations, load_datasets
from database.db_handler import get_db
import pandas as pd

class RecommendationService:
    """
    Service layer for handling recommendation and user-related operations.
    """
    def __init__(self):
        self.df = load_datasets()

    def handle_request(self):
        
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

    @staticmethod
    def create_user():
        """
        Handle user creation by inserting the user data into the database.
        """
        try:
            data = request.json
            username = data.get("username", "").strip()
            email = data.get("email", "").strip()

            if not username or not email:
                return jsonify({"error": "Username and email cannot be empty."}), 400

            db = get_db()
            db.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                (username, email),
            )
            db.commit()

            return jsonify({"message": "User created successfully."}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500
