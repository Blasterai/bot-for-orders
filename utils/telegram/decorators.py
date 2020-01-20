import os
import traceback
from ast import literal_eval
from functools import wraps
from typing import Dict

from decorator import decorator
from loguru import logger
from telegram import Message, Update, ReplyKeyboardRemove
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from utils.telegram import send_message
from utils.telegram.bot_basics import alert_admin

env = os.environ


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


@decorator
def remove_markup(func, *args, **kwargs):
    """Removes reply markup from context.chat_data['sent'] and deletes ['sent'] key."""
    assert isinstance(args[1], CallbackContext)
    chat_data: Dict = args[1].chat_data
    if chat_data.get("sent"):
        try:
            logger.debug("Removing markup")
            sent: Message = chat_data["sent"]
            sent.edit_reply_markup(remove_markup=ReplyKeyboardRemove())
            sent.edit_reply_markup(reply_markup=None)
            del chat_data["sent"]
        except BadRequest as e:
            logger.debug(e)
    return func(*args, **kwargs)


@decorator
def clear_data(func, *args, **kwargs):
    """
    Clears context.user_data and context.chat_data on return. Decorates any handler
    with (update, context, *args, **kwargs) signature.
    """
    result = func(*args, **kwargs)
    args[1].user_data.clear()
    args[1].chat_data.clear()
    return result


@decorator
def debug_mode(func, *args, **kwargs):
    update: Update = args[0]
    msg: Message = update.effective_message

    env = os.environ
    DEBUG = bool(literal_eval(env.get("DEBUG", "0")))
    if not DEBUG:
        return msg.reply_markdown("Not in debug mode")

    return func(*args, **kwargs)


@decorator
def conversation_next(func, next_step=-1, *args, **kwargs):
    res = func(*args, **kwargs)
    if isinstance(res, Message):
        args[1].chat_data["sent"] = res
    return next_step


def send_error_notification(bot, telegram_id, e):
    traceback_info = traceback.format_exc()
    bot.send_message(telegram_id, f"{type(e).__name__}: {e}\n\n{traceback_info}")

