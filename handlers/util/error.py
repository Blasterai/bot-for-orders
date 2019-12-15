from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext


def error_h(update: Update, context: CallbackContext, **kwargs):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, kwargs["error"])
