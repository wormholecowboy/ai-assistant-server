from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from google import genai
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
app = FastAPI()

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Important if you're using cookies or sessions
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.) - or specify what you want
    allow_headers=["*"],  # Allows all headers - or list specific headers for better security
)

class Question(BaseModel):
    message: str

@app.post("/ask")
async def ask(message: Question) -> str:
    response = gemini_client.models.generate_content(
    model="gemini-2.0-flash", contents=message.message
    )
    print(response.text)
    return response.text

@app.get("/")
async def root():
    contents = "This is just an api test. Say hello in any language you like!"
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash", contents=contents
    )
    print(response.text)

    return {"message": response.text}
