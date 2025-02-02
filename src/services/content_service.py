from database.db_handler import get_db
from flask import jsonify

class ContentService:
    @staticmethod
    def get_content(page=1, limit=20, search_query='', content_type='', sort_by='title', order='asc'):
        try:
            db = get_db()
            offset = (page - 1) * limit

            # Define valid sorting fields
            valid_sort_fields = {
                "title": "title",
                "release": "release",
                "vote_average": "vote_average"
            }
            sort_column = valid_sort_fields.get(sort_by, "title")

            # Define sorting order
            order = "ASC" if order.lower() == "asc" else "DESC"

            # Base queries for movies and books
            base_query_movies = """
                SELECT id, title, 'Movie' AS type, author, genres, plot, vote_average, vote_count, 
                    release_date AS release, large_cover_url 
                FROM movies
            """
            base_query_books = """
                SELECT id, title, 'Book' AS type, author, genres, plot, vote_average, vote_count, 
                    release_date AS release, large_cover_url 
                FROM books
            """

            # Apply search filter
            filter_clause = ""
            params = []

            if search_query:
                filter_clause = " WHERE title LIKE ?"
                params.append(f"%{search_query}%")

            # Apply filters to both queries
            base_query_movies += filter_clause
            base_query_books += filter_clause

            # Use UNION ALL directly (no parentheses)
            full_query = f"""
                SELECT * FROM (
                    {base_query_movies}
                    UNION ALL
                    {base_query_books}
                ) 
                ORDER BY {sort_column} {order}
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])

            # Execute query
            results = db.execute(full_query, params).fetchall()

            return jsonify([dict(item) for item in results]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
