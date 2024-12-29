from flask import Flask, render_template, request, jsonify, Blueprint
from app.models.election_analysis import analyze_election_data

bp = Blueprint('election_analy', __name__)

@bp.route('/election_analy')
def home():
    """Render the home page"""
    return render_template('election_analy.html')

@bp.route('/analyze_election_analysis', methods=['POST'])
def analyze():
    """Handle analysis requests"""
    
    state = request.form.get('state', '').strip()
    district = request.form.get('district', '').strip()
    ward = request.form.get('ward', '').strip()

    # Check if all required fields are provided
    if not all([state, district, ward]):
        return jsonify({
            "error": "Please provide all required fields: state, district, and ward"
        }), 400

    # Analyze the election data (replace with your actual logic)
    analysis_result = analyze_election_data(state, district, ward)

    return jsonify(analysis_result)

@bp.route('/states_list')
def get_states():
    """Return list of Indian states"""
    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
        "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
        "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
        "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
        "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir", "Lakshadweep"
    ]
    return jsonify(states)
