from database.db_handler import get_db
from flask import jsonify, request

class ContentService:
    @staticmethod
    def get_content(page=1, limit=20, search_query='', content_type='', sort_by='title', order='asc'):
        try:
            db = get_db()
            
            # Validate sorting parameters.
            valid_sort_fields = {
                "title": "title",
                "release": "release_date",
                "vote_average": "vote_average"
            }
            sort_column = valid_sort_fields.get(sort_by, "title")
            order_clause = "ASC" if order.lower() == "asc" else "DESC"
            
            # Compute offset for pagination.
            offset = (page - 1) * limit

            # Build the filter clause for the search query.
            # (You can extend this if you add more filters later.)
            filter_clause = "1=1"
            params = []
            if search_query:
                filter_clause += " AND title LIKE ?"
                params.append(f"%{search_query}%")

            # If a specific content type is requested, run only that query.
            if content_type.lower() == 'movie':
                query = f"""
                    SELECT id, title, 'Movie' AS type, author, genres, plot, vote_average, vote_count, 
                        release_date, large_cover_url 
                    FROM movies 
                    WHERE {filter_clause}
                    ORDER BY {sort_column} {order_clause}
                    LIMIT ? OFFSET ?
                """
                params_with_pagination = params + [limit, offset]
                results = db.execute(query, params_with_pagination).fetchall()
                return jsonify([dict(item) for item in results]), 200

            elif content_type.lower() == 'book':
                query = f"""
                    SELECT id, title, 'Book' AS type, author, genres, plot, vote_average, vote_count, 
                        release_date, large_cover_url 
                    FROM books 
                    WHERE {filter_clause}
                    ORDER BY {sort_column} {order_clause}
                    LIMIT ? OFFSET ?
                """
                params_with_pagination = params + [limit, offset]
                results = db.execute(query, params_with_pagination).fetchall()
                return jsonify([dict(item) for item in results]), 200

            else:
                # When no content_type is provided, get balanced results from both tables.
                query_movies = f"""
                    SELECT id, title, 'Movie' AS type, author, genres, plot, vote_average, vote_count, 
                        release_date, large_cover_url 
                    FROM movies 
                    WHERE {filter_clause}
                    ORDER BY {sort_column} {order_clause}
                    LIMIT ? OFFSET ?
                """
                query_books = f"""
                    SELECT id, title, 'Book' AS type, author, genres, plot, vote_average, vote_count, 
                        release_date, large_cover_url 
                    FROM books 
                    WHERE {filter_clause}
                    ORDER BY {sort_column} {order_clause}
                    LIMIT ? OFFSET ?
                """
                params_movies = params + [limit, offset]
                params_books = params + [limit, offset]

                results_movies = db.execute(query_movies, params_movies).fetchall()
                results_books = db.execute(query_books, params_books).fetchall()

                # Combine the two result sets.
                # (If you prefer interleaving the two lists instead of concatenation,
                #  you could loop over the two lists alternately.)
                combined_results = [dict(item) for item in results_movies] + [dict(item) for item in results_books]

                return jsonify(combined_results), 200

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

            results = db.execute(query, params).fetchall()

            suggestions = [row["title"] for row in results]
            return jsonify(suggestions), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
