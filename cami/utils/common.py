from .logger import logger
from functools import wraps


def tool_error_handler(error_msg):
    def outer_fn(fn):
        @wraps(fn)
        async def inner_fn(*args, **kwargs):
            try:
                logger.info(f"Calling original fn: {fn.__name__} with args: {args}, {kwargs}")
                return await fn(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing function {fn.__name__}: {e!s}")
                # Assuming 'error' is a function that returns an error object/message
                return error(error_msg)

        logger.info(f"Setup inner_fn for: {fn.__name__}")
        return inner_fn

    logger.info(f"Setting up tool error handler with message: {error_msg}")
    return outer_fn


def error(msg):
    return {
        "status": "error",
        "result": msg,
    }


def success(msg):
    return {
        "status": "success",
        "result": msg,
    }
