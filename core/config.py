import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class AppConfig:
    """Central configuration for models, keys, and paths."""
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")
    DATA_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

    @classmethod
    def validate(cls):
        if not cls.GOOGLE_API_KEY:
            raise ValueError("Missing GOOGLE_API_KEY or GEMINI_API_KEY in environment or .env file.")
       