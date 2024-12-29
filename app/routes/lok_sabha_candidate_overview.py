from flask import Flask, render_template, jsonify,Blueprint
import json
import os

bp = Blueprint('lok_sabha_candidate_overview', __name__)

# Load the data
def load_candidate_data():
    try:
        with open('app/data/wmpls.json', 'r') as f:
            data = json.load(f)

            # Check for missing images and add alt text or fallback URL
            for candidate in data.values():
                image_url = candidate.get('image_url')
                image_path = os.path.join('app','static', image_url) if image_url else None
                # Check if the image exists or if it's missing in the folder
                if not image_url or not os.path.exists(image_path):
                    candidate['image_url'] = 'placeholder.jpg'  # Fallback to placeholder image
                candidate['alt_text'] = candidate.get('alt_text', "Image not available")
            return data
    except FileNotFoundError:
        print("Error: wmpls.json file not found")
        return {}
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in wmpls.json")
        return {}

# Load the candidate data
candidates_data = load_candidate_data()

@bp.route('/lok_sabha_overview')
def index():
    return render_template('lok_sabha_overview.html', candidates=candidates_data)

@bp.route('/api/candidates')
def get_candidates():
    return jsonify(candidates_data)

@bp.route('/api/candidate/<name>')
def get_candidate(name):
    candidate = candidates_data.get(name)
    if candidate:
        return jsonify(candidate)
    return jsonify({"error": "Candidate not found"}), 404

