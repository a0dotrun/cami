import asyncio
import json
import warnings
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.responses import StreamingResponse
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from pydantic import BaseModel
from cami.workers.background import agent_runner_background
from cami.agents.root import agent
from cami.config import (
    APP_NAME,
)
from cami.services import red
from cami.workers.background import count_words

# --- Basic Configuration --- #
warnings.filterwarnings("ignore")
from cami.utils.logger import logger

USER_ID = "sanchitrk"


class ThreadMessageRequest(BaseModel):
    message: str


session_service = DatabaseSessionService(
    db_url="postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
    echo=True,
)

runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("starting up FASTAPI app")
    try:
        try:
            await red.initialize_async()
            logger.info("redis connection initialized successfully")
        except Exception as e:
            logger.error(f"redis initialization failed: {e}", exc_info=True)
            raise e
        yield
        try:
            logger.info("closing redis connection")
        except Exception as e:
            logger.error(f"closing redis connection failed: {e}", exc_info=True)
        logger.info("shutting down FASTAPI app")
    except Exception as e:
        logger.error(f"failed to start FASTAPI app:{e}", exc_info=True)
        raise


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def stream_agent_run(
        user_id: str, session_id: str, query: str
) -> AsyncGenerator[str, None]:
    logger.info(f"running agent with user_id: {user_id}, session_id: {session_id}")
    logger.info(f"query: {query}")

    content = types.Content(role="user", parts=[types.Part(text=query)])

    try:
        async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content
        ):
            if event.error_message is not None:
                response = {
                    "status": "error",
                    "error_message": event.error_message,
                }
                yield f"data: {json.dumps(response)}\n\n"
            elif event.content and event.content.parts:
                text_parts = [
                    getattr(part, "text", "")
                    for part in event.content.parts
                    if hasattr(part, "text")
                ]
                response = {"status": "ok", "text": " ".join(filter(None, text_parts))}
                yield f"data: {json.dumps(response)}\n\n"
            await asyncio.sleep(0.01)
    except Exception as e:
        logger.error(
            f"error during agent execution or event streaming: {e}", exc_info=True
        )
        error_event_data = {"status": "error", "error_message": str(e)}
        yield f"data: {json.dumps(error_event_data)}\n\n"


@app.post("/api/v1/threads/{thread_id}/messages/stream")
async def thread_messages(thread_id: str, body: ThreadMessageRequest = Body(...)):
    logger.info(f"received request for user_id: {USER_ID}, session_id: {thread_id}")
    logger.info(f"message: {body.message}")
    try:
        current_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=thread_id,
        )
        if not current_session:
            logger.info(f"session does not exist, creating new session")
            current_session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=thread_id,
            )
            logger.info(f"session created with id: {current_session.id}")
    except Exception as e:
        logger.error(f"error getting or creating session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="error getting or creating session")

    return StreamingResponse(
        stream_agent_run(user_id=USER_ID, session_id=thread_id, query=body.message),
        status_code=200,
        media_type="text/event-stream",
    )


class TestURL(BaseModel):
    url: str


@app.post("/api/v1/test")
async def test(body: TestURL = Body(...)):
    logger.info("got test request!!")
    user_id = USER_ID
    session_id = '1'
    key = f"agent:run_state:{user_id}:{session_id}"

    curr_agent_run_state = await red.get(key, None)
    logger.info(f"got agent run state: {curr_agent_run_state}")
    if curr_agent_run_state:
        if curr_agent_run_state == 'pending':
            return Response(status_code=204)

    agent_runner_background.send(APP_NAME, USER_ID, session_id)
    await red.set(key, 'pending', red.REDIS_KEY_TTL)

    return 'ok'
