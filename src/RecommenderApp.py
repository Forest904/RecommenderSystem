from flask import Flask
from flask_cors import CORS
from database.db_handler import init_db
from services.recommendations_service import RecommendationService
from services.content_service import ContentService
from services.user_service import UserService
from utils.error_handler import error_response
from flask import request

app = Flask(__name__)
CORS(app)

# Initialize service instances
recommender_service = RecommendationService()
user_service = UserService()
content_service = ContentService()

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    return error_response(str(e), 500)

# Recommendation endpoints
@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    return recommender_service.get_recommendations()

# User account endpoints
@app.route('/create_user', methods=['POST'])
def create_user():
    return UserService.create_user()

@app.route('/account', methods=['POST', 'GET'])
def manage_account():
    if request.method == 'POST':
        return UserService.login()
    elif request.method == 'GET':
        return UserService.get_profile_details()
    
# Profile details endpoints
@app.route('/update_profile', methods=['POST'])
def update_profile():
    return UserService.update_profile_details()

# Library management endpoints
@app.route('/library', methods=['GET', 'POST', 'DELETE'])
def manage_library():
    if request.method == 'GET':
        return user_service.get_user_library()
    elif request.method == 'POST':
        return user_service.add_to_library()
    elif request.method == 'DELETE':
        return user_service.delete_from_library()
    
# Content fetching endpoint
@app.route('/content', methods=['GET'])
def get_content():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    # Use the proper parameter names as provided by the front end
    search_query = request.args.get('search_query', '').strip()
    content_type = request.args.get('type', '').strip()
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    
    return content_service.get_content(page, limit, search_query, content_type, sort_by, order)

@app.route('/search_suggestions', methods=['GET'])
def search_suggestions():
    return content_service.get_search_suggestions()

@app.route('/favorites', methods=['GET', 'POST', 'DELETE'])
def manage_favorites():
    if request.method == 'GET':
        return user_service.get_user_favorites()
    elif request.method == 'POST':
        return user_service.add_to_favorites()
    elif request.method == 'DELETE':
        return user_service.remove_from_favorites()

@app.route('/favicon.ico')
def favicon():
    return ('', 204)  # Respond with No Content

if __name__ == "__main__":
    # Initialize the database
    init_db(app)
    app.run(debug=True)
