import json
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def analyze_election_data(state, district, ward):
    """
    Analyze election data using Groq API and ensure proper JSON formatting
    """
    prompt = f"""
    Please analyze the municipal corporation election data and provide a detailed JSON response for:
    State: {state}
    District: {district}
    Ward: {ward}

    Return the data in the following JSON structure:
    {{
        "election_status": "string describing current election status",
        "last_election_date": "YYYY-MM-DD",
        "results": {{
            "winning_party": "string",
            "winner_name": "string",
            "vote_share": "percentage",
            "total_votes": "number"
        }},
        "performance_metrics": {{
            "development_projects": ["list of projects"],
            "budget_utilization": "percentage",
            "citizen_satisfaction": "rating"
        }},
        "key_issues": ["list of key issues"],
        "voter_data": {{
            "total_registered": "number",
            "turnout_percentage": "number",
            "demographic_split": {{
                "male": "percentage",
                "female": "percentage",
                "other": "percentage"
            }}
        }}
    }}
    
    Ensure all data is properly formatted as a valid JSON object.
    """

    try:
        # Make API call to Groq
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=2000
        )

        # Extract and parse response
        response_content = chat_completion.choices[0].message.content
        
        # Try to find JSON content within the response
        try:
            json_response = json.loads(response_content)
        except json.JSONDecodeError:
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_content[start_idx:end_idx]
                try:
                    json_response = json.loads(json_str)
                except json.JSONDecodeError:
                    raise ValueError("Could not parse JSON from response")
            else:
                raise ValueError("No JSON content found in response")

        # Ensure all required fields exist
        required_fields = {
            "election_status": "Status information unavailable",
            "last_election_date": None,
            "results": {
                "winning_party": "Not available",
                "winner_name": "Not available",
                "vote_share": "0",
                "total_votes": "0"
            },
            "performance_metrics": {
                "development_projects": [],
                "budget_utilization": "0",
                "citizen_satisfaction": "N/A"
            },
            "key_issues": [],
            "voter_data": {
                "total_registered": "0",
                "turnout_percentage": "0",
                "demographic_split": {
                    "male": "0",
                    "female": "0",
                    "other": "0"
                }
            }
        }

        # Validate all required fields
        for key, default_value in required_fields.items():
            if key not in json_response:
                json_response[key] = default_value

        return json_response

    except Exception as e:
        # Return structured error response
        return {
            "error": str(e),
            "election_status": "Error fetching data",
            "last_election_date": None,
            "results": None,
            "performance_metrics": None,
            "key_issues": [],
            "voter_data": None
        }
