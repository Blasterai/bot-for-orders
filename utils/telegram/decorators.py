from functools import wraps


from utils.telegram import send_message
from loguru import logger

from utils.telegram.bot_basics import alert_admin


def catch_exceptions(func):
    @wraps(func)
    def wrapper(bot, update, *args, **kwargs):
        try:
            return func(bot, update, *args, **kwargs)
        except Exception as e:
            from utils import ui_msg

            logger.exception(str(e))
            alert_admin(bot, f"Unhandled exception in {func.__name__}:\n\n{e} ")
            send_message(
                bot, update.effective_user.id, ui_msg.GENERAL.UNHANDLED_EXCEPTION
            )
            return -1

    return wrapper
