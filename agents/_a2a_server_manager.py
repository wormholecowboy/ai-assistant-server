from contextlib import AsyncExitStack

from .supabase_a2a_server import supabase_a2a_main

agent_stack = AsyncExitStack()

async def start_all_a2a_servers():
    try:
        await agent_stack.enter_async_context(supabase_a2a_main())
    except Exception as e:
        print(f"Error starting agent A2A servers: {e}")
        print("Continuing without agent A2A servers...")
        

async def stop_all_a2a_servers():
    try:
        await agent_stack.aclose()
    except Exception as e:
        print(f"Error stopping agent A2A servers: {e}")
        print("Continuing without stopping agent A2A servers...")
