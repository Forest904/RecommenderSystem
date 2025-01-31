from flask import request, jsonify
from database.db_handler import get_db
import bcrypt

class UserService:
    """
    Service layer for handling user account and library operations.
    """
    @staticmethod
    def create_user():
        try:
            data = request.json
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()

            if not username or not password:
                return jsonify({"error": "Username and password cannot be empty."}), 400

            # Hash the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            db = get_db()
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            db.commit()
            db.close()

            return jsonify({"message": "User created successfully."}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def login():
        try:
            data = request.json  # POST data
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()

            if not username or not password:
                return jsonify({"error": "Username and password are required."}), 400

            db = get_db()
            user = db.execute(
                "SELECT id, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()

            if user is None or not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
                return jsonify({"error": "Invalid username or password."}), 401

            return jsonify({"user_id": user["id"]}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_profile():
        try:
            user_id = request.args.get("user_id")

            if not user_id:
                return jsonify({"error": "User ID is required."}), 400

            db = get_db()
            user = db.execute(
                "SELECT id, username FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

            if user is None:
                return jsonify({"error": "User not found."}), 404

            return jsonify({"user_id": user["id"], "username": user["username"]}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500



    @staticmethod
    def get_user_library():
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

    @staticmethod
    def add_to_library():
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

    @staticmethod
    def delete_from_library():
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
