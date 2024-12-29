from flask import Blueprint, render_template, request, jsonify
from app.models.panchayat_analy_service import PanchayatAnalyzer  # Import the PanchayatAnalyzer class

# Create the Blueprint instance
bp = Blueprint('panchayat', __name__)

# Initialize the PanchayatAnalyzer
analyzer = PanchayatAnalyzer()

@bp.route('/panchayat')
def home():
    """Render the home page"""
    return render_template('panchayat_analy.html')

@bp.route('/panchayat_analyze', methods=['POST'])
def analyze():
    """Handle analysis requests with input validation"""
    try:
        data = request.get_json()
        state = data.get('state', '').strip()
        district = data.get('district', '').strip()
        village = data.get('village', '').strip()

        # Validate input data
        if not all([state, district, village]):
            return jsonify({
                "success": False,
                "error": "Please provide all required fields: state, district, and village"
            }), 400

        result = analyzer.analyze_panchayat_election(state, district, village)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Analysis error: {str(e)}",
            "data": analyzer.create_default_response()
        }), 500

@bp.route('/api/states', methods=['GET'])
def get_states():
    """Return list of Indian states"""
    try:
        states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
            "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
            "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
            "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
            "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
            "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]
        return jsonify({
            "success": True,
            "data": states
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching states: {str(e)}"
        }), 500
