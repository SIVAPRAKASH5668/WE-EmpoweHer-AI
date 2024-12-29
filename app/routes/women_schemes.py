# app/routes/women_schemes.py

from flask import Blueprint, request, render_template, jsonify
from app.models.women_schemes_bot import WomenSchemesBot
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Create a blueprint for the women_schemes route
bp = Blueprint('women_schemes', __name__)

# Create a bot instance
bot = WomenSchemesBot(GROQ_API_KEY)

# Route to display the form for searching schemes
@bp.route('/women_schemes')
def index():
    return render_template('schemes.html')

# Route to handle the form submission and search for schemes
@bp.route('/search_schemes', methods=['POST'])
def search_schemes():
    user_details = request.json  # Get user details from the form (assumes JSON POST request)
    search_prompt = bot.generate_search_prompt(user_details)
    schemes_response = bot.search_schemes(search_prompt)
    return jsonify(schemes_response)  # Return the schemes as a JSON response
