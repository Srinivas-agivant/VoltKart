"""Configuration module for VoltKart application.

Loads environment variables using python-dotenv and provides application constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")

# MongoDB Settings
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME") or os.getenv("MONGODB_DATABASE", "voltkart_db")

# Google Gemini Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Application Settings
STORE_NAME = "VoltKart"
STORE_TAGLINE = "High-Performance Laptops, Powered by Intelligent Guidance"
MAX_RECOMMENDATIONS = 3

# Collection Names
COLLECTION_PRODUCTS = "products"
COLLECTION_FAQS = "faqs"
COLLECTION_POLICIES = "store_policies"
COLLECTION_CONVERSATIONS = "conversations"
COLLECTION_MESSAGES = "messages"
COLLECTION_RECOMMENDATIONS = "recommendations"
COLLECTION_IMPORT_HISTORY = "import_history"
COLLECTION_KNOWLEDGE_BASE = "knowledge_base"

def validate_config() -> dict[str, bool]:
    """Checks the status of critical configurations."""
    return {
        "mongodb_configured": bool(MONGODB_URI),
        "gemini_configured": bool(GEMINI_API_KEY),
    }
