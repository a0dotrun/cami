from .logger import logger


def tool_error_handler(error_msg):
    def outer_fn(fn):
        def inner_fn(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing function {fn}: {e!s}")
                return {
                    "status": "error",
                    "result": error_msg,
                }
        return inner_fn
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
