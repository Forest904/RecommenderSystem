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

    def get_account_details(self):
        """
        Fetch account details for the logged-in user.
        """
        try:
            user_id = request.args.get("user_id")

            if not user_id:
                return jsonify({"error": "User ID is required."}), 400

            db = get_db()
            user = db.execute(
                "SELECT id, username, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

            if user is None:
                return jsonify({"error": "User not found."}), 404

            return jsonify(dict(user)), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def update_account_details(self):
        """
        Update account details for the logged-in user.
        """
        try:
            data = request.json
            user_id = data.get("user_id")
            username = data.get("username", "").strip()
            email = data.get("email", "").strip()

            if not user_id or not username or not email:
                return jsonify({"error": "User ID, username, and email are required."}), 400

            db = get_db()
            db.execute(
                "UPDATE users SET username = ?, email = ? WHERE id = ?",
                (username, email, user_id),
            )
            db.commit()

            return jsonify({"message": "Account updated successfully."}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_user_library(self):
        """
        Fetch library items for the logged-in user.
        """
        try:
            user_id = request.args.get("user_id")

            if not user_id:
                return jsonify({"error": "User ID is required."}), 400

            db = get_db()
            library = db.execute(
                """
                SELECT c.id, c.title, c.type, c.large_cover_url
                FROM user_library ul
                JOIN contents c ON ul.content_id = c.id
                WHERE ul.user_id = ?
                """,
                (user_id,),
            ).fetchall()

            return jsonify([dict(item) for item in library]), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def add_to_library(self):
        """
        Add a content item to the user's library.
        """
        try:
            data = request.json
            user_id = data.get("user_id")
            content_id = data.get("content_id")

            if not user_id or not content_id:
                return jsonify({"error": "User ID and content ID are required."}), 400

            db = get_db()
            db.execute(
                "INSERT INTO user_library (user_id, content_id) VALUES (?, ?)",
                (user_id, content_id),
            )
            db.commit()

            return jsonify({"message": "Content added to library successfully."}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def delete_from_library(self):
        """
        Remove a content item from the user's library.
        """
        try:
            data = request.json
            user_id = data.get("user_id")
            content_id = data.get("content_id")

            if not user_id or not content_id:
                return jsonify({"error": "User ID and content ID are required."}), 400

            db = get_db()
            db.execute(
                "DELETE FROM user_library WHERE user_id = ? AND content_id = ?",
                (user_id, content_id),
            )
            db.commit()

            return jsonify({"message": "Content removed from library successfully."}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
