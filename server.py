from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
app = FastAPI()

@app.get("/")
async def root():
    contents = "This is just an api test. Say hello in any language you like!"
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash", contents=contents
    )
    print(response.text)

    return {"message": response.text}
