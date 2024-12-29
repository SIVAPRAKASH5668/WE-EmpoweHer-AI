# app/services/employment_opportunity.py

from groq import Groq
from flask import jsonify, request
import os
from dotenv import load_dotenv
import logging
from time import time
from functools import wraps

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting (global variable)
request_counts = {}
RATE_LIMIT = 5  # Allow 5 requests per minute per IP
TIME_FRAME = 60  # in seconds

# Initialize Groq client
try:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    raise

def get_bot_response(user_input: str) -> str:
    """
    Get response from Groq API
    """
    try:
        if not user_input.strip():
            return "Please provide a valid input."
        
        prompt = f"""User asks: {user_input}
        Provide brief, practical information on relevant job opportunities, 
        training, and schemes."""
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=500  # Prevent overly long responses
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error in get_bot_response: {e}")
        return "An error occurred while processing your request. Please try again."

# Rate limiting decorator
def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time()
        
        # Check if this IP has made any request
        if client_ip in request_counts:
            request_times = request_counts[client_ip]
            # Remove requests older than TIME_FRAME seconds
            request_counts[client_ip] = [timestamp for timestamp in request_times if current_time - timestamp < TIME_FRAME]
        
        # Allow request if less than RATE_LIMIT requests in the last TIME_FRAME seconds
        if len(request_counts.get(client_ip, [])) >= RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({"error": "Too many requests. Please try again later."}), 429  # 429 Too Many Requests
        
        # Log the request time for the client IP
        if client_ip not in request_counts:
            request_counts[client_ip] = []
        request_counts[client_ip].append(current_time)
        
        return f(*args, **kwargs)
    return decorated_function
