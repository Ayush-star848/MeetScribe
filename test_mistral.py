import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY was not loaded from .env")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.3,
)

try:
    response = llm.invoke("Reply with only the word Hello")
    print("Gemini response:", response.content)

except Exception as e:
    print("Gemini test failed")
    print(type(e).__name__)
    print(str(e))
