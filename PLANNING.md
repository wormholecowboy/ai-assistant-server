This app is designed to take in a request from a user. The request is handled
by an orchestrator of ai sub-agents. The orchestrator decides which sub agent
the request should go to and sends it.

# ARCHITECTURE
- Uses Pydantic for data validation
- Uses Pydantic-ai for AI/LLM agent framework
- Uses NextJs for the frontend (not included in this repo)
- Sub-agents will be tools for the orchestrator to use
