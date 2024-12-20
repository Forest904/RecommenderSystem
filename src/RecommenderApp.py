from flask import Flask
from flask_cors import CORS
from database.db_handler import init_db
from services.recommendations import RecommendationService
from utils.error_handler import error_response

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

if __name__ == "__main__":
    # Initialize the database
    init_db(app)
    app.run(debug=True)
