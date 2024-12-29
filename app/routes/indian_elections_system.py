from flask import Blueprint, render_template
import os

bp = Blueprint('indian_election_system', __name__)

@bp.route('/indian_election_system')
def index():
    return render_template('indian_election_system/indian_election_system.html')

@bp.route('/indian_state_election_system')
def state():
    return render_template('indian_election_system/indian_state_election_system.html')

@bp.route('/state/indian_election_system/tamil-nadu')
def tamil_nadu():
    return render_template('indian_election_system/tamil-nadu.html')
