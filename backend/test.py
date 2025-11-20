from dotenv import load_dotenv
from google import genai
import os

load_dotenv()   # loads .env file

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("API key NOT LOADED")
else:
    print("API key loaded successfully!")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?"
)

print(response.text)
