import asyncio

from google.adk.sessions import DatabaseSessionService

from cami.utils.logger import logger

sess: DatabaseSessionService | None = None
_initialized: bool = False
_init_lock: asyncio.Lock = asyncio.Lock()


def initialize() -> DatabaseSessionService:
    global sess
    logger.info("Initialize DB session service")
    sess = DatabaseSessionService(
        db_url="postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
        echo=False,
    )

    return sess


async def initialize_async() -> DatabaseSessionService:
    global sess, _initialized

    async with _init_lock:
        if not _initialized:
            logger.info("Initialize DB session service")
            initialize()
            try:
                logger.info("Successfully connected to DB session service")
                _initialized = True
            except Exception as e:
                logger.error(f"Failed to create DB session service: {e}")
                sess = None
                raise

    return sess


async def service() -> DatabaseSessionService:
    global sess, _initialized
    if sess is None or not _initialized:
        await initialize_async()
    return sess
