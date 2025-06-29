from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    FilePart,
    FileWithBytes,
    InvalidParamsError,
    Part,
    Task,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    completed_task,
    new_agent_text_message,
    new_artifact,
)
from a2a.utils.errors import ServerError
from supabase_agent import SupabaseAgent

class SupbaseAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = SupabaseAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        query = context.get_user_input()
        try:
            result = self.agent.invoke(query)
            print(f'Final Result ===> {result}')
        except Exception as e:
            print('Error invoking agent: %s', e)
            raise ServerError(
                error=ValueError(f'Error invoking agent: {e}')
            ) from e

        await event_queue.enqueue_event(
            completed_task(
                context.task_id,
                context.context_id,
                new_agent_text_message(result),
                [context.message],
            )
        )

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
