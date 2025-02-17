from flask import request, jsonify
from database.db_handler import get_db
import bcrypt

class UserService:
    """
    Service layer for handling user account, library, and favorites operations.
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
            cursor = db.cursor()

            # Insert user into users table
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            user_id = cursor.lastrowid  # Get the generated user ID

            # Create an empty profile for the user in user_profiles
            cursor.execute(
                "INSERT INTO user_profiles (user_id, first_name, last_name, date_of_birth, avatar_url, bio) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, None, None, None, None, None)
            )

            db.commit()
            db.close()

            return jsonify({"message": "User created successfully.", "user_id": user_id}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def login():
        try:
            data = request.json
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()

            if not username or not password:
                return jsonify({"error": "Username and password are required."}), 400

            db = get_db()
            user = db.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()

            if user is None or not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
                return jsonify({"error": "Invalid username or password."}), 401

            # Return user details including username
            return jsonify({
                "user_id": user["id"],
                "username": user["username"]
            }), 200

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
    def get_profile_details():
        try:
            user_id = request.args.get("user_id")

            if not user_id:
                return jsonify({"error": "User ID is required."}), 400

            db = get_db()
            user = db.execute(
                """
                SELECT u.id, u.username, p.first_name, p.last_name, p.date_of_birth, p.avatar_url, p.bio
                FROM users u
                LEFT JOIN user_profiles p ON u.id = p.user_id
                WHERE u.id = ?
                """,
                (user_id,),
            ).fetchone()

            if user is None:
                return jsonify({"error": "User not found."}), 404

            return jsonify(dict(user)), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @staticmethod
    def update_profile_details():
        try:
            data = request.json
            user_id = data.get("user_id")
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            date_of_birth = data.get("date_of_birth", "")
            avatar_url = data.get("avatar_url", "")
            bio = data.get("bio", "")
            user_color = data.get("user_color", "")

            if not user_id:
                return jsonify({"error": "User ID is required."}), 400

            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                """
                UPDATE user_profiles
                SET first_name = ?,
                    last_name = ?,
                    date_of_birth = ?,
                    avatar_url = ?,
                    bio = ?,
                    user_color = ?
                WHERE user_id = ?
                """,
                (first_name, last_name, date_of_birth, avatar_url, bio, user_color, user_id)
            )

            db.commit()
            db.close()

            return jsonify({"message": "Profile updated successfully."}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        
    @staticmethod
    def get_user_favorites():
        """
        Fetch the list of favorite movies and books for a user.
        """
        try:
            user_id = request.args.get("user_id")
            if not user_id:
                return jsonify({"error": "User ID is required."}), 400

            db = get_db()

            # Fetch favorite movies
            favorite_movies = db.execute(
                """
                SELECT m.id, m.title, 'Movie' AS type, m.large_cover_url, m.link
                FROM user_favorites uf
                JOIN movies m ON uf.content_id = m.id
                WHERE uf.user_id = ?
                """,
                (user_id,),
            ).fetchall()

            # Fetch favorite books
            favorite_books = db.execute(
                """
                SELECT b.id, b.title, 'Book' AS type, b.large_cover_url, b.link
                FROM user_favorites uf
                JOIN books b ON uf.content_id = b.id
                WHERE uf.user_id = ?
                """,
                (user_id,),
            ).fetchall()

            # Convert results to list of dictionaries
            favorites = [dict(item) for item in favorite_movies] + [dict(item) for item in favorite_books]

            return jsonify(favorites), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @staticmethod
    def add_to_favorites():
        try:
            data = request.json
            user_id = data.get("user_id")
            content_id = data.get("content_id")

            if not user_id or not content_id:
                return jsonify({"error": "User ID and Content ID are required."}), 400

            db = get_db()
            db.execute(
                "INSERT INTO user_favorites (user_id, content_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
                (user_id, content_id),
            )
            db.commit()

            return jsonify({"message": "Content added to favorites."}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def remove_from_favorites():
        try:
            data = request.json
            user_id = data.get("user_id")
            content_id = data.get("content_id")

            if not user_id or not content_id:
                return jsonify({"error": "User ID and Content ID are required."}), 400

            db = get_db()
            db.execute(
                "DELETE FROM user_favorites WHERE user_id = ? AND content_id = ?",
                (user_id, content_id),
            )
            db.commit()

            return jsonify({"message": "Content removed from favorites."}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
