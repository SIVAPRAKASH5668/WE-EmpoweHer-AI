# routes.py

from flask import Blueprint, request, jsonify,render_template
from app.models.gov_services import get_services

# Create a Blueprint for your routes
bp = Blueprint('gov_services', __name__)

@bp.route('/api/services', methods=['POST'])
def fetch_services():
    data = request.json
    result = get_services(
        data['district'],
        data['locationType'],
        data['locationName']
    )
    return jsonify(result)

@bp.route('/gov_services')
def home():
    """Render the compare page"""
    return render_template('services.html')
