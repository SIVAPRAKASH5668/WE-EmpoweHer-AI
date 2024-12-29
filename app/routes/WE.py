from flask import Blueprint, request, render_template, jsonify

bp = Blueprint('WE', __name__)

# Home page (WE.html)
@bp.route('/')
def home():
    return render_template('WE.html')  # Renders the WE.html homepage
