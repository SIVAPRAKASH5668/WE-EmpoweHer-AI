import logging
import json
from groq import Groq

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class ConstituencyService:
    """Service class to handle constituency-related logic."""
    
    def __init__(self, api_key):
        """Initialize with Groq API Key."""
        self.client = Groq(api_key=api_key)

    def find_constituency(self, state, district, locality):
        """Find constituency information using Groq API with improved prompting."""
        if not self.client:
            return {
                "success": False,
                "error": "API client not initialized. Please check your API key."
            }

        try:
            prompt = f"""You are an expert on Indian electoral constituencies and political geography. Given the following location:

State: {state}
District: {district}
Locality: {locality}

Provide accurate constituency information based on official Election Commission of India data. Your response must be a valid JSON object with this exact structure:

{{
    "parliamentary_constituency": "the accurate Lok Sabha constituency name for this location",
    "assembly_constituency": "the accurate Vidhan Sabha constituency name for this location",
    "mp_details": {{
        "name": "current sitting MP name (2024)",
        "party": "their political party abbreviation (e.g., BJP, INC, etc.)"
    }},
    "mla_details": {{
        "name": "current sitting MLA name (2024)",
        "party": "their political party abbreviation"
    }},
    "district_info": {{
        "headquarters": "official district headquarters city/town name",
        "distance_from_hq": "approximate distance from locality to HQ in kilometers (numeric only)"
    }},
    "nearby_landmarks": [
        "3-4 actual major landmarks, tourist spots, or government offices within 10km"
    ],
    "last_updated": "2024-03-29"
}}

Example for Bangalore:
{{
    "parliamentary_constituency": "Bangalore North",
    "assembly_constituency": "Hebbal",
    "mp_details": {{
        "name": "D V Sadananda Gowda",
        "party": "BJP"
    }},
    "mla_details": {{
        "name": "Byrathi Suresh",
        "party": "INC"
    }},
    "district_info": {{
        "headquarters": "Bangalore",
        "distance_from_hq": 5
    }},
    "nearby_landmarks": [
        "Bangalore Palace",
        "Manyata Tech Park",
        "Indian Air Force Base",
        "Baptist Hospital"
    ]
}}

Return ONLY the JSON object with real, accurate data for the provided location. No additional text or explanations.
"""

            completion = self.client.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": "You are a precise constituency data provider. Always return accurate, properly formatted JSON data based on real Indian electoral information."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                model="mixtral-8x7b-32768",
                temperature=0.1,  # Reduced temperature for more consistent responses
                max_tokens=1000
            )

            response_text = completion.choices[0].message.content.strip()

            # Handle potential leading/trailing text in the response
            try:
                # Find the first '{' and last '}' to extract JSON
                start_idx = response_text.find('{')
                end_idx = response_text.rindex('}') + 1
                json_str = response_text[start_idx:end_idx]
                
                # Parse and validate JSON
                constituency_data = json.loads(json_str)
                
                # Validate required fields
                required_fields = [
                    "parliamentary_constituency", "assembly_constituency",
                    "mp_details", "mla_details", "district_info", "nearby_landmarks"
                ]
                
                for field in required_fields:
                    if field not in constituency_data:
                        raise ValueError(f"Missing required field: {field}")
                    
                if not isinstance(constituency_data["nearby_landmarks"], list):
                    raise ValueError("nearby_landmarks must be a list")
                    
                if not isinstance(constituency_data["district_info"]["distance_from_hq"], (int, float)):
                    raise ValueError("distance_from_hq must be a number")
                
                return {
                    "success": True,
                    "data": constituency_data
                }
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Invalid response format: {str(e)}")
                return {
                    "success": False,
                    "error": f"Invalid response format: {str(e)}"
                }

        except Exception as e:
            logging.error(f"API Error: {str(e)}")
            return {
                "success": False,
                "error": f"API Error: {str(e)}"
            }
