import asyncio
import json
from uuid import uuid4

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import Middleware
from google.adk.runners import Runner
from google.genai import types

from cami.agents import root_agent
from cami.config import APP_NAME
from cami.infra import red, session
from cami.utils.logger import logger


class WorkerInitializerMiddleware(Middleware):
    def after_worker_boot(self, broker, worker):
        global session_service
        try:
            logger.info("initializing redis connection")
            red.initialize()
            session.initialize()
        except Exception as e:
            logger.error(f"failed to initialize redis connection: {e}", exc_info=True)
            raise

    def before_process_message(self, broker, message):
        """Called before processing each message to ensure Redis is connected."""
        # This ensures Redis is initialized for each message processing
        # We'll handle Redis initialization in each actor as needed
        pass


# Create middleware instance
initializer_middleware = WorkerInitializerMiddleware()

# Configure RabbitMQ broker with middleware
broker = RabbitmqBroker(
    host="localhost",
    port=5672,
    middleware=[
        dramatiq.middleware.AsyncIO(),
        initializer_middleware,
    ],
)
dramatiq.set_broker(broker)


@dramatiq.actor
async def test_runner_background(app_id: str, user_id: str, session_id: str) -> None:
    logger.info(f"agent runner background {app_id} {user_id} {session_id}")
    key = f"agent:run_state:{user_id}:{session_id}"
    response_channel = f"agent:responses:{user_id}:{session_id}"
    try:
        await asyncio.sleep(1)
        payload = {"id": str(uuid4()), "type": "message", "data": "hello, message 1"}
        payload_json = json.dumps(payload)
        await red.publish(response_channel, payload_json)

        await asyncio.sleep(1)
        payload = {"id": str(uuid4()), "type": "message", "data": "hello, message 2"}
        payload_json = json.dumps(payload)
        await red.publish(response_channel, payload_json)

        await asyncio.sleep(1)
        payload = {"id": str(uuid4()), "type": "message", "data": "hello, message 3"}
        payload_json = json.dumps(payload)
        await red.publish(response_channel, payload_json)

        await red.set(key, "idle", ex=red.REDIS_KEY_TTL)
        logger.info(f"agent run completed for {user_id}:{session_id}")
    except Exception as e:
        logger.error(f"Error in agent runner: {e}")
        await red.set(key, "aborted", ex=300)
        raise


@dramatiq.actor
async def agent_runner_background(
    app_name: str, user_id: str, session_id: str, message: str
):
    logger.info(
        f"agent runner background started for app_name={app_name} user_id={user_id} session_id={session_id}"
    )
    run_state_key = f"agent:run_state:{user_id}:{session_id}"
    response_channel = f"agent:responses:{user_id}:{session_id}"

    content = types.Content(role="user", parts=[types.Part(text=message)])
    full_response_text = ""
    try:
        service = await session.service()
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=service,
        )
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            if event.error_message and event.error_code:
                response = {
                    "id": str(uuid4()),
                    "event": "error",
                    "data": event.error_message,
                }
                await red.publish(response_channel, json.dumps(response))
            if (
                event.partial
                and event.content
                and event.content.parts
                and event.content.parts[0].text
            ):
                full_response_text += event.content.parts[0].text

            if event.is_final_response():
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    final_text = full_response_text + (
                        event.content.parts[0].text if not event.partial else ""
                    )
                    response = {
                        "id": str(uuid4()),
                        "event": "message",
                        "data": final_text,
                    }
                    await red.publish(response_channel, json.dumps(response))
                    full_response_text = ""
                    await red.set(run_state_key, "idle", ex=red.REDIS_KEY_TTL)
                elif (
                    event.actions
                    and event.actions.skip_summarization
                    and event.get_function_responses()
                ):
                    response_data = event.get_function_responses()[0].response
                    print(f"Display raw tool result: {response_data}")
                elif (
                    hasattr(event, "long_running_tool_ids")
                    and event.long_running_tool_ids
                ):
                    print("Display message: Tool is running in background...")
            else:
                # Handle other types of final responses if applicable
                print("Display: Final non-textual response or signal.")
    except Exception as e:
        logger.error(f"error during agent execution: {e}")
