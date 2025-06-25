from .logger import logger
from functools import wraps


def tool_error_handler(error_msg):
    def outer_fn(fn):

        @wraps(fn)
        def inner_fn(*args, **kwargs):
            try:
                logger.info(f"Calling original fn: {fn} with args: {args}, {kwargs}")
                return fn(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing function {fn}: {e!s}")
                return error(error_msg)
        return inner_fn

    logger.info("setup tool with error: {}".format(error_msg))
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
