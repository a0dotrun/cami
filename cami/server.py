import asyncio
import json
import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from pydantic import BaseModel

from cami.agents.root import agent
from cami.config import (
    APP_NAME,
)
from cami.services import red
from cami.utils.logger import logger
from cami.workers.background import agent_runner_background

# --- Basic Configuration --- #
warnings.filterwarnings("ignore")

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


async def get_current_user_id():
    """Placeholder for a real authentication dependency."""
    return USER_ID


@app.get("/")
def index():
    return {
        "status": "ok",
        "timestamp": datetime.now(datetime.UTC).isoformat(),
    }


@app.get("/api/v1/threads/{thread_id}/responses/stream")
async def stream_responses(
    request: Request,
    thread_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Streams agent responses for a given thread using Redis Pub/Sub and Server-Sent Events (SSE).
    """
    response_channel = f"agent:responses:{user_id}:{thread_id}"

    async def response_stream_generator():
        logger.info(f"Starting stream for channel: {response_channel}")
        pubsub = None
        try:
            # 1. Create a Pub/Sub object and subscribe
            pubsub = await red.create_pubsub()
            await pubsub.subscribe(response_channel)

            # 2. Use a simple, idiomatic loop to listen for messages
            async for message in pubsub.listen():
                print("message:", message)
                # Check if client has disconnected
                if await request.is_disconnected():
                    logger.warning(
                        f"Client disconnected from stream for thread {thread_id}."
                    )
                    break

                # 3. Process valid messages, ignoring subscribe confirmations
                if message and message["type"] == "message":
                    data = message["data"]
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")

                    # 4. Yield the data directly in SSE format
                    # The data from pub/sub IS the response, no need for another fetch.
                    logger.debug(f"Streaming data for {thread_id}: {data}")
                    yield f"data: {data}\n\n"

        except asyncio.CancelledError:
            logger.info(
                f"Stream cancelled for thread {thread_id}. Client likely disconnected."
            )
        except Exception as e:
            logger.error(f"Error in stream for thread {thread_id}: {e}", exc_info=True)
            error_payload = json.dumps(
                {"type": "error", "message": "An unexpected error occurred."}
            )
            yield f"data: {error_payload}\n\n"
        finally:
            # 5. Clean up the subscription
            if pubsub:
                await pubsub.unsubscribe(response_channel)
                await pubsub.close()
            logger.info(f"Stream closed for channel: {response_channel}")

    return StreamingResponse(
        response_stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def stream_agent_run(
    user_id: str, session_id: str, query: str
) -> AsyncGenerator[str]:
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


@app.post("/api/v1/threads/{thread_id}/run")
async def run_thread(thread_id: str, body: ThreadMessageRequest = Body(...)):
    logger.info(f"received request for user_id: {USER_ID}, session_id: {thread_id}")
    logger.info(f"message: {body.message}")
    try:
        current_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=thread_id,
        )
        if not current_session:
            logger.info("session does not exist, creating new session")
            current_session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=thread_id,
            )
            logger.info(f"session created with id: {current_session.id}")
    except Exception as e:
        logger.error(f"error getting or creating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="error getting or creating session"
        ) from e

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
    session_id = "1"
    key = f"agent:run_state:{user_id}:{session_id}"

    curr_agent_run_state = await red.get(key, None)
    logger.info(f"got agent run state: {curr_agent_run_state}")
    if curr_agent_run_state:
        if curr_agent_run_state == "running":
            return Response(status_code=204)

    agent_runner_background.send(APP_NAME, USER_ID, session_id)
    await red.set(key, "running", red.REDIS_KEY_TTL)

    return "ok"
