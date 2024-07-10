import logging
from functools import wraps

logger = logging.getLogger(__name__)


def log(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = await func(*args, **kwargs)
        logger.info(f"{func.__name__} returned: {result}")
        return result

    return wrapper
