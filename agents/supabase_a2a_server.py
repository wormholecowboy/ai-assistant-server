import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from .supabase_agent_executor import SupbaseAgentExecutor
from agent_registry import registry

class SupabaseServerContextManager:
    def __init__(self):
        self.server_instance = None
        
    async def __aenter__(self):
        create_row = AgentSkill(
            id='create_row',
            name='Create Row',
            description='creates a new row in the database',
            tags=['database', 'supabase', 'create'],
            examples=['Your new record has been created', 'Your new table has been created', 'There was an error creating the row']
        )

        agent_card = AgentCard(
            name='Supabase Agent',
            description=registry["Supabase Agent"]["description"],
            url=f'http://localhost:{registry["Supabase Agent"]["PORT"]}/',
            version='1.0.0',
            defaultInputModes=['text'],
            defaultOutputModes=['text'],
            capabilities=AgentCapabilities(streaming=False),
            skills=[create_row],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=SupbaseAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler,
        )

        config = uvicorn.Config(server.build(), host='0.0.0.0', port=registry["Supabase Agent"]["PORT"])
        self.server_instance = uvicorn.Server(config)
        
        # Start server in background
        import asyncio
        self.server_task = asyncio.create_task(self.server_instance.serve())
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.server_instance:
            self.server_instance.should_exit = True
            await self.server_instance.shutdown()
        if hasattr(self, 'server_task'):
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass

def supabase_a2a_main():
    return SupabaseServerContextManager()
