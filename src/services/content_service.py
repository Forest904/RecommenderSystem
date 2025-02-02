from database.db_handler import get_db
from flask import jsonify, request

class ContentService:
    @staticmethod
    def get_content(page=1, limit=20, search_query='', content_type='', sort_by='title', order='asc'):
        try:
            db = get_db()
            offset = (page - 1) * limit

            print(f"🔥 Received search_query: '{search_query}'")  # Debug

            # Validate sorting parameters.
            valid_sort_fields = {
                "title": "title",
                "release": "release_date",
                "vote_average": "vote_average"
            }
            sort_column = valid_sort_fields.get(sort_by, "title")
            order = "ASC" if order.lower() == "asc" else "DESC"

            # Build separate filters and parameter lists for movies and books.
            movie_filter = "1=1"
            book_filter = "1=1"
            params_movies = []
            params_books = []

            if search_query:
                movie_filter += " AND title LIKE ?"
                book_filter += " AND title LIKE ?"
                params_movies.append(f"%{search_query}%")
                params_books.append(f"%{search_query}%")

            # Construct the two sub-queries.
            query_movies = f"""
                SELECT id, title, 'Movie' AS type, author, genres, plot, vote_average, vote_count, 
                    release_date, large_cover_url 
                FROM movies WHERE {movie_filter}
            """
            query_books = f"""
                SELECT id, title, 'Book' AS type, author, genres, plot, vote_average, vote_count, 
                    release_date, large_cover_url 
                FROM books WHERE {book_filter}
            """

            # Combine the two queries via UNION ALL, then sort and paginate.
            full_query = f"""
                SELECT * FROM (
                    {query_movies}
                    UNION ALL
                    {query_books}
                ) AS content
                ORDER BY {sort_column} {order}
                LIMIT ? OFFSET ?
            """

            # Merge the parameters in the order in which the placeholders appear.
            parameters = params_movies + params_books + [limit, offset]

            print(f"🔥 Executing Query:\n{full_query}")
            print(f"🔥 Query Parameters:\n{parameters}")

            results = db.execute(full_query, parameters).fetchall()

            return jsonify([dict(item) for item in results]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_search_suggestions():
        try:
            search_query = request.args.get("query", "").strip()
            if not search_query:
                return jsonify([]), 200

            db = get_db()
            query = """
                SELECT title FROM (
                    SELECT title FROM movies WHERE title LIKE ?
                    UNION ALL
                    SELECT title FROM books WHERE title LIKE ?
                ) LIMIT 10
            """
            params = (f"%{search_query}%", f"%{search_query}%")

            print(f"Executing query: {query} with params: {params}")

            results = db.execute(query, params).fetchall()

            suggestions = [row["title"] for row in results]
            print(f"Suggestions found: {suggestions}")

            return jsonify(suggestions), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
