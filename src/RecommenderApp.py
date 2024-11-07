from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from utils.note import get_recommendations, cross_content, title_type_df

# Assuming all your existing code is already executed here, including:
# - Data loading and preprocessing
# - Definition of get_recommendations function
# - Variables: cross_content, title_type_df, etc.

class RecommenderApp:
    def __init__(self):
        self.app = Flask(__name__)

        # Define the index route
        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            if request.method == 'POST':
                content_title = request.form['title']
                recommendations = get_recommendations(content_title, k=10)
                
                if not recommendations:
                    error_message = f"Content titled '{content_title}' not found."
                    return render_template('index.html', error=error_message)
                
                # Get additional information about recommendations
                recommended_contents = cross_content[cross_content['Title'].isin(recommendations)]
                
                # Convert DataFrame to a list of dictionaries for easy templating
                recommendations_list = recommended_contents.to_dict(orient='records')
                
                # Optional: Print the keys to verify 'content_type' is present
                # print(recommendations_list[0].keys())
                
                return render_template(
                    'index.html', 
                    recommendations=recommendations_list, 
                    content_title=content_title
                )
            else:
                return render_template('index.html')

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app = RecommenderApp()
    app.run()
