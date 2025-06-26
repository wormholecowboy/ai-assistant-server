import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    LLM_API_KEY = os.getenv('LLM_API_KEY')
    
    # App Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Constants
    TRANSCRIPT_CHUNK_SIZE_TOKENS = 4000
    TRANSCRIPT_CHUNK_OVERLAP_TOKENS = 200
    NUM_IDEAS_TO_EXTRACT_PER_VIDEO = 5
