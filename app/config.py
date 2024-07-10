import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    REDIS_HOST=os.environ.get('REDIS_HOST')
    REDIS_PORT=os.environ.get('REDIS_PORT')
    OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY=os.environ.get('ANTHROPIC_API_KEY')
