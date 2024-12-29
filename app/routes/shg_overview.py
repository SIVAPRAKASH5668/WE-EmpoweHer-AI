from flask import Flask, render_template, jsonify, Blueprint
import json
import os

# Create a Blueprint for SHG Overview
bp = Blueprint('shg_overview', __name__)

# Load the SHG data
def load_shg_data():
    try:
        with open('app/data/selfhelpgrp.json', 'r') as file:
            data = json.load(file)

            # Check for missing images and add alt text or fallback URL
            for shg in data:
                image_url = shg.get('image_url')
                print(image_url)
                image_path = os.path.join('app','static', image_url) if image_url else None
                print(image_path)
                
                # Check if the image exists or if it's missing in the folder
                if not image_url or not os.path.exists(image_path):
                    shg['image_url'] = 'placeholder.jpg'  # Fallback to placeholder image
                shg['alt_text'] = shg.get('alt_text', "Image not available")
            return data
    except FileNotFoundError:
        print("Error: selfhelpgrp.json file not found")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in selfhelpgrp.json")
        return []

# Load SHG data
shg_data = load_shg_data()

@bp.route('/shg_overview')
def index():
    return render_template('shg_overview.html', shgs=shg_data)

@bp.route('/api/shgs')
def get_shgs():
    return jsonify(shg_data)

@bp.route('/api/shg/<name>')
def get_shg(name):
    shg = next((item for item in shg_data if item["name"] == name), None)
    if shg:
        return jsonify(shg)
    return jsonify({"error": "SHG not found"}), 404

# Initialize the Flask app
app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)
