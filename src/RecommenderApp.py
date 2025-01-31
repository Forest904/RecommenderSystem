from flask import Flask
from flask_cors import CORS
from database.db_handler import init_db
from services.recommendations_service import RecommendationService
from services.user_service import UserService
from utils.error_handler import error_response
from flask import request

app = Flask(__name__)
CORS(app)

# Initialize service instances
recommender_service = RecommendationService()
user_service = UserService()

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
        return UserService.login()  # Ensure this method correctly handles login requests
    elif request.method == 'GET':
        return UserService.get_profile()  # Optional: Use GET to fetch user profile info


# Library management endpoints
@app.route('/library', methods=['GET', 'POST', 'DELETE'])
def manage_library():
    if request.method == 'GET':
        return user_service.get_user_library()
    elif request.method == 'POST':
        return user_service.add_to_library()
    elif request.method == 'DELETE':
        return user_service.delete_from_library()

if __name__ == "__main__":
    # Initialize the database
    init_db(app)
    app.run(debug=True)
