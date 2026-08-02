from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(override=True)

# Access API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
#anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
google_api_key = os.getenv("GEMINI_API_KEY")

# Example: print to verify loading (remove in production)
print("API keys loaded from .env")
print(f"OpenAI API Key: {openai_api_key}")
print(f"Google API Key: {google_api_key}")