from flask import Flask, render_template, jsonify,Blueprint
import json
import os

bp = Blueprint('rajya_sabha_candidate_overview', __name__)

# Load the data
def load_rajya_candidate_data():
    try:
        with open('app/data/wmprs.json', 'r') as f:
            data = json.load(f)

            # Check for missing images and add alt text or fallback URL
            for candidate in data.values():
                image_url = candidate.get('image_url')
                print(image_url)
                image_path = os.path.join('app','static', image_url) if image_url else None
                print(image_path)
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
candidates_data = load_rajya_candidate_data()

@bp.route('/rajya_sabha_overview')
def index():
    return render_template('rajya_sabha_overview.html', candidates=candidates_data)

@bp.route('/api/rajya_candidates')
def get_rajya_candidates():
    return jsonify(candidates_data)

@bp.route('/api/rajya_candidate/<name>')
def get_rajya_candidate(name):
    candidate = candidates_data.get(name)
    if candidate:
        return jsonify(candidate)
    return jsonify({"error": "Candidate not found"}), 404

