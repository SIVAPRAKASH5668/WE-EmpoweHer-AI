from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

from .routes import candidate_compare, employment, gov_services, women_schemes,WE,indian_elections_system,complain_route,constituency_routes,lok_sabha_candidate_overview,election_analy,panchayat_analy,rajya_sabha_candidate_overview,shg_overview,img_gen

def create_app():
    # Initialize Flask app
    app = Flask(__name__,static_folder='static')

    # Load environment variables from .env file
    load_dotenv()  # Ensure .env file is loaded for environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-default-secret-key')  # Ensure SECRET_KEY is set
    
    # Optionally, load configuration from file
    app.config.from_pyfile('config.py')

    # Enable CORS if the front-end is hosted on a different domain
    CORS(app)

    # Register blueprints
    app.register_blueprint(WE.bp)
    app.register_blueprint(candidate_compare.bp)
    app.register_blueprint(employment.bp)
    app.register_blueprint(gov_services.bp)
    app.register_blueprint(women_schemes.bp)
    app.register_blueprint(indian_elections_system.bp)
    app.register_blueprint(complain_route.bp)
    app.register_blueprint(constituency_routes.bp)
    app.register_blueprint(lok_sabha_candidate_overview.bp)
    app.register_blueprint(rajya_sabha_candidate_overview.bp)
    app.register_blueprint(election_analy.bp)
    app.register_blueprint(panchayat_analy.bp)
    app.register_blueprint(shg_overview.bp)
    app.register_blueprint(img_gen.bp)
    # Global error handling (optional)
    @app.errorhandler(404)
    def page_not_found(e):
        return {"error": "Page not found"}, 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return {"error": "Internal server error"}, 500
    # Optionally, set up logging (You can configure logging as per your needs)
    import logging
    logging.basicConfig(level=logging.DEBUG)  # You can adjust the level (DEBUG, INFO, ERROR)
    logger = logging.getLogger(__name__)

    return app
