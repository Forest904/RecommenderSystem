from flask import Flask
from flask_cors import CORS
from database.db_handler import init_db
from services.recommendations import RecommendationService
from utils.error_handler import error_response
from flask import request

app = Flask(__name__)
CORS(app)

recommender_service = RecommendationService()

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    return error_response(str(e), 500)

# Endpoint to fetch recommendations
@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    return recommender_service.handle_request()

# Endpoint to create a user
@app.route('/create_user', methods=['POST'])
def create_user():
    return recommender_service.create_user()

@app.route('/account', methods=['GET', 'PUT'])
def manage_account():
    if request.method == 'GET':
        return recommender_service.get_account_details()
    elif request.method == 'PUT':
        return recommender_service.update_account_details()

@app.route('/library', methods=['GET', 'POST', 'DELETE'])
def manage_library():
    if request.method == 'GET':
        return recommender_service.get_user_library()
    elif request.method == 'POST':
        return recommender_service.add_to_library()
    elif request.method == 'DELETE':
        return recommender_service.delete_from_library()


if __name__ == "__main__":
    # Initialize the database
    init_db(app)
    app.run(debug=True)
