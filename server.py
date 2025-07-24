from pydantic import BaseModel, ConfigDict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from orchestrator import orchestrator
from agents.mcp_manager import start_mcp_servers, stop_mcp_servers
from agents._a2a_server_manager import start_all_a2a_servers, stop_all_a2a_servers

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Initializing MCP servers...")
    await start_mcp_servers()
    await start_all_a2a_servers()
    yield
    print("Application shutdown: Cleaning up MCP servers...")
    await stop_mcp_servers()
    await stop_all_a2a_servers()

app = FastAPI(lifespan=lifespan) # Apply the lifespan manager

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserQuery(BaseModel):
    message: str

class Answer(BaseModel):
    response: str | dict

@app.post("/ask", response_model=Answer)
async def ask(message: UserQuery):
    """
    Receives a question or command and routes it to the primary orchestration agent.
    """
    if not message.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        print(f"Received request for orchestrator: {message.message}")
        # Use primary_agent.run() for a single response
        # If you needed streaming, you'd use primary_agent.run_stream()
        # and return a StreamingResponse from FastAPI
        print(f"Message passed to orchestrator: {message.message}") # Added log for clarity
        result = await orchestrator.run(message.message, deps=message.message)
        print(f"Orchestrator agent response: {result}")
        response_data = result.output if result.output is not None else "Agent did not return data."

        # If the agent returns a dict (e.g., from a tool call),
        # ensure it's handled correctly. For now, we wrap it.
        # You might want more specific handling based on expected agent output.
        if isinstance(response_data, dict):
             return Answer(response=response_data)
        else:
             return Answer(response=str(response_data))

    except Exception as e:
        print(f"Error processing request with orchestrator: {e}")
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

if __name__ == "__main__":
    # Run the FastAPI app using uvicorn when the script is executed directly
    uvicorn.run(app, host="0.0.0.0", port=8000)
