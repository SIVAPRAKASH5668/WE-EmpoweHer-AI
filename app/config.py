import os

class Config:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    RATE_LIMIT = 5  # requests per minute
    TIME_FRAME = 60  # in seconds
    DEBUG = True  # or False for production environment
