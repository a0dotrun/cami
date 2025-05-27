import restate
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from pydantic import BaseModel

from cami.agents import agent
from cami.config import APP_NAME, DATABASE_PASSWORD, DATABASE_URL
from cami.utils.types import ChatEntry


class Response(BaseModel):
    status: str


session_service = DatabaseSessionService(
    db_url=f"postgresql://postgres:{DATABASE_PASSWORD}@{DATABASE_URL}/postgres",
    echo=False,
)

chat = restate.VirtualObject("agent")

# fixme: should come from auth layer.
USER_ID = "sanchitrk"


@chat.handler("message")
async def on_message(ctx: restate.ObjectContext, message: ChatEntry) -> Response:
    print(f"-> ctx.key(): {ctx.key()}")
    print(f"-> role: {message.role} content: {message.content}")

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=ctx.key(),
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=ctx.key(),
        )

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    content = types.Content(role="user", parts=[types.Part(text=message.content)])
    async for event in runner.run_async(
        user_id=USER_ID,
        new_message=content,
        session_id=ctx.key(),
    ):
        print(
            f"Start of Event ---------"
            f"Author: {event.author} "
            f"Type: {type(event).__name__} "
            f"Final: {event.is_final_response()}, Content: {event.content}"
            f"End of Event ---------"
        )
        if event.is_final_response():
            if event.content and event.content.parts:
                final_reponse_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate and event.error_message:
                final_reponse_text = f"Escalated with message: {event.error_message}"
            elif event.actions and event.actions.escalate:
                final_reponse_text = "Escalated without message"
            break
    print(f"Agent: {final_reponse_text}")

    return Response(status="ok")
