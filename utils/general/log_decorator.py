from decorator import decorator
from loguru import logger

# new_level = logger.level("CHYCHA", no=38, color="<yellow>", icon="🐍")


@decorator
def log_this(func, level="DEBUG", *args, **kwargs):
    logger.log(level, f"Enter {func.__name__}")
    result = func(*args, **kwargs)
    logger.log(level, f"Result: {result}")
    logger.log(level, f"Exit: {func.__name__}")
    return result
