# app/routes/employment.py

from flask import Blueprint, render_template, request, jsonify
from app.models.employment_opportunity import get_bot_response, rate_limit
import logging

# Initialize the Blueprint for the 'employment' route
bp = Blueprint('employment', __name__)
# Configure logging
logger = logging.getLogger(__name__)

# Define your routes
@bp.route('/employment')
def index():
    try:
        return render_template('employ.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return jsonify({"error": "Error loading page"}), 500

@bp.route('/api/chat', methods=['POST'])
@rate_limit  # Apply rate limiting to this endpoint
def chat():
    try:
        data = request.get_json()
        if not data:
            logger.error("No data provided in request")
            return jsonify({"error": "No data provided"}), 400
            
        user_message = data.get('message', '').strip()
        if not user_message:
            logger.error("Received an empty message")
            return jsonify({"error": "Message cannot be empty"}), 400
            
        response = get_bot_response(user_message)
        logger.info(f"User message: {user_message}")
        logger.info(f"Bot response: {response}")
        
        return jsonify({"response": response})
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500
