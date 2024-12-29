import json
import groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Initialize the Groq client with the API key from the environment variable
groq_client = groq.Client(api_key=GROQ_API_KEY)

class IndianElectionAnalyzer:
    def __init__(self):
        self.election_levels = {
            'regional': 'Assembly/Municipal',
            'state': 'State Legislative',
            'national': 'Lok Sabha'
        }
        
        self.default_sectors = {
            'women_empowerment': [
                'Education initiatives',
                'Economic opportunities',
                'Healthcare access',
                'Political representation',
                'Safety and security'
            ],
            'economic_development': [
                'Job creation',
                'Infrastructure development',
                'Industry growth',
                'Rural development',
                'Urban planning'
            ],
            'social_welfare': [
                'Healthcare systems',
                'Education quality',
                'Social security',
                'Minority welfare',
                'Poverty alleviation'
            ]
        }
    
    def analyze_candidate(self, candidate_info, sector):
        """
        Analyze candidate based on election level and chosen sector
        """
        prompt = f"""
        Analyze the following Indian election candidate for {candidate_info['election_level']} election:
        
        Candidate Name: {candidate_info['name']}
        Constituency/Region: {candidate_info['constituency']}
        Party: {candidate_info['party']}
        
        Please provide a detailed analysis for the sector: {sector}
        
        Analysis should include:
        1. Past track record in this sector
        2. Current initiatives and promises
        3. Quantitative metrics where available
        4. Comparison with standard benchmarks
        5. Areas of strength and improvement
        
        Format the response as JSON with this structure:
        {{
            "summary": "Overall analysis summary",
            "track_record": {{
                "initiatives": [],
                "impact_metrics": [],
                "key_achievements": []
            }},
            "current_agenda": {{
                "promises": [],
                "proposed_programs": [],
                "budget_allocations": []
            }},
            "performance_scores": {{
                "policy_strength": number,
                "implementation": number,
                "innovation": number,
                "community_impact": number,
                "sustainability": number
            }},
            "recommendations": []
        }}
        """
        
        # Make the API call to Groq with the constructed prompt
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.3,
        )
        
        # Parse and return the response from Groq API
        return json.loads(response.choices[0].message.content)

    def compare_candidates(self, candidates, sector):
        """
        Compare multiple candidates based on sector
        """
        analysis_results = {}
        for candidate in candidates:
            analysis_results[candidate['name']] = self.analyze_candidate(candidate, sector)
        return analysis_results
