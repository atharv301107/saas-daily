import os
from dotenv import load_dotenv

# Load local .env file if it exists (for local testing)
load_dotenv()

# API Keys & Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Print startup configuration details
def validate_config():
    missing = []
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")
    
    if missing:
        print(f"[WARNING] The following environment variables are missing: {', '.join(missing)}")
        print("[INFO] If running locally, make sure they are in a .env file. In GitHub Actions, ensure they are set in repository secrets.")
    else:
        print("[INFO] All configuration parameters loaded successfully.")
