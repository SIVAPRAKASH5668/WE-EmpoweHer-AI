from flask import Blueprint, request, jsonify, render_template,send_from_directory
import requests
import base64
import os
import time
import logging

# Blueprint setup
bp = Blueprint("image_gen", __name__)

# Logger setup
logger = logging.getLogger(__name__)

# Load .env file for environment variables
from dotenv import load_dotenv
load_dotenv()

def wait_for_model(headers, api_url, max_retries=5, initial_wait=2):
    """Check if model is ready and wait if necessary"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": "test"},
                timeout=10
            )
            
            if response.status_code == 200:
                return True
                
            if response.status_code == 503:
                error_data = response.json()
                if "estimated_time" in error_data:
                    wait_time = min(float(error_data["estimated_time"]), 20)
                    return {"wait_time": wait_time}
            
            time.sleep(initial_wait * (attempt + 1))
            
        except Exception as e:
            logger.error(f"Error checking model status: {str(e)}")
            time.sleep(initial_wait * (attempt + 1))
    
    return False

def generate_image(prompt):
    """Generate an image using the Hugging Face API"""
    API_TOKEN = os.getenv("HF_API_TOKEN")
    if not API_TOKEN:
        raise Exception("API token not configured")

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    model_status = wait_for_model(headers, API_URL)
    if isinstance(model_status, dict) and "wait_time" in model_status:
        return {"status": "loading", "wait_time": model_status["wait_time"]}
    
    if not model_status:
        raise Exception("Model is unavailable. Please try again later.")
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            return {"status": "success", "image": response.content}
            
        error_message = response.text
        try:
            error_data = response.json()
            if "error" in error_data:
                error_message = error_data["error"]
        except:
            pass
            
        raise Exception(f"API Error {response.status_code}: {error_message}")
            
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. Please try again.")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

# Route for homepage (index)
@bp.route("/img_generator", methods=["GET"])
def index():
    return render_template("img_gen.html")


# Route for generating images
@bp.route("/generate_img", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        if not data or "prompt" not in data:
            return jsonify({"error": "Prompt is required"}), 400
        
        prompt = data["prompt"].strip()
        if not prompt:
            return jsonify({"error": "Prompt cannot be empty"}), 400
        
        result = generate_image(prompt)
        
        if isinstance(result, dict) and result.get("status") == "loading":
            return jsonify({
                "status": "loading",
                "wait_time": result["wait_time"],
                "message": "Model is warming up"
            }), 202
            
        if isinstance(result, dict) and result.get("status") == "success":
            encoded_image = base64.b64encode(result["image"]).decode("utf-8")
            return jsonify({"status": "success", "image": encoded_image})
        
        return jsonify({"error": "Unexpected response format"}), 500
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500
