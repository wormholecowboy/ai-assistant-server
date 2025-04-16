from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import necessary components from orchestrator
from orchestrator import primary_agent, start_mcp_servers, stop_mcp_servers

load_dotenv()
# Remove GEMINI specific setup
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# gemini_client = genai.Client(api_key=GEMINI_API_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the MCP servers
    print("Application startup: Initializing MCP servers...")
    await start_mcp_servers()
    yield
    # Shutdown: Stop the MCP servers
    print("Application shutdown: Cleaning up MCP servers...")
    await stop_mcp_servers()

app = FastAPI(lifespan=lifespan) # Apply the lifespan manager

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    # Add other origins if needed
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

# Define a response model for clarity (optional but good practice)
class Answer(BaseModel):
    response: str | dict # Agent might return string or dict

@app.post("/ask", response_model=Answer)
async def ask(question: Question):
    """
    Receives a question and routes it to the primary orchestration agent.
    """
    if not question.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        print(f"Received request for primary agent: {question.message}")
        # Use primary_agent.run() for a single response
        # If you needed streaming, you'd use primary_agent.run_stream()
        # and return a StreamingResponse from FastAPI
        result = await primary_agent.run(question.message)

        # The agent's run method returns a RunResult object.
        # The final answer is typically in result.data
        print(f"Primary agent response: {result.data}")

        # Ensure the response data is suitable for the Answer model
        response_data = result.data if result.data is not None else "Agent did not return data."

        # If the agent returns a dict (e.g., from a tool call),
        # ensure it's handled correctly. For now, we wrap it.
        # You might want more specific handling based on expected agent output.
        if isinstance(response_data, dict):
             return Answer(response=response_data)
        else:
             return Answer(response=str(response_data))


    except Exception as e:
        print(f"Error processing request with primary agent: {e}")
        # Consider more specific error handling based on potential agent errors
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")

# Keep the root endpoint or modify/remove as needed
# It currently uses Gemini, which we removed. Let's make it a simple health check.
@app.get("/")
async def root():
    """
    Simple health check endpoint.
    """
    return {"message": "Orchestration API is running"}

# Note: If you run this with uvicorn, use --reload carefully during development,
# as the MCP server processes might not restart cleanly every time.
# Example: uvicorn server:app --host 0.0.0.0 --port 8000
