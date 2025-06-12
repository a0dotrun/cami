import asyncio
import json
import warnings
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from cami.config import (
    APP_NAME,
    USER_ID,
)
from cami.infra import red, session
from cami.utils.logger import logger
from cami.workers.background import agent_runner_background

warnings.filterwarnings("ignore")


class ThreadMessageRequest(BaseModel):
    message: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("starting up FASTAPI app")
    try:
        try:
            await red.initialize_async()
            await session.initialize_async()
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


@app.post("/api/v1/threads")
async def create_thread(user_id: str = Depends(get_current_user_id)):
    service = await session.service()
    sess = await service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
    )
    return {"thread_id": sess.id}


@app.get("/api/v1/threads/{thread_id}")
async def get_thread(thread_id: str, user_id: str = Depends(get_current_user_id)):
    service = await session.service()
    sess = await service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=thread_id
    )
    if not session:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"thread_id": sess.id}


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


@app.post("/api/v1/threads/{thread_id}/run")
async def run_thread(
    thread_id: str,
    user_id: str = Depends(get_current_user_id),
    body: ThreadMessageRequest = Body(...),
):
    logger.info(f"received request for user_id: {USER_ID}, session_id: {thread_id}")
    logger.info(f"message: {body.message}")
    run_state_key = f"agent:run_state:{user_id}:{thread_id}"
    try:
        service = await session.service()
        current_session = await service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=thread_id,
        )
        if not current_session:
            logger.info("session does not exist, creating new session")
            current_session = await service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=thread_id,
            )
            logger.info(f"session created with id: {current_session.id}")
        agent_runner_background.send(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=thread_id,
            message=body.message,
        )
        await red.set(run_state_key, "running", red.REDIS_KEY_TTL)
    except Exception as e:
        logger.error(f"error getting or creating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="error getting or creating session"
        ) from e

    return Response(status_code=204)
