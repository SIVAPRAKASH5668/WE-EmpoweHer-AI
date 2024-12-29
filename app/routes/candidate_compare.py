from flask import Blueprint, render_template, request, jsonify
import os
from dotenv import load_dotenv
from app.models.indian_election_analyzer import IndianElectionAnalyzer  # Import the analysis logic

# Create the Blueprint object
bp = Blueprint('candidate_compare', __name__)

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Initialize the election analyzer (this is where the analysis logic is)
analyzer = IndianElectionAnalyzer()

# Define routes for the Blueprint

@bp.route('/candidate_compare')
def home():
    """Render the compare page"""
    return render_template('compare.html')

@bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze the provided candidates and return comparison results"""
    data = request.get_json()
    # Get candidates and sector from the request data
    candidates = data['candidates']
    sector = data['sector']
    
    # Use the IndianElectionAnalyzer to compare candidates
    results = analyzer.compare_candidates(candidates, sector)
    
    # Return the results as a JSON response
    return jsonify(results)
