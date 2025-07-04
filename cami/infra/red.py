import asyncio
import os
from typing import TYPE_CHECKING

import redis.asyncio as redis
from dotenv import load_dotenv

from cami.utils.logger import logger

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from redis.asyncio.client import PubSub
else:
    from redis.asyncio import Redis

# Redis client
client: Redis | None = None
_initialized: bool = False
_init_lock: asyncio.Lock = asyncio.Lock()

# Constants
REDIS_KEY_TTL = 3600 * 24  # 24 hour TTL as safety mechanism


def initialize() -> Redis:
    """Initialize Redis connection using environment variables."""
    global client

    # Load environment variables if not already loaded
    load_dotenv()

    # Get Redis configuration
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_password = os.getenv("REDIS_PASSWORD", "")
    # Convert string 'True'/'False' to boolean
    redis_ssl_str = os.getenv("REDIS_SSL", "False")
    redis_ssl = redis_ssl_str.lower() == "true"

    logger.info(f"Initializing Redis connection to {redis_host}:{redis_port}")

    # Create Redis client with basic configuration
    client = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=0,
        password=redis_password if redis_password else None,
        ssl=redis_ssl,
        decode_responses=True,
        socket_timeout=5.0,
        socket_connect_timeout=5.0,
        retry_on_timeout=True,
        health_check_interval=30,
    )

    return client


async def initialize_async() -> Redis:
    """Initialize Redis connection asynchronously."""
    global client, _initialized

    async with _init_lock:
        if not _initialized:
            logger.info("Initializing Redis connection")
            initialize()

            try:
                await client.ping()
                logger.info("Successfully connected to Redis")
                _initialized = True
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                client = None
                raise

    return client


async def close() -> None:
    """Close Redis connection."""
    global client, _initialized
    if client:
        logger.info("Closing Redis connection")
        await client.aclose()
        client = None
        _initialized = False
        logger.info("Redis connection closed")


async def get_client() -> Redis:
    """Get the Redis client, initializing if necessary."""
    global client, _initialized
    if client is None or not _initialized:
        await initialize_async()
    return client


# Basic Redis operations
async def set(
    key: str, value: str | bytes | int | float, ex: None | int = None
) -> bool:
    """Set a Redis key."""
    redis_client = await get_client()
    return await redis_client.set(key, value, ex=ex)


async def get(key: str, default: str | None = None) -> str | None:
    """Get a Redis key."""
    redis_client = await get_client()
    result = await redis_client.get(key)
    return result if result is not None else default


async def delete(key: str) -> int:
    """Delete a Redis key."""
    redis_client = await get_client()
    return await redis_client.delete(key)


async def publish(channel: str, message: str) -> int:
    """Publish a message to a Redis channel."""
    redis_client = await get_client()
    return await redis_client.publish(channel, message)


async def create_pubsub() -> "PubSub":
    """Create a Redis pubsub object."""
    redis_client = await get_client()
    return redis_client.pubsub()


# List operations
async def rpush(key: str, *values: str | bytes | int | float) -> int:
    """Append one or more values to a list."""
    redis_client = await get_client()
    return await redis_client.rpush(key, *values)


async def lrange(key: str, start: int, end: int) -> list[str]:
    """Get a range of elements from a list."""
    redis_client = await get_client()
    return await redis_client.lrange(key, start, end)


async def llen(key: str) -> int:
    """Get the length of a list."""
    redis_client = await get_client()
    return await redis_client.llen(key)


# Key management
async def expire(key: str, time: int) -> bool:
    """Set a key's time to live in seconds."""
    redis_client = await get_client()
    return await redis_client.expire(key, time)


async def keys(pattern: str) -> list[str]:
    """Get keys matching a pattern."""
    redis_client = await get_client()
    return await redis_client.keys(pattern)
