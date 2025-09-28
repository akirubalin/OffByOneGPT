from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

resp = client.models.generate_content(
    model="gemini-2.0-flash",  # you can also try "gemini-1.5-flash"
    contents="Say something silly and wrong on purpose."
)

print(resp.text)

