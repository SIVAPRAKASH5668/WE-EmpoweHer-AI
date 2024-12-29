# app/services/women_schemes_bot.py

from groq import Groq
import os

class WomenSchemesBot:
    def __init__(self, api_key):
        """Initialize the bot with an API key."""
        self.client = Groq(api_key=api_key)

    def generate_search_prompt(self, user_details):
        """Generate a detailed search prompt based on user details."""
        prompt = f"""
        Find relevant government schemes for women in India with the following profile:
        - Age: {user_details['age']} years
        - State: {user_details['state']}
        - Annual Income: ₹{user_details['annual_income']}
        - Marital Status: {user_details['marital_status']}
        - Education: {user_details['education']}
        - Employment Status: {user_details['occupation']}

        Please provide:
        1. Names of applicable schemes (National, State, and Regional level)
        2. Eligibility criteria for each scheme
        3. Benefits provided
        4. Application process
        """
        return prompt

    def search_schemes(self, prompt):
        """Search for schemes using Groq API."""
        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert on government schemes for women in India. Provide accurate and up-to-date information about schemes, their eligibility criteria, and benefits."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.1,
                max_tokens=2000
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error occurred while searching schemes: {str(e)}"
