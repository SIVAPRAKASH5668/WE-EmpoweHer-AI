import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

class PanchayatAnalyzer:
    def __init__(self):
        self.client = None
        self._initialize_groq_client()

    def _initialize_groq_client(self):
        """Initializes the Groq API client with error handling."""
        try:
            if not GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            self.client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            print(f"Error initializing Groq client: {str(e)}")

    def clean_json_response(self, response):
        """
        Function to clean the response from Groq API, extract and return only the JSON part.
        Removes any notes or text that are not part of the actual JSON.
        """
        match = re.search(r'```json\n({.*?})\n```', response, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            try:
                json_data = json.loads(json_str)
                return json_data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                return None
        else:
            print("No valid JSON found in the response.")
            return None

    def analyze_panchayat_election(self, state, district, village):
        """Analyze panchayat election data using Groq API and extract only the JSON portion."""
        if not self.client:
            return {
                "success": False,
                "error": "Groq client not initialized",
                "data": self.create_default_response()
            }

        prompt = f"""
        Analyze the panchayat election data for:
        State: {state}
        District: {district}
        Village: {village}

        Please return ONLY a valid JSON object with the following structure. No text, no explanations, just the JSON:
        {{
            "election_status": {{
                "has_election_happened": boolean,
                "last_election_date": "YYYY-MM-DD or null",
                "next_election_date": "YYYY-MM-DD or null",
                "current_status": "string"
            }},
            "election_results": {{
                "winning_candidate": "string or null",
                "party_affiliation": "string or null",
                "margin_of_victory": "number or null",
                "voter_turnout": "number or null"
            }},
            "performance_analysis": {{
                "key_initiatives": ["list of initiatives"],
                "development_projects": ["list of projects"],
                "budget_utilization": "number or null",
                "community_satisfaction": "number or null"
            }},
            "challenges_and_issues": ["list of challenges"],
            "demographic_data": {{
                "total_population": "number",
                "eligible_voters": "number",
                "gender_ratio": "number",
                "literacy_rate": "number"
            }},
            "recommendations": ["list of recommendations"]
        }}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model="mixtral-8x7b-32768",
                temperature=0.3,
                max_tokens=2000
            )

            response_content = chat_completion.choices[0].message.content.strip()
            print(f"Raw API Response: {response_content}")

            # Clean the response and extract JSON data
            json_data = self.clean_json_response(response_content)
            
            if json_data:
                return {
                    "success": True,
                    "data": json_data
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to extract valid JSON",
                    "data": self.create_default_response()
                }

        except Exception as e:
            print(f"API error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": self.create_default_response()
            }

    def create_default_response(self):
        """Function to generate a default response in case of errors."""
        return {
            "election_status": {
                "has_election_happened": False,
                "last_election_date": None,
                "next_election_date": None,
                "current_status": "No data"
            },
            "election_results": {
                "winning_candidate": None,
                "party_affiliation": None,
                "margin_of_victory": None,
                "voter_turnout": None
            },
            "performance_analysis": {
                "key_initiatives": [],
                "development_projects": [],
                "budget_utilization": None,
                "community_satisfaction": None
            },
            "challenges_and_issues": [],
            "demographic_data": {
                "total_population": 0,
                "eligible_voters": 0,
                "gender_ratio": 0,
                "literacy_rate": 0
            },
            "recommendations": []
        }

