from flask import Blueprint, request, jsonify, render_template
from dotenv import load_dotenv
from app.models.constituency_service import ConstituencyService
import os

# Load environment variables
load_dotenv()

# Create blueprint
bp = Blueprint('constituency', __name__)

# Initialize the ConstituencyService with the API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
constituency_service = ConstituencyService(GROQ_API_KEY)

@bp.route('/constituency')
def home():
    """Render the home page."""
    return render_template('constituency.html')

@bp.route('/api/states')
def get_states():
    """Return list of Indian states."""
    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
        "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
        "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
        "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
        "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]
    return jsonify({"success": True, "data": states})

@bp.route('/find_constituency', methods=['POST'])
def find_constituency():
    """Handle constituency search requests."""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON"
            }), 400

        data = request.get_json()
        required_fields = ['state', 'district', 'locality']
        
        # Validate all required fields are present and not empty
        missing_fields = [field for field in required_fields 
                         if not data.get(field, '').strip()]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        result = constituency_service.find_constituency(
            data['state'].strip(),
            data['district'].strip(),
            data['locality'].strip()
        )
        
        if not result["success"]:
            return jsonify(result), 400
            
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500
