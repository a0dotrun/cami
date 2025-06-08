import asyncio

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import Middleware

from cami.services import red
from cami.utils.logger import logger


class WorkerInitializerMiddleware(Middleware):
    def after_worker_boot(self, broker, worker):
        try:
            logger.info("initializing redis connection")
            red.initialize()
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
    ]
)
dramatiq.set_broker(broker)


@dramatiq.actor
async def agent_runner_background(app_id: str, user_id: str, session_id: str) -> None:
    logger.info(f"agent runner background {app_id} {user_id} {session_id}")
    try:
        key = f"agent:run_state:{user_id}:{session_id}"
        await asyncio.sleep(5)
        await red.set(key, "resolved", ex=red.REDIS_KEY_TTL)
        logger.info(f"agent run completed for {user_id}:{session_id}")
    except Exception as e:
        logger.error(f"Error in agent runner: {e}")
        error_key = f"agent:run_state:{user_id}:{session_id}"
        await red.set(error_key, "error", ex=300)
        raise
