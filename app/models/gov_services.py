# gov_services.py

import groq
import os
import json
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Initialize Groq client
client = groq.Client(api_key=GROQ_API_KEY)

def get_services(district, location_type, location_name):
    prompt = f"""Return a JSON array of government services in {location_name} {location_type}, {district} District.
    Each service object should have exactly these fields:
    {{
        "name": "Service Name",
        "type": "Service Type",
        "location": "Exact Address",
        "timing": "Operating Hours",
        "contact": "Contact Details",
        "documents": "Required Documents"
    }}
    Include  relevant state government services."""
    
    try:
        # Make the request to Groq's API
        response = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=2000
        )
        
        # Print the raw response for debugging
        content = response.choices[0].message.content.strip()
        print("Raw API Response:", content)  # Debug print
        
        # Try to parse the response content as JSON
        services = json.loads(content)
        
        # Ensure the result is a list, even if only one service is returned
        if isinstance(services, dict):
            services = [services]
        
        return services

    except json.JSONDecodeError:
        print("JSON Decode Error:", content)  # Debugging output for error
        return {"error": "Invalid response format"}
    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}
