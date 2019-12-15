import logging
import os
from functools import wraps

try:
    from telegram import Bot, TelegramError
except ModuleNotFoundError:
    pass


def bot_report_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not os.environ.get("BOT_TOKEN_REPORTER"):
            raise KeyError(
                'No bot token in os environment variables under "BOT_TOKEN_REPORTER"'
            )
        if not os.environ.get("REPORT_TO_TELEGRAM_ID"):
            raise KeyError(
                'No telegram id to report to in os environment variables under "REPORT_TO_TELEGRAM_ID"'
            )

        reporter_bot = Bot(os.environ["BOT_TOKEN_REPORTER"])
        report_to_telegram_id = os.environ["REPORT_TO_TELEGRAM_ID"]
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_message = f"Error in: {func.__name__} [{func.__module__}]\n{e}"
            try:
                reporter_bot.send_message(report_to_telegram_id, log_message)
            except TelegramError as e:
                logging.critical(
                    f"Failed to send message to {report_to_telegram_id}: {e}"
                )
            raise

    return wrapper
